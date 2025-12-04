# Private Laws Database Dashboard

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
├── app.py              # Main application entry point
├── layout.py           # Dashboard layout components
├── callbacks.py        # Dash callback functions
├── styles.py           # Color theme and styling
├── config.py           # Category definitions
├── data_loader.py      # Data loading utilities
├── requirements.txt    # Python dependencies
├── .gitignore          # Git ignore rules
├── Private_Laws_Data.csv  # Dataset (not in repo)
└── README.md           # This file
```

## Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Private-Law-Dashboard.git
   cd Private-Law-Dashboard
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Add your `Private_Laws_Data.csv` file to the project root

5. Run the application:
   ```bash
   python app.py
   ```

6. Open http://127.0.0.1:8050 in your browser

## Deployment (Render)

This app is configured for deployment on Render:

- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:server`

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

## Tech Stack

- [Dash](https://dash.plotly.com/) - Web framework
- [Plotly](https://plotly.com/) - Interactive charts
- [Pandas](https://pandas.pydata.org/) - Data processing
- [Gunicorn](https://gunicorn.org/) - WSGI server

## Author

Kenneth Nguyen

## License

MIT
