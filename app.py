"""
Private Laws Database Dashboard
===============================
A comprehensive interactive dashboard for exploring 45,000+ Congressional Private Laws (1789-2025)

Features:
- Interactive timeline with year/congress toggle
- Multi-category subject matter breakdown with side-by-side chart and table
- Click-to-filter on breakdown charts or checkboxes
- Search and export functionality
- Responsive dark theme with blue accent, orange filter highlight

Run locally: python app.py
Open: http://127.0.0.1:8050
"""

import os
import dash

from styles import CUSTOM_CSS
from layout import create_layout
from callbacks import register_callbacks
from data_loader import load_data_from_csv, generate_sample_data

# =============================================================================
# CONFIGURATION
# =============================================================================

# Data file path - adjust if needed
DATA_FILE = 'Private_Laws_Data.csv'

# Use sample data if CSV not found (for testing)
USE_SAMPLE_IF_MISSING = True

# =============================================================================
# LOAD DATA
# =============================================================================

if os.path.exists(DATA_FILE):
    df = load_data_from_csv(DATA_FILE)
else:
    if USE_SAMPLE_IF_MISSING:
        print(f"⚠ {DATA_FILE} not found. Using sample data for testing.")
        df = generate_sample_data(5000)
    else:
        raise FileNotFoundError(f"Data file not found: {DATA_FILE}")

# =============================================================================
# APP INITIALIZATION
# =============================================================================

app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Private Law Database"

# Custom CSS
app.index_string = CUSTOM_CSS

# Set layout
app.layout = create_layout()

# Register callbacks
register_callbacks(app, df)

# Expose server for deployment (Render, Gunicorn, etc.)
server = app.server

# =============================================================================
# RUN SERVER
# =============================================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("  Private Law Database Dashboard")
    print("="*60)
    print(f"\n  ✓ Loaded {len(df):,} records")
    print(f"  ✓ Year range: {df['year'].min()} - {df['year'].max()}")
    print("\n  Open your browser to: http://127.0.0.1:8050")
    print("\n  Press Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    # IMPORTANT: debug=False for production/deployment
    app.run(debug=False, host='0.0.0.0', port=8050)
