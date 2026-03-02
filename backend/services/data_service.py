"""
DataService: loads the CSV and provides pre-filtering helpers.
"""
import re
import pandas as pd
from typing import Optional

STOP_WORDS = {
    "what", "are", "users", "saying", "about", "the", "in", "for", "our",
    "a", "an", "and", "or", "is", "was", "were", "how", "which", "who",
    "when", "where", "do", "does", "did", "have", "has", "had", "will",
    "would", "could", "should", "may", "might", "can", "we", "they",
    "their", "this", "that", "these", "those", "on", "with", "by",
    "from", "to", "of", "at", "me", "my", "your", "its", "all", "any",
    "tell", "show", "give", "me", "get", "find", "see", "look", "think",
    "across", "between", "during", "over", "under", "been", "being",
}


class DataService:
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.df: Optional[pd.DataFrame] = None

    # ── Loading ──────────────────────────────────────────────────────────────

    def load_data(self) -> None:
        """Read CSV and parse dates. Adds an integer _id column."""
        self.df = pd.read_csv(self.csv_path)
        self.df["_id"] = range(len(self.df))
        try:
            self.df["comment_date"] = pd.to_datetime(self.df["comment_date"])
            self.df["date"] = pd.to_datetime(self.df["date"])
        except Exception:
            pass  # non-fatal — dates will be strings

    def reload_from_bytes(self, raw_bytes: bytes) -> None:
        """Replace current data with uploaded CSV bytes."""
        import io
        self.df = pd.read_csv(io.BytesIO(raw_bytes))
        self.df["_id"] = range(len(self.df))
        try:
            self.df["comment_date"] = pd.to_datetime(self.df["comment_date"])
            self.df["date"] = pd.to_datetime(self.df["date"])
        except Exception:
            pass

    # ── Info ─────────────────────────────────────────────────────────────────

    def get_info(self) -> dict:
        if self.df is None:
            return {"loaded": False, "total_rows": 0}
        try:
            date_start = str(self.df["comment_date"].min())[:10]
            date_end   = str(self.df["comment_date"].max())[:10]
        except Exception:
            date_start = date_end = "unknown"

        return {
            "loaded":    True,
            "total_rows": int(len(self.df)),
            "date_range": {"start": date_start, "end": date_end},
            "platforms":  self.df["social_network"].dropna().unique().tolist(),
            "accounts":   self.df["google_account"].dropna().unique().tolist(),
            "campaigns":  self.df["campaign_name"].dropna().unique().tolist(),
        }

    # ── Pre-filtering ─────────────────────────────────────────────────────────

    def filter_candidates(self, query: str, max_results: int = 250) -> list[dict]:
        """
        Returns a list of row dicts whose comment_text / post_caption /
        campaign_name contain at least one keyword from the query.

        Falls back to a random sample if keyword hits are too few.
        """
        if self.df is None or len(self.df) == 0:
            return []

        keywords = self._extract_keywords(query)
        mask = pd.Series([False] * len(self.df), index=self.df.index)

        for kw in keywords:
            pat = re.compile(re.escape(kw), re.IGNORECASE)
            mask |= self.df["comment_text"].str.contains(pat, na=False)
            mask |= self.df["post_caption"].str.contains(pat, na=False)
            mask |= self.df["campaign_name"].str.contains(pat, na=False)

        filtered = self.df[mask].copy()

        # If keyword matching yields too few, grab a random sample of everything
        if len(filtered) < 30:
            extra = self.df[~mask].sample(
                min(max_results - len(filtered), len(self.df) - len(filtered)),
                random_state=7,
            )
            filtered = pd.concat([filtered, extra])

        if len(filtered) > max_results:
            filtered = filtered.sample(max_results, random_state=7)

        # Convert dates to strings for JSON serialisation
        result = filtered.copy()
        for col in ("comment_date", "date"):
            if col in result.columns:
                result[col] = result[col].astype(str)

        return result.to_dict("records")

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _extract_keywords(query: str) -> list[str]:
        words = re.findall(r"[a-zA-Z\u00C0-\u024F]{3,}", query.lower())
        kws = [w for w in words if w not in STOP_WORDS]
        return kws if kws else [query.lower()[:30]]
