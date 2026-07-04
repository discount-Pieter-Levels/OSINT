import re
from datetime import datetime
from typing import Any, Dict, List

try:
    from dateutil import parser as _date_parser  # type: ignore
except Exception:
    _date_parser = None


_HASHTAG_RE = re.compile(r"(?:#|＃)([\w\-]+)", re.UNICODE)


def _parse_date(s: Any) -> str:
    if not s:
        return ""
    if isinstance(s, (int, float)):
        try:
            return datetime.fromtimestamp(float(s)).isoformat()
        except Exception:
            return str(s)
    s_str = str(s).strip()
    if _date_parser:
        try:
            return _date_parser.parse(s_str).isoformat()
        except Exception:
            pass
    fmts = ["%B %d, %Y", "%b %d, %Y", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%m/%d/%Y", "%d %b %Y"]
    for f in fmts:
        try:
            return datetime.strptime(s_str, f).isoformat()
        except Exception:
            continue
    return s_str


def _extract_hashtags(text: str) -> List[str]:
    if not text:
        return []
    return [f"#{m.group(1)}" for m in _HASHTAG_RE.finditer(text)]


def normalize_profile(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize a noisy profile dict into the canonical app format.

    Canonical output keys:
      - username
      - display_name
      - bio
      - captions (list[str])
      - hashtags (list[str])
      - posting_times (list[str], ISO-ish)
      - profile_image (always empty string)

    The function is defensive and tolerates many common noisy shapes.
    """
    if not isinstance(raw, dict):
        return {
            "username": "",
            "display_name": "",
            "bio": "",
            "captions": [],
            "hashtags": [],
            "posting_times": [],
            "profile_image": "",
        }

    # username / handle
    username = raw.get("username") or raw.get("handle") or raw.get("screen_name") or raw.get("user") or ""

    # display name
    display_name = raw.get("display_name") or raw.get("name") or raw.get("full_name") or ""

    # bio / description
    bio = raw.get("bio") or raw.get("description") or raw.get("about") or ""

    captions: List[str] = []
    hashtags: List[str] = []
    posting_times: List[str] = []

    # Some inputs use `posts` list of objects
    posts = raw.get("posts") or raw.get("timeline") or raw.get("tweets") or raw.get("items") or []
    if isinstance(posts, list) and posts:
        for p in posts:
            if not isinstance(p, dict):
                continue
            text = p.get("caption") or p.get("text") or p.get("message") or ""
            if text:
                captions.append(text)
                hashtags.extend(_extract_hashtags(text))
            # hashtags field inside post
            post_tags = p.get("hashtags") or p.get("tags") or []
            if isinstance(post_tags, list):
                for t in post_tags:
                    if isinstance(t, str):
                        hashtags.append(t if t.startswith("#") else f"#{t}")
            # timestamp
            ts = p.get("timestamp") or p.get("time") or p.get("created_at")
            if ts:
                posting_times.append(_parse_date(ts))

    # top-level captions array
    top_caps = raw.get("captions") or raw.get("texts") or raw.get("messages")
    if isinstance(top_caps, list):
        for c in top_caps:
            if isinstance(c, str):
                captions.append(c)
                hashtags.extend(_extract_hashtags(c))

    # top-level hashtags
    top_tags = raw.get("hashtags") or raw.get("tags")
    if isinstance(top_tags, list):
        for t in top_tags:
            if isinstance(t, str):
                hashtags.append(t if t.startswith("#") else f"#{t}")

    # posting_times top-level
    top_times = raw.get("posting_times") or raw.get("timestamps") or raw.get("dates")
    if isinstance(top_times, list):
        for t in top_times:
            posting_times.append(_parse_date(t))

    # If captions empty but there's a top-level caption-like string
    if not captions:
        possible = raw.get("caption") or raw.get("text") or raw.get("status")
        if isinstance(possible, str) and possible:
            captions.append(possible)
            hashtags.extend(_extract_hashtags(possible))

    # Ensure uniqueness and preserve order
    seen = set()
    clean_hashtags: List[str] = []
    for h in hashtags:
        if h not in seen:
            seen.add(h)
            clean_hashtags.append(h)

    # Always drop image data — the UI and model do not rely on raw images
    return {
        "username": username,
        "display_name": display_name,
        "bio": bio,
        "captions": captions,
        "hashtags": clean_hashtags,
        "posting_times": posting_times,
        "profile_image": "",
    }
