from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import main


class MainTests(unittest.TestCase):
    def test_build_tmdb_url(self) -> None:
        url = main.build_tmdb_url("862", "ABC123", "en-US")
        parsed = urlparse(url)
        params = parse_qs(parsed.query)

        self.assertEqual(parsed.scheme, "https")
        self.assertEqual(parsed.netloc, "api.themoviedb.org")
        self.assertEqual(parsed.path, "/3/movie/862")
        self.assertEqual(params["api_key"], ["ABC123"])
        self.assertEqual(params["language"], ["en-US"])

    def test_select_movie_prefers_exact_title_match(self) -> None:
        movies = [
            {"id": "1", "title": "Toy Story", "release_date": "1995-11-22"},
            {"id": "2", "title": "Toy Story 2", "release_date": "1999-10-30"},
        ]

        movie, strategy = main.select_movie(movies, "Toy Story", None)

        self.assertEqual(movie["id"], "1")
        self.assertEqual(strategy, "exact")

    def test_parse_json_blob_and_local_context(self) -> None:
        movie = {
            "id": "862",
            "title": "Toy Story",
            "release_date": "1995-11-22",
            "imdb_id": "tt0114709",
            "overview": "A movie about toys.",
            "tagline": "A story of toys.",
            "budget": "30000000",
            "revenue": "373554033",
            "runtime": "81",
            "vote_average": "7.9",
            "vote_count": "12000",
            "genres": '[{"id": 16, "name": "Animation"}, {"id": 35, "name": "Comedy"}]',
            "production_companies": '[{"id": 1, "name": "Pixar"}]',
            "spoken_languages": '[{"iso_639_1": "en", "name": "English"}]',
        }
        credits = {
            "cast": '[{"name": "Tom Hanks"}, {"name": "Tim Allen"}]',
            "crew": '[{"job": "Director", "name": "John Lasseter"}]',
        }
        keywords = {
            "keywords": '[{"name": "toy"}, {"name": "friendship"}]',
        }

        context = main.build_local_context(movie, credits, keywords)

        self.assertEqual(context["title"], "Toy Story")
        self.assertEqual(context["release_year"], 1995)
        self.assertEqual(context["budget"], 30000000)
        self.assertEqual(context["genres"], ["Animation", "Comedy"])
        self.assertEqual(context["top_cast"], ["Tom Hanks", "Tim Allen"])
        self.assertEqual(context["directors"], ["John Lasseter"])
        self.assertEqual(context["keywords"], ["toy", "friendship"])

    def test_build_processed_record_includes_files_and_tmdb(self) -> None:
        movie = {
            "id": "862",
            "title": "Toy Story",
            "release_date": "1995-11-22",
            "imdb_id": "tt0114709",
            "overview": "A movie about toys.",
            "tagline": "A story of toys.",
            "budget": "30000000",
            "revenue": "373554033",
            "runtime": "81",
            "vote_average": "7.9",
            "vote_count": "12000",
            "genres": '[{"id": 16, "name": "Animation"}]',
            "production_companies": '[{"id": 1, "name": "Pixar"}]',
            "spoken_languages": '[{"iso_639_1": "en", "name": "English"}]',
        }
        tmdb_payload = {
            "id": 862,
            "title": "Toy Story",
            "original_title": "Toy Story",
            "release_date": "1995-11-22",
            "runtime": 81,
            "vote_average": 7.7,
            "vote_count": 12000,
            "genres": [{"name": "Animation"}],
            "production_companies": [{"name": "Pixar"}],
            "spoken_languages": [{"english_name": "English"}],
            "overview": "A movie about toys.",
            "status": "Released",
            "homepage": "https://www.pixar.com/toy-story",
            "poster_path": "/abc.jpg",
            "imdb_id": "tt0114709",
        }
        raw_path = Path("data/raw/test.raw.json")
        processed_path = Path("data/processed/test.summary.json")

        summary = main.build_processed_record(
            movie,
            credits_row=None,
            keywords_row=None,
            tmdb_payload=tmdb_payload,
            title_query="Toy Story",
            year_query=1995,
            match_strategy="exact+year=1995",
            movies_csv=Path("data/movies_metadata.csv"),
            credits_csv=Path("data/credits.csv"),
            keywords_csv=Path("data/keywords.csv"),
            raw_path=raw_path,
            processed_path=processed_path,
        )

        self.assertEqual(summary["query"]["title"], "Toy Story")
        self.assertEqual(summary["movie_lens"]["title"], "Toy Story")
        self.assertEqual(summary["tmdb"]["title"], "Toy Story")
        self.assertEqual(summary["files"]["raw_response"], raw_path.as_posix())
        self.assertEqual(summary["source_files"]["movies_csv"], "data/movies_metadata.csv")

    def test_load_dotenv_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text("TMDB_API_KEY=ABC123\nTMDB_LANGUAGE=en-US\n")

            original_key = os.environ.get("TMDB_API_KEY")
            original_language = os.environ.get("TMDB_LANGUAGE")
            self.addCleanup(
                lambda: self._restore_env(
                    original_key=original_key, original_language=original_language
                )
            )

            os.environ.pop("TMDB_API_KEY", None)
            os.environ.pop("TMDB_LANGUAGE", None)
            main.load_dotenv_file(env_path)

            self.assertEqual(os.environ["TMDB_API_KEY"], "ABC123")
            self.assertEqual(os.environ["TMDB_LANGUAGE"], "en-US")

    @staticmethod
    def _restore_env(original_key: str | None, original_language: str | None) -> None:
        if original_key is None:
            os.environ.pop("TMDB_API_KEY", None)
        else:
            os.environ["TMDB_API_KEY"] = original_key
        if original_language is None:
            os.environ.pop("TMDB_LANGUAGE", None)
        else:
            os.environ["TMDB_LANGUAGE"] = original_language


if __name__ == "__main__":
    unittest.main()
