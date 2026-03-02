"""
ClaudeService: wraps the Anthropic API with extended thinking.
"""
import json
import re
import anthropic

# ─── Prompt templates ────────────────────────────────────────────────────────

SYSTEM_PROMPT = """\
You are a senior social media analyst working for Google's marketing organization.
Your role: analyse real social media comment data and surface precise, evidence-backed insights
for Product Marketing Managers.

Rules you must follow:
1. PRECISION OVER RECALL — use semantic understanding, not keyword matching.
   A comment mentioning "Android" is NOT automatically about camera quality.
2. MULTILINGUAL — handle Portuguese, Spanish, and English equally.
   Never exclude or downweight a comment because it is not in English.
3. TRANSPARENCY — capture your reasoning clearly. Explain what you included and why.
4. HONESTY — if data is thin or ambiguous, say so clearly. Never fake confidence.
5. SPECIFICITY — action items must be grounded in actual patterns from real comments.
   Never give generic advice.
6. EXCLUSION — spam, noise, irrelevant comments must be excluded from analysis.
"""

ANALYSIS_PROMPT_TEMPLATE = """\
A Product Marketing Manager has asked:

QUERY: {query}

DATASET CONTEXT:
- Total comments in database: {total_rows}
- Date range: {date_start} → {date_end}
- Platforms: {platforms}
- You are reviewing {n_candidates} pre-filtered candidate comments below.

CANDIDATE COMMENTS (JSON):
{comments_json}

────────────────────────────────────────────────
Analyse the above and return ONLY a valid JSON object — no markdown, no explanation outside JSON.
Use this exact schema:

{{
  "relevant_comment_ids": [<list of integer _id values of truly relevant comments>],
  "sentiment_breakdown": {{
    "positive_pct": <number 0-100>,
    "neutral_pct":  <number 0-100>,
    "negative_pct": <number 0-100>,
    "total_relevant": <integer>
  }},
  "sentiment_trend": [
    {{"period": "<Mon YYYY>", "positive": <n>, "neutral": <n>, "negative": <n>}}
  ],
  "platform_breakdown": [
    {{"platform": "<name>", "positive": <n>, "neutral": <n>, "negative": <n>, "total": <n>}}
  ],
  "written_summary": "<3-5 sentence plain-English synthesis of key findings>",
  "key_themes": ["<theme>", "<theme>", "<theme>"],
  "action_items": [
    {{
      "title": "<specific, concrete action title>",
      "description": "<2-3 sentences grounded in actual comment patterns>",
      "platform": "<recommended platform or 'All'>",
      "priority": "<high|medium|low>"
    }}
  ],
  "reasoning_plain": "<2-4 paragraphs: what you searched for, how you decided relevance, multilingual handling, any limitations>",
  "time_range_covered": {{"start": "<YYYY-MM-DD>", "end": "<YYYY-MM-DD>"}},
  "data_quality_note": "<null or a brief note if data is thin / incomplete>"
}}

Requirements:
- 2–4 action items, highly specific, grounded in comment evidence
- 3–6 key themes
- sentiment_trend grouped by calendar month (Mon YYYY)
- platform_breakdown only includes platforms with at least 1 relevant comment
- If fewer than 10 relevant comments found, set data_quality_note accordingly
"""

FOLLOWUP_PROMPT_TEMPLATE = """\
The PMM has a follow-up question based on the prior analysis.

ORIGINAL QUERY: {original_query}
FOLLOW-UP QUESTION: {followup_query}

PRIOR ANALYSIS SUMMARY:
- Relevant comments found: {n_relevant}
- Sentiment: {pos}% positive / {neu}% neutral / {neg}% negative
- Key themes: {themes}

ADDITIONAL CANDIDATES (JSON):
{comments_json}

Answer the follow-up question directly and concisely.
Ground your answer in the comment data.
Return ONLY valid JSON:

{{
  "answer": "<direct answer to the follow-up question, 2-5 sentences>",
  "supporting_comment_ids": [<list of _id integers>],
  "additional_insights": "<null or 1-2 sentences of additional context>",
  "reasoning_plain": "<brief explanation of how you answered this follow-up>"
}}
"""


# ─── Service ──────────────────────────────────────────────────────────────────

class ClaudeService:
    MODEL = "claude-opus-4-5"

    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    # ── Main analysis ─────────────────────────────────────────────────────────

    def analyze(self, query: str, candidates: list[dict], data_info: dict) -> dict:
        """
        Full analysis with extended thinking.
        Returns a structured result dict ready for the frontend.
        """
        comments_json = json.dumps(
            [{k: v for k, v in c.items()} for c in candidates],
            ensure_ascii=False,
            indent=None,
        )

        user_prompt = ANALYSIS_PROMPT_TEMPLATE.format(
            query=query,
            total_rows=data_info.get("total_rows", "?"),
            date_start=data_info.get("date_range", {}).get("start", "?"),
            date_end=data_info.get("date_range", {}).get("end", "?"),
            platforms=", ".join(data_info.get("platforms", [])),
            n_candidates=len(candidates),
            comments_json=comments_json,
        )

        response = self.client.messages.create(
            model=self.MODEL,
            max_tokens=16000,
            thinking={"type": "enabled", "budget_tokens": 10000},
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )

        thinking_text, response_text = _extract_blocks(response)
        parsed = _parse_json(response_text)

        # Hydrate relevant comments from the candidates list
        id_set = set(parsed.get("relevant_comment_ids", []))
        relevant_comments = [c for c in candidates if c.get("_id") in id_set]

        return {
            **parsed,
            "relevant_comments":  relevant_comments,
            "thinking":           thinking_text,
            "total_analyzed":     data_info.get("total_rows", len(candidates)),
            "candidates_reviewed": len(candidates),
            "query":              query,
        }

    # ── Follow-up ─────────────────────────────────────────────────────────────

    def follow_up(
        self,
        followup_query: str,
        candidates: list[dict],
        conversation_history: list[dict],
        current_results: dict,
    ) -> dict:
        """
        Answers a follow-up question in the context of the current analysis.
        """
        prior = current_results.get("sentiment_breakdown", {})
        themes = ", ".join(current_results.get("key_themes", []))

        comments_json = json.dumps(
            [{k: v for k, v in c.items()} for c in candidates],
            ensure_ascii=False,
            indent=None,
        )

        user_prompt = FOLLOWUP_PROMPT_TEMPLATE.format(
            original_query=current_results.get("query", ""),
            followup_query=followup_query,
            n_relevant=prior.get("total_relevant", "?"),
            pos=prior.get("positive_pct", "?"),
            neu=prior.get("neutral_pct", "?"),
            neg=prior.get("negative_pct", "?"),
            themes=themes,
            comments_json=comments_json,
        )

        # Build conversation context for the API
        messages = []
        for turn in conversation_history[-6:]:  # last 3 exchanges
            messages.append({"role": turn["role"], "content": turn["content"]})
        messages.append({"role": "user", "content": user_prompt})

        response = self.client.messages.create(
            model=self.MODEL,
            max_tokens=8000,
            thinking={"type": "enabled", "budget_tokens": 5000},
            system=SYSTEM_PROMPT,
            messages=messages,
        )

        thinking_text, response_text = _extract_blocks(response)
        parsed = _parse_json(response_text)

        # Hydrate supporting comments
        id_set = set(parsed.get("supporting_comment_ids", []))
        supporting_comments = [c for c in candidates if c.get("_id") in id_set]

        return {
            **parsed,
            "supporting_comments": supporting_comments,
            "thinking": thinking_text,
            "query": followup_query,
        }


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _extract_blocks(response) -> tuple[str, str]:
    """Return (thinking_text, response_text) from an Anthropic message."""
    thinking_text = ""
    response_text = ""
    for block in response.content:
        if block.type == "thinking":
            thinking_text = block.thinking
        elif block.type == "text":
            response_text = block.text
    return thinking_text, response_text


def _parse_json(text: str) -> dict:
    """
    Parse JSON from Claude's response, stripping markdown fences if present.
    Falls back to an error dict on failure.
    """
    # Strip markdown code fences
    clean = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.MULTILINE)
    clean = re.sub(r"```\s*$", "", clean.strip(), flags=re.MULTILINE)
    try:
        return json.loads(clean)
    except json.JSONDecodeError as exc:
        return {
            "error": f"Failed to parse AI response: {exc}",
            "raw_response": text[:500],
        }
