# Private Laws Database Dashboard (In-Progress)

> The first publicly accessible, comprehensive database of U.S. Congressional Private Laws (1789-2025)

Screenshot

Live Prototype: Link

## Overview

This project supports Professor Chris Mirasola's research at the University of Houston Law Center on private legislation and historical trends. Developed in collaboration with UH Law and UH IT, the dashboard provides students and scholars with tools to explore 45,000+ private laws, previously fragmented across various government sources, in a unified, searchable interface.

## My Contributions
### Extraction
- Unified **45,000+ private laws** from Congress.gov and GovInfo API into a single normalized dataset
- Built data pipelines to extract, clean, and standardize records spanning 236 years of legislation.
- Resolved inconsistencies across source formats (date normalization, deduplication, schema alignment)

### Dashboard Development
- Designed and built interactive Dash/Plotly dashboard to be able to visualize and dive deep into the data
- Implemented full-text search
- Created export functionality for researchers to download filtered datasets

### AI Classification Pipeline (In Progress)
- Developing OpenAI API pipeline to classify private laws by relief type and subject matter (referencing codebooks created by UH Law School)
- Validating model outputs against 1000+ manually labeled laws from UH Law students
- Iterating on prompt engineering and codebook refinement

## Current Status
| Milestone | Status | Notes |
|-----------|--------|--------|
| Data collection + cleaning | Done | Python script pulling from Congress.gov and GovInfo API |
| Dashboard Proof of Concept | Done | Features mentioned below |
| AI Classification pipeline | In Progress | Building script using OpenAI API and testing on subset of data, iteratively refine model to handle edge cases |
| Web hosting architecture | In Progress | Collaboration with UH IT on deployment strategy |
| Manual Data QC validation | In Progress | - |

## Data Schema

| Column | Description |
|--------|-------------|
| `congress` | Congress number (1–118) |
| `volume` | Statute volume |
| `chapter` | Chapter number |
| `title` | Law title |
| `date` | Enactment date |
| `subject_category` | Subject classification(s) |
| `relief_category` | Relief type classification(s) |
| `summary` | Brief description |
| `pdf_link` | Link to PDF document |
| `details_link` | Link to Congress.gov page |


## Dashboard Features

- **Interactive Timeline**: View laws by year or Congress session
- **Category Filtering**: Filter by subject matter or relief category
- **Search**: Full-text search across titles, dates, and categories
- **Export**: Download filtered results as CSV

## Libraries Used

- [Dash](https://dash.plotly.com/) - Web framework
- [Plotly](https://plotly.com/) - Interactive charts
- [Pandas](https://pandas.pydata.org/) - Data processing
- [Gunicorn](https://gunicorn.org/) - WSGI server

## Credits

Developed by **Kenneth Nguyen**.  
This project was completed in collaboration with the **University of Houston Law Center** and **Professor Chris Mirasola** as part of ongoing research into private legislation.
