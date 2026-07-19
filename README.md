# INSY7970 Sprint Practicum

Repository for the practicum CSV inspector, sprint specs, data file, and submission notes.

## Run

Inspect a CSV file with the default preview size:

```bash
python main.py data/test.csv
```

Show a different number of example rows:

```bash
python main.py data/test.csv --head 3
```

Run the tests:

```bash
python -m unittest discover
```
