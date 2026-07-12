# Sprint 2: Preview Example Rows

## Problem Statement

Extend the CSV inspection tool so users can preview example rows from a file in addition to seeing the basic summary.

## User Requirements

Goals for this sprint are 3-5 concise, concrete user needs:

1. The user can choose how many example rows to show with a `--head N` option.
2. The tool shows the first N data rows in a readable format.
3. The tool keeps reporting the row count and column names from Sprint 1.
4. The tool tells the user when fewer rows are available than requested.
5. The preview keeps quoted values and commas inside fields readable.

## Plan

Add a small preview feature on top of the Sprint 1 summary. The command-line interface should accept an optional row-count argument, read the CSV once, and display a short sample without changing the basic summary behavior.

## Tasks

- Add a `--head N` command-line option.
- Reuse the existing CSV loading logic from Sprint 1.
- Display the requested number of data rows after the basic summary.
- Handle files with fewer rows than the requested preview size.
- Confirm that the preview output stays readable when values contain commas or quotes.

## Out of Scope

- Editing CSV data.
- Calculating missing-value percentages.
- Computing numeric statistics.
- Exporting a Markdown report.
- Supporting non-CSV file formats.

## Definition of Done

- The tool accepts an optional `--head N` argument.
- The tool still prints the row count and column names.
- The tool prints a readable preview of the requested number of rows.
- The tool handles short files cleanly.
- The repository documentation reflects the new behavior.
