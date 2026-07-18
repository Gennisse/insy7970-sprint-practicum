from __future__ import annotations

import argparse
import ast
import csv
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

TMDB_MOVIE_URL = "https://api.themoviedb.org/3/movie/{movie_id}"
RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")


def load_dotenv_file(path: Path = Path(".env")) -> None:
    if not path.exists():
        return

    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("export "):
            stripped = stripped.removeprefix("export ").strip()
        if "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch TMDb movie details for a MovieLens title."
    )
    parser.add_argument("--title", required=True, help="Movie title to look up")
    parser.add_argument(
        "--year",
        type=int,
        default=None,
        help="Optional release year to disambiguate titles",
    )
    parser.add_argument(
        "--movies-csv",
        default=os.getenv("MOVIELENS_MOVIES_CSV", "data/movies_metadata.csv"),
        help="Path to movies_metadata.csv",
    )
    parser.add_argument(
        "--credits-csv",
        default=os.getenv("MOVIELENS_CREDITS_CSV", "data/credits.csv"),
        help="Path to credits.csv",
    )
    parser.add_argument(
        "--keywords-csv",
        default=os.getenv("MOVIELENS_KEYWORDS_CSV", "data/keywords.csv"),
        help="Path to keywords.csv",
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("TMDB_API_KEY", ""),
        help="TMDb API key stored in .env",
    )
    parser.add_argument(
        "--language",
        default=os.getenv("TMDB_LANGUAGE", "en-US"),
        help="TMDb response language",
    )
    return parser.parse_args()


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "movie"


def safe_int(value: Any) -> int | None:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def safe_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", value.lower())).strip()


def extract_year(release_date: str | None) -> int | None:
    if not release_date:
        return None
    match = re.match(r"^(\d{4})", release_date.strip())
    if not match:
        return None
    return int(match.group(1))


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return [row for row in reader]


def parse_json_blob(raw_value: str | None) -> list[dict[str, Any]]:
    if not raw_value or not raw_value.strip():
        return []

    try:
        parsed = json.loads(raw_value)
    except json.JSONDecodeError:
        try:
            parsed = ast.literal_eval(raw_value)
        except (ValueError, SyntaxError):
            return []

    if isinstance(parsed, list):
        return [item for item in parsed if isinstance(item, dict)]
    if isinstance(parsed, dict):
        return [parsed]
    return []


def parse_named_items(raw_value: str | None) -> list[str]:
    return [str(item.get("name")) for item in parse_json_blob(raw_value) if item.get("name")]


def load_movie_sources(
    movies_csv: Path, credits_csv: Path, keywords_csv: Path
) -> tuple[list[dict[str, str]], dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    movies = read_csv_rows(movies_csv)
    credits = {row.get("id", ""): row for row in read_csv_rows(credits_csv)}
    keywords = {row.get("id", ""): row for row in read_csv_rows(keywords_csv)}
    return movies, credits, keywords


def select_movie(
    movies: list[dict[str, str]], title: str, year: int | None
) -> tuple[dict[str, str], str]:
    normalized_title = normalize_text(title)
    exact_matches: list[dict[str, str]] = []
    loose_matches: list[dict[str, str]] = []

    for row in movies:
        candidate_title = row.get("title", "")
        normalized_candidate = normalize_text(candidate_title)
        if not normalized_candidate:
            continue
        if normalized_candidate == normalized_title:
            exact_matches.append(row)
        elif normalized_title in normalized_candidate or normalized_candidate in normalized_title:
            loose_matches.append(row)

    candidates = exact_matches or loose_matches
    if year is not None:
        candidates = [row for row in candidates if extract_year(row.get("release_date")) == year]

    if not candidates:
        raise LookupError(f'Could not find a movie titled "{title}" in the MovieLens CSV.')

    candidates.sort(
        key=lambda row: (
            extract_year(row.get("release_date")) or 9999,
            normalize_text(row.get("title", "")),
        )
    )
    selected = candidates[0]
    strategy = "exact" if exact_matches else "loose"
    if year is not None:
        strategy += f"+year={year}"
    return selected, strategy


def build_tmdb_url(movie_id: str, api_key: str, language: str) -> str:
    query = urlencode({"api_key": api_key, "language": language})
    return f"{TMDB_MOVIE_URL.format(movie_id=movie_id)}?{query}"


def fetch_json(url: str) -> tuple[str, dict[str, Any]]:
    request = Request(url, headers={"User-Agent": "insy7970-sprint-practicum/1.0"})
    with urlopen(request, timeout=30) as response:
        raw_text = response.read().decode("utf-8")
    return raw_text, json.loads(raw_text)


def build_local_context(
    movie_row: dict[str, str],
    credits_row: dict[str, str] | None,
    keywords_row: dict[str, str] | None,
) -> dict[str, Any]:
    cast = parse_json_blob((credits_row or {}).get("cast"))
    crew = parse_json_blob((credits_row or {}).get("crew"))
    keyword_items = parse_json_blob((keywords_row or {}).get("keywords"))

    directors = [
        member.get("name")
        for member in crew
        if member.get("job") == "Director" and member.get("name")
    ]

    return {
        "title": movie_row.get("title"),
        "release_date": movie_row.get("release_date"),
        "release_year": extract_year(movie_row.get("release_date")),
        "tmdb_id": movie_row.get("id"),
        "imdb_id": movie_row.get("imdb_id"),
        "overview": movie_row.get("overview"),
        "tagline": movie_row.get("tagline"),
        "budget": safe_int(movie_row.get("budget")),
        "revenue": safe_int(movie_row.get("revenue")),
        "runtime": safe_float(movie_row.get("runtime")),
        "vote_average": safe_float(movie_row.get("vote_average")),
        "vote_count": safe_int(movie_row.get("vote_count")),
        "genres": parse_named_items(movie_row.get("genres")),
        "production_companies": parse_named_items(movie_row.get("production_companies")),
        "spoken_languages": parse_named_items(movie_row.get("spoken_languages")),
        "top_cast": [member.get("name") for member in cast[:5] if member.get("name")],
        "directors": directors,
        "keywords": [item.get("name") for item in keyword_items if item.get("name")],
    }


def build_processed_record(
    movie_row: dict[str, str],
    credits_row: dict[str, str] | None,
    keywords_row: dict[str, str] | None,
    tmdb_payload: dict[str, Any],
    title_query: str,
    year_query: int | None,
    match_strategy: str,
    movies_csv: Path,
    credits_csv: Path,
    keywords_csv: Path,
    raw_path: Path,
    processed_path: Path,
) -> dict[str, Any]:
    tmdb_genres = tmdb_payload.get("genres") or []
    tmdb_companies = tmdb_payload.get("production_companies") or []
    tmdb_languages = tmdb_payload.get("spoken_languages") or []

    return {
        "query": {
            "title": title_query,
            "year": year_query,
            "match_strategy": match_strategy,
        },
        "source_files": {
            "movies_csv": movies_csv.as_posix(),
            "credits_csv": credits_csv.as_posix(),
            "keywords_csv": keywords_csv.as_posix(),
        },
        "movie_lens": build_local_context(movie_row, credits_row, keywords_row),
        "tmdb": {
            "id": tmdb_payload.get("id"),
            "title": tmdb_payload.get("title"),
            "original_title": tmdb_payload.get("original_title"),
            "release_date": tmdb_payload.get("release_date"),
            "runtime": tmdb_payload.get("runtime"),
            "vote_average": tmdb_payload.get("vote_average"),
            "vote_count": tmdb_payload.get("vote_count"),
            "genres": [item.get("name") for item in tmdb_genres if isinstance(item, dict)],
            "production_companies": [
                item.get("name")
                for item in tmdb_companies
                if isinstance(item, dict)
            ],
            "spoken_languages": [
                item.get("english_name") or item.get("name")
                for item in tmdb_languages
                if isinstance(item, dict)
            ],
            "overview": tmdb_payload.get("overview"),
            "status": tmdb_payload.get("status"),
            "homepage": tmdb_payload.get("homepage"),
            "poster_path": tmdb_payload.get("poster_path"),
            "imdb_id": tmdb_payload.get("imdb_id"),
        },
        "files": {
            "raw_response": raw_path.as_posix(),
            "processed_summary": processed_path.as_posix(),
        },
    }


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def make_output_stem(title: str, year: int | None, fetched_at: datetime) -> str:
    parts = [slugify(title)]
    if year is not None:
        parts.append(str(year))
    parts.append(fetched_at.strftime("%Y%m%dT%H%M%SZ"))
    return "-".join(parts)


def print_summary(
    title_query: str,
    selected_movie: dict[str, str],
    tmdb_payload: dict[str, Any],
    raw_path: Path,
    processed_path: Path,
) -> None:
    print(f'Movie lookup: "{title_query}"')
    print(
        "Matched MovieLens row: "
        f"{selected_movie.get('title')} ({selected_movie.get('release_date', '')[:4] or 'unknown'})"
    )
    print(
        "TMDb result: "
        f"{tmdb_payload.get('title')} (id {tmdb_payload.get('id')}, runtime {tmdb_payload.get('runtime')} min)"
    )
    print(f"Raw response: {raw_path}")
    print(f"Processed summary: {processed_path}")


def run(
    title: str,
    year: int | None,
    movies_csv: Path,
    credits_csv: Path,
    keywords_csv: Path,
    api_key: str,
    language: str,
) -> int:
    if not api_key:
        raise RuntimeError(
            "TMDB_API_KEY is missing. Put it in .env or pass --api-key."
        )

    movies, credits, keywords = load_movie_sources(movies_csv, credits_csv, keywords_csv)
    selected_movie, match_strategy = select_movie(movies, title, year)
    movie_id = selected_movie.get("id")
    if not movie_id:
        raise LookupError(f'The selected movie "{selected_movie.get("title")}" has no TMDb id.')

    fetched_at = datetime.now(timezone.utc)
    url = build_tmdb_url(movie_id, api_key, language)
    raw_text, tmdb_payload = fetch_json(url)

    raw_path = RAW_DIR / f"{make_output_stem(selected_movie.get('title', title), year, fetched_at)}.tmdb.raw.json"
    processed_path = PROCESSED_DIR / f"{make_output_stem(selected_movie.get('title', title), year, fetched_at)}.tmdb.summary.json"

    credits_row = credits.get(movie_id)
    keywords_row = keywords.get(movie_id)
    summary = build_processed_record(
        selected_movie,
        credits_row,
        keywords_row,
        tmdb_payload,
        title,
        year,
        match_strategy,
        movies_csv,
        credits_csv,
        keywords_csv,
        raw_path,
        processed_path,
    )

    write_text(raw_path, raw_text)
    write_json(processed_path, summary)
    print_summary(title, selected_movie, tmdb_payload, raw_path, processed_path)
    return 0


def main() -> None:
    load_dotenv_file()
    args = parse_args()

    try:
        exit_code = run(
            title=args.title,
            year=args.year,
            movies_csv=Path(args.movies_csv),
            credits_csv=Path(args.credits_csv),
            keywords_csv=Path(args.keywords_csv),
            api_key=args.api_key,
            language=args.language,
        )
        raise SystemExit(exit_code)
    except FileNotFoundError as exc:
        print(f"Error: {exc}")
        raise SystemExit(1)
    except LookupError as exc:
        print(f"Error: {exc}")
        raise SystemExit(1)
    except HTTPError as exc:
        print(f"Error: TMDb request failed with HTTP {exc.code}: {exc.reason}")
        raise SystemExit(1)
    except URLError as exc:
        print(f"Error: TMDb request could not be reached: {exc.reason}")
        raise SystemExit(1)
    except json.JSONDecodeError as exc:
        print(f"Error: TMDb returned invalid JSON: {exc}")
        raise SystemExit(1)
    except RuntimeError as exc:
        print(f"Error: {exc}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
