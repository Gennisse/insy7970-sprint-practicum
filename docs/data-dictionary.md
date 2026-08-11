# Processed recipe data dictionary

Each live run writes a JSON object to `data/processed/`. Recipe API is the source of provider values; `main.py` supplies the documented transformations. JSON `null` represents missing provider values. Unknown provider fields are accepted during validation but are not automatically added to this stable processed contract.

## Top-level fields

| Field | Type | Meaning and source | Missing values / transformation |
|---|---|---|---|
| `query` | object | Exact search, ingredient, page, and page-size parameters sent by the application | Always present; API key is never included |
| `recommendation_limits` | object | User-selected `max_prep_minutes` (minutes) and `max_calories` (kilocalories per recipe) | Always present; nonnegative integers |
| `counts` | object | Returned, qualifying, and provider pagination counts | Provider pagination values may be `null` |
| `recommendations` | array of recipe objects | Recipes meeting both limits, sorted by prep minutes, calories, then name | Empty when none qualify; incomplete measurements are excluded |
| `recipes` | array of recipe objects | All normalized recipes on the returned page | Empty when the API page has no recipes |
| `links` | object | Provider pagination URLs: `first`, `last`, `prev`, `next` | Any unavailable link is `null` |
| `meta` | object | Provider `path` and `language` metadata | Either value may be `null` |

## `counts`

| Field | Type | Meaning / allowable values |
|---|---|---|
| `recipes_returned` | integer | Number of recipes in this response page; 0 or greater |
| `recommendations` | integer | Number meeting both user limits; 0 through `recipes_returned` |
| `current_page` | integer or null | Provider page number |
| `last_page` | integer or null | Provider final page number |
| `per_page` | integer or null | Provider page-size value |
| `total` | integer or null | Provider count across pages |

## Recipe object

The same fields occur in `recipes` and `recommendations`; the latter also contains `recommendation_rank`.

| Field | Type | Units / allowable values | Source and transformation / missing rule |
|---|---|---|---|
| `id` | integer, string, or null | Provider identifier | Copied from Recipe API |
| `name` | string or null | Free text | Copied from Recipe API |
| `description` | string or null | Free text | Copied from Recipe API |
| `cuisine` | string or null | Provider category | Copied without category recoding |
| `difficulty` | string or null | Provider category | Copied without category recoding |
| `meal_type` | string or null | Provider category | Copied without category recoding |
| `prep_time_minutes` | integer or null | Minutes | Copied from provider; null prevents recommendation |
| `calories` | integer or null | Kilocalories per recipe as reported by provider | Copied from provider; null prevents recommendation |
| `ingredients` | array | Up to 10 provider values | First 10 elements retained; missing/non-list becomes empty array |
| `instruction_count` | integer | Count, 0 or greater | Length of provider instructions; missing/non-list becomes 0 |
| `recommendation_rank` | integer | 1 is best | Added only to qualifying copies; prep ascending, calories ascending, name ascending |

## Provenance and files

The matching file in `data/raw/` preserves the provider response text before validation or transformation. Both filenames share a search/page/UTC timestamp stem. The processed file deliberately excludes credentials and acquisition headers. The reproducible report uses the committed provider-shaped test fixture named in the report, rather than a live request, so anyone can rebuild it without a secret.

## SQLite recommendation history

Successful CLI and dashboard runs add one row to `data/weeknight-recipe-scout.sqlite3` by default. The database never stores the API key or raw response.

| Field | SQLite type | Meaning / missing rule |
|---|---|---|
| `id` | INTEGER | Auto-incrementing local run identifier |
| `recorded_at` | TEXT | UTC-aware ISO 8601 timestamp |
| `search` | TEXT | Search term used for the run |
| `max_prep_minutes` | INTEGER | Preparation-time ceiling in minutes |
| `max_calories` | INTEGER | Calorie ceiling in kilocalories |
| `recipes_returned` | INTEGER | Recipes returned on the page |
| `recommendations` | INTEGER | Recipes meeting both limits |
| `top_name` | TEXT or NULL | First ranked recommendation; null when none qualifies |
| `top_prep_minutes` | INTEGER or NULL | Provider prep minutes for the top pick |
| `top_calories` | INTEGER or NULL | Provider calories for the top pick |
| `processed_path` | TEXT | Processed JSON supporting the history row |
