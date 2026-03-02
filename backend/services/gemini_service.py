"""
GeminiService: wraps the Google Gemini API with native thinking mode.
Drop-in replacement for the previous claude_service.py.
"""
import json
import re

from google import genai
from google.genai import types

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
6. EXCLUSION — spam, noise, irrelevant comments, and gibberish must be excluded from analysis.
"""

ANALYSIS_PROMPT_TEMPLATE = """\
{system}

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
{system}

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

class GeminiService:
    MODEL = "gemini-3.1-pro-preview"

    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    # ── Main analysis ─────────────────────────────────────────────────────────

    def analyze(self, query: str, candidates: list[dict], data_info: dict) -> dict:
        """Full analysis with Gemini thinking mode."""
        comments_json = json.dumps(
            [{k: v for k, v in c.items()} for c in candidates],
            ensure_ascii=False,
        )

        prompt = ANALYSIS_PROMPT_TEMPLATE.format(
            system=SYSTEM_PROMPT,
            query=query,
            total_rows=data_info.get("total_rows", "?"),
            date_start=data_info.get("date_range", {}).get("start", "?"),
            date_end=data_info.get("date_range", {}).get("end", "?"),
            platforms=", ".join(data_info.get("platforms", [])),
            n_candidates=len(candidates),
            comments_json=comments_json,
        )

        thinking_text, response_text = self._generate(prompt, thinking_budget=10000)
        parsed = _parse_json(response_text)

        id_set = set(parsed.get("relevant_comment_ids", []))
        relevant_comments = [c for c in candidates if c.get("_id") in id_set]

        return {
            **parsed,
            "relevant_comments":   relevant_comments,
            "thinking":            thinking_text,
            "total_analyzed":      data_info.get("total_rows", len(candidates)),
            "candidates_reviewed": len(candidates),
            "query":               query,
        }

    # ── Follow-up ─────────────────────────────────────────────────────────────

    def follow_up(
        self,
        followup_query: str,
        candidates: list[dict],
        conversation_history: list[dict],
        current_results: dict,
    ) -> dict:
        """Answers a follow-up question in context of the current analysis."""
        prior = current_results.get("sentiment_breakdown", {})
        themes = ", ".join(current_results.get("key_themes", []))

        comments_json = json.dumps(
            [{k: v for k, v in c.items()} for c in candidates],
            ensure_ascii=False,
        )

        prompt = FOLLOWUP_PROMPT_TEMPLATE.format(
            system=SYSTEM_PROMPT,
            original_query=current_results.get("query", ""),
            followup_query=followup_query,
            n_relevant=prior.get("total_relevant", "?"),
            pos=prior.get("positive_pct", "?"),
            neu=prior.get("neutral_pct", "?"),
            neg=prior.get("negative_pct", "?"),
            themes=themes,
            comments_json=comments_json,
        )

        # Prepend recent conversation turns for context
        if conversation_history:
            history_text = "\n\nCONVERSATION HISTORY (most recent 3 exchanges):\n"
            for turn in conversation_history[-6:]:
                role = turn.get("role", "user").upper()
                history_text += f"{role}: {turn.get('content', '')}\n"
            prompt = history_text + "\n" + prompt

        thinking_text, response_text = self._generate(prompt, thinking_budget=5000)
        parsed = _parse_json(response_text)

        id_set = set(parsed.get("supporting_comment_ids", []))
        supporting_comments = [c for c in candidates if c.get("_id") in id_set]

        return {
            **parsed,
            "supporting_comments": supporting_comments,
            "thinking":            thinking_text,
            "query":               followup_query,
        }

    # ── Core generation ───────────────────────────────────────────────────────

    def _generate(self, prompt: str, thinking_budget: int = 8000) -> tuple[str, str]:
        """
        Call Gemini with thinking mode enabled.
        Returns (thinking_text, response_text).
        """
        response = self.client.models.generate_content(
            model=self.MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(
                    thinking_budget=thinking_budget,
                ),
                temperature=1,
            ),
        )

        thinking_parts: list[str] = []
        response_parts: list[str] = []

        for part in response.candidates[0].content.parts:
            text: str = str(part.text or "")
            if getattr(part, "thought", False):
                thinking_parts.append(text)
            else:
                response_parts.append(text)

        return "".join(thinking_parts), "".join(response_parts)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _parse_json(text: str) -> dict:
    """Parse JSON from Gemini response, stripping markdown fences if present."""
    clean = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.MULTILINE)
    clean = re.sub(r"```\s*$", "", clean.strip(), flags=re.MULTILINE)
    try:
        return json.loads(clean)
    except json.JSONDecodeError as exc:
        return {
            "error": f"Failed to parse AI response: {exc}",
            "raw_response": text[:500],
        }
