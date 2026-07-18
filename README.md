# MovieLens TMDb Starter

A small `uv` command-line project that picks a movie from the MovieLens metadata CSVs, fetches the matching TMDb movie details, and saves both the raw API response and a processed summary.

## API

- The Movie Database (TMDb) movie details API
- Docs: https://developer.themoviedb.org/reference/movie-details

## Example request

```text
https://api.themoviedb.org/3/movie/862?api_key=YOUR_TMDB_API_KEY&language=en-US
```

## What the response contains

The TMDb response includes movie details such as title, runtime, overview, genres, production companies, spoken languages, vote counts, vote averages, poster path, homepage, and IMDb ID.

## What I will build

I will extend this starter into a movie exploration tool that compares MovieLens metadata with live TMDb details and can later support richer browsing or recommendations.

## Setup

1. Copy `.env.example` to `.env`.
2. Put your TMDb API key in `TMDB_API_KEY`.
3. Place the MovieLens CSVs in `data/` or point the command at their paths.
4. Run the project with `uv run main.py --title "Toy Story" --year 1995`.

## Files written

- Raw TMDb JSON is saved under `data/raw/`.
- Processed summary JSON is saved under `data/processed/`.

## Notes

- `data/`, `.env`, and `.venv/` are ignored by Git.
- The MovieLens CSVs used here are `movies_metadata.csv`, `credits.csv`, and `keywords.csv`.
