# Sprint 1: Basic CSV Inspection

## Problem Statement

Build a Python command-line tool to inspect CSV files.

## User Requirements

Goals for this sprint are 3-5 concise, concrete user needs:

1. The user can provide a CSV file path.
2. The tool reports the row count.
3. The project includes basic run instructions.
4. The user can see the column names in the file.
5. The tool clearly reports if the CSV file cannot be read.

## Plan

Start with a minimal command-line program that accepts one CSV path, opens the file safely, and prints a small summary. Focus on reliable file loading and simple output before adding any richer analysis.

## Tasks

- Define the command-line interface for accepting a CSV path.
- Read the CSV file and count its rows.
- Display the column names when the file has a header row.
- Handle missing files or unreadable input with a clear message.
- Add brief run instructions to the repository documentation.

## Out of Scope

- Editing or cleaning CSV data.
- Building a graphical interface.
- Advanced statistics or visualizations.
- Support for multiple file formats.

## Definition of Done

- The tool runs from the command line with a CSV file path.
- The tool prints the row count.
- The tool shows the column names when available.
- The tool handles basic file-read errors cleanly.
- The repository includes simple instructions for running the tool.
