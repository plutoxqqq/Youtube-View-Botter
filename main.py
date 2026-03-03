"""Open a user-selected YouTube video in a web browser.

This utility asks the user which YouTube video they want to open, then opens
that video (or a YouTube search page) once in the default browser.
"""

from __future__ import annotations

import re
import sys
import webbrowser
from urllib.parse import quote_plus, urlparse, parse_qs

YOUTUBE_WATCH_URL = "https://www.youtube.com/watch?v={video_id}"
YOUTUBE_SEARCH_URL = "https://www.youtube.com/results?search_query={query}"
VIDEO_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{11}$")


def extract_video_id(text: str) -> str | None:
    """Return a YouTube video ID if one can be extracted from text."""
    candidate = text.strip()
    if not candidate:
        return None

    if VIDEO_ID_PATTERN.fullmatch(candidate):
        return candidate

    if "youtube.com" in candidate or "youtu.be" in candidate:
        parsed = urlparse(candidate)

        if parsed.netloc.endswith("youtu.be"):
            path_part = parsed.path.strip("/")
            if VIDEO_ID_PATTERN.fullmatch(path_part):
                return path_part

        if parsed.netloc.endswith("youtube.com"):
            query_video_id = parse_qs(parsed.query).get("v", [""])[0]
            if VIDEO_ID_PATTERN.fullmatch(query_video_id):
                return query_video_id

            path_parts = parsed.path.strip("/").split("/")
            if len(path_parts) >= 2 and path_parts[0] in {"shorts", "embed"}:
                if VIDEO_ID_PATTERN.fullmatch(path_parts[1]):
                    return path_parts[1]

    return None


def build_destination(user_input: str) -> str:
    """Build the destination URL from a video ID, URL, or search text."""
    video_id = extract_video_id(user_input)
    if video_id:
        return YOUTUBE_WATCH_URL.format(video_id=video_id)

    return YOUTUBE_SEARCH_URL.format(query=quote_plus(user_input.strip()))


def main() -> int:
    """Prompt the user for a video and open it once in the default browser."""
    print("YouTube Video Opener")
    print("Enter a YouTube link, video ID, or video title to search for.")
    selection = input("Which YouTube video would you like to open? ").strip()

    if not selection:
        print("No video was provided. Exiting.")
        return 1

    target_url = build_destination(selection)

    opened = webbrowser.open(target_url, new=2)
    if not opened:
        print(f"Could not open your browser automatically. Open this URL manually: {target_url}")
        return 1

    print(f"Opened: {target_url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
