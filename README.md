# Private Laws Database Dashboard (In-Progress)

An interactive dashboard for exploring 45,000+ Congressional Private Laws from 1789-2025.

## Features

- **Interactive Timeline**: View laws by year or Congress session
- **Category Filtering**: Filter by subject matter or relief category
- **Search**: Full-text search across titles, dates, and categories
- **Export**: Download filtered results as CSV
- **Responsive Design**: Dark theme with intuitive navigation

## Project Structure

```
private-laws-dashboard/
├── app.py              # Main application
├── layout.py           # Dashboard layout components
├── callbacks.py        # Dash callback functions
├── styles.py           # Color theme and styling
├── config.py           # Category definitions
├── data_loader.py      # Data loading utilities
├── requirements.txt    # Python dependencies
├── .gitignore          # Git ignore rules
├── Private_Laws_Data.csv  # Dataset
└── README.md           
```

## Next Steps

1. Modify the AI pipeline to categorize and summarize each private law based on updated codebooks
2. Use a subset of data (~500 private laws) to test AI pipeline and manually QC

## Data Format

The CSV file should contain these columns:
- `congress`: Congress number
- `volume`: Statute volume
- `chapter`: Chapter number
- `title`: Law title
- `date`: Enactment date
- `year`: Year (derived from date if not present)
- `subject_category`: Subject classification(s)
- `relief_category`: Relief type classification(s)
- `summary`: Brief description
- `pdf_link`: Link to PDF document
- `details_link`: Link to Congress.gov page

## Libraries Used

- [Dash](https://dash.plotly.com/) - Web framework
- [Plotly](https://plotly.com/) - Interactive charts
- [Pandas](https://pandas.pydata.org/) - Data processing
- [Gunicorn](https://gunicorn.org/) - WSGI server

## Credits

Developed by **Kenneth Nguyen**.  
This project was completed in collaboration with the **University of Houston Law Center** and **Professor Chris Mirasola** as part of ongoing research into private legislation.
