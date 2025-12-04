"""
Private Laws Database Dashboard v3
==================================
A comprehensive interactive dashboard for exploring 45,000+ Congressional Private Laws (1789-2025)

Features:
- Interactive timeline with year/congress toggle
- Multi-category subject matter breakdown with side-by-side chart and table
- Click-to-filter on breakdown charts or checkboxes
- Search and export functionality
- Responsive dark theme with blue accent, orange filter highlight

Run: python private_laws_dashboard_v3.py
Open: http://127.0.0.1:8050
"""

import dash
from dash import dcc, html, dash_table, callback, Input, Output, State, ctx
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from io import StringIO

# =============================================================================
# COLOR THEME - Blue shades with proper contrast + Orange for filtering
# =============================================================================

COLORS = {
    # Backgrounds
    'bg_dark': '#0d1117',
    'bg_card': '#161b22',
    'bg_elevated': '#1c2128',
    'bg_hover': '#21262d',
    
    # Borders & Dividers
    'border': '#30363d',
    'border_light': '#484f58',
    'divider': '#21262d',
    
    # Text
    'text_primary': '#f0f6fc',
    'text_secondary': '#8b949e',
    'text_muted': '#6e7681',
    
    # Accent Blues
    'accent_primary': '#58a6ff',
    'accent_light': '#79c0ff',
    'accent_dark': '#1f6feb',
    'accent_subtle': '#388bfd26',
    
    # Filter/Historical Orange
    'filter_orange': '#d4a84b',
    'filter_orange_light': '#e8c078',
    'filter_orange_subtle': '#d4a84b33',
    
    # Highlight
    'highlight_row': '#1f6feb',
    'highlight_header': '#58a6ff',
    
    # Chart colors
    'bar_default': '#58a6ff',
    'bar_active': '#d4a84b',  # Orange when filtered
    'bar_muted': '#30363d',
    
    # Status
    'success': '#3fb950',
    'warning': '#d29922',
    'error': '#f85149'
}

# =============================================================================
# CATEGORY DEFINITIONS
# =============================================================================

SUBJECT_CATEGORIES = [
    "Macroeconomics",
    "Civil Rights, Minority Issues, and Civil Liberties",
    "Health",
    "Agriculture",
    "Labor and Employment",
    "Education",
    "Environment",
    "Energy",
    "Immigration",
    "Transportation",
    "Law, Crime, and Family Issues",
    "Social Welfare",
    "Community Development and Housing Ideas",
    "Banking, Finance, and Domestic Commerce",
    "Defense",
    "Space, Science, Technology, and Communications",
    "Foreign Trade",
    "International Affairs and Foreign Aid",
    "Government Operations",
    "Public Lands and Water Management",
    "District of Columbia Affairs"
]

RELIEF_CATEGORIES = [
    "For Federal Government Service",
    "For Federal Contract Claims",
    "For Damage Caused by the Federal Government",
    "Federal Tax Relief",
    "Relief from Non-Tax Federal Monetary Obligations",
    "Real Property",
    "Chattel Property",
    "Patent Rights or Copyright",
    "Adjusting Immigration Status",
    "Bringing Claims Before Article III Court",
    "Bringing Claims Before an Existing, Non–Article III Tribunal",
    "Creating Ad Hoc Adjudication Process",
    "Directing Further Fact-Finding",
    "Statutory or Regulatory Procedures and Obligations",
    "Article III and non-Article III Procedures or Decisions",
    "Relief from Constitutional Disability",
    "Providing or Amending an Institutional Charter",
    "Granting a Divorce or Authorizing a Name Change",
    "Payment of Private Liabilities",
    "Providing Relief from Harm Caused by Natural or non-Natural Disasters"
]

# =============================================================================
# DATA LOADING FUNCTIONS
# =============================================================================

def load_data_from_csv(filepath):
    """Load private laws data from CSV file with robust date handling."""
    df = pd.read_csv(filepath)
    
    if 'id' not in df.columns:
        df['id'] = range(1, len(df) + 1)
    
    if 'date' in df.columns:
        for fmt in ['%Y-%m-%d', '%m-%d-%Y', '%m/%d/%Y', '%Y/%m/%d', '%d-%m-%Y', '%d/%m/%Y']:
            try:
                df['date'] = pd.to_datetime(df['date'], format=fmt)
                print(f"✓ Parsed dates with format: {fmt}")
                break
            except (ValueError, TypeError):
                continue
        else:
            try:
                df['date'] = pd.to_datetime(df['date'])
                print("✓ Parsed dates using pandas auto-detection")
            except Exception as e:
                print(f"⚠ Could not parse dates: {e}")
    
    if 'year' not in df.columns and 'date' in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df['date']):
            df['year'] = df['date'].dt.year
        else:
            df['year'] = pd.to_datetime(df['date'], errors='coerce').dt.year
    
    df['year'] = df['year'].astype(int)
    
    if 'subject_category' in df.columns:
        df['subject_category'] = df['subject_category'].fillna('')
    
    if 'relief_category' in df.columns:
        df['relief_category'] = df['relief_category'].fillna('')
    
    for col in ['summary', 'pdf_link', 'details_link']:
        if col not in df.columns:
            df[col] = ''
    
    print(f"✓ Loaded {len(df):,} records")
    print(f"✓ Year range: {df['year'].min()} - {df['year'].max()}")
    
    return df


def generate_sample_data(n_records=5000):
    """Generate sample data for testing."""
    np.random.seed(42)
    
    years = []
    for _ in range(n_records):
        period = np.random.choice(['early', 'mid', 'peak', 'modern'], p=[0.1, 0.2, 0.5, 0.2])
        if period == 'early':
            years.append(np.random.randint(1789, 1860))
        elif period == 'mid':
            years.append(np.random.randint(1860, 1920))
        elif period == 'peak':
            years.append(np.random.randint(1920, 1970))
        else:
            years.append(np.random.randint(1970, 2025))
    
    years = np.array(years)
    congress_numbers = ((years - 1789) // 2) + 1
    
    subjects = []
    for _ in range(n_records):
        n_cats = np.random.choice([1, 2, 3], p=[0.7, 0.25, 0.05])
        cats = np.random.choice(SUBJECT_CATEGORIES, n_cats, replace=False)
        subjects.append(", ".join(cats))
    
    data = {
        'id': range(1, n_records + 1),
        'congress': congress_numbers,
        'volume': np.random.randint(1, 150, n_records),
        'chapter': np.random.randint(1, 500, n_records),
        'title': [f"An Act for the Relief of {np.random.choice(['John', 'Mary', 'James', 'Elizabeth', 'William', 'Sarah'])} {np.random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis'])}" for _ in range(n_records)],
        'date': pd.to_datetime([f"{y}-{np.random.randint(1,13):02d}-{np.random.randint(1,29):02d}" for y in years]),
        'year': years,
        'subject_category': subjects,
        'relief_category': [''] * n_records,
        'summary': ["This private law provides relief to the named individual(s)." for _ in range(n_records)],
        'pdf_link': [f"https://www.govinfo.gov/content/pkg/STATUTE-{v}/pdf/STATUTE-{v}-Pg{c}.pdf" for v, c in zip(np.random.randint(1, 120, n_records), np.random.randint(1, 1000, n_records))],
        'details_link': [f"https://www.congress.gov/bill/{c}th-congress/private-law/{np.random.randint(1, 500)}" for c in congress_numbers]
    }
    
    return pd.DataFrame(data).sort_values('date').reset_index(drop=True)


def get_ordinal_suffix(n):
    """Return ordinal suffix for a number (1st, 2nd, 3rd, etc.)"""
    if 11 <= (n % 100) <= 13:
        return 'th'
    else:
        return {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')


def truncate_label(text, max_length=25):
    """Truncate text to max length with ellipsis."""
    if len(str(text)) > max_length:
        return str(text)[:max_length-3] + "..."
    return str(text)


def count_categories(df, category_column, valid_categories):
    """Count category assignments from a column that may contain multiple categories."""
    counts = {cat: 0 for cat in valid_categories}
    sorted_categories = sorted(valid_categories, key=len, reverse=True)
    
    for value in df[category_column]:
        if pd.isna(value) or value == '':
            continue
        
        value_str = str(value).strip()
        
        for cat in sorted_categories:
            if cat in value_str:
                counts[cat] += 1
                value_str = value_str.replace(cat, '', 1)
    
    return counts


# =============================================================================
# LOAD DATA
# =============================================================================

# OPTION 1: Load from CSV
df = load_data_from_csv('Private_Laws_Data.csv')

# OPTION 2: Use sample data for testing
# df = generate_sample_data(5000)

# =============================================================================
# APP INITIALIZATION
# =============================================================================

app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Private Law Database"

# =============================================================================
# CUSTOM CSS
# =============================================================================

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            ::-webkit-scrollbar {
                width: 8px;
                height: 8px;
            }
            ::-webkit-scrollbar-track {
                background: #161b22;
            }
            ::-webkit-scrollbar-thumb {
                background: #30363d;
                border-radius: 4px;
            }
            ::-webkit-scrollbar-thumb:hover {
                background: #484f58;
            }
            
            .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner th {
                position: sticky !important;
                top: 0 !important;
                z-index: 10 !important;
            }
            
            .rc-slider-track {
                background-color: #58a6ff !important;
            }
            .rc-slider-handle {
                border-color: #58a6ff !important;
            }
            .rc-slider-rail {
                background-color: #30363d !important;
            }
            
            /* Custom checkbox styling */
            input[type="checkbox"] {
                accent-color: #d4a84b;
                width: 14px;
                height: 14px;
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# =============================================================================
# COMPONENT STYLES
# =============================================================================

def section_header_style():
    return {
        'color': COLORS['text_primary'],
        'fontSize': '20px',
        'fontWeight': '600',
        'marginBottom': '0',
        'paddingBottom': '5px',
        'borderBottom': f"2px solid {COLORS['accent_primary']}",
        'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif'
    }


def subsection_header_style():
    return {
        'color': COLORS['text_primary'],
        'fontSize': '15px',
        'fontWeight': '500',
        'marginBottom': '4px',
        'marginTop': '0',
        'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif'
    }


def card_style():
    return {
        'backgroundColor': COLORS['bg_card'],
        'border': f"1px solid {COLORS['border']}",
        'borderRadius': '8px',
        'padding': '20px',
        'paddingTop': '0px'
    }


def gradient_divider():
    return html.Div(style={
        'height': '1px',
        'background': f"linear-gradient(90deg, transparent, {COLORS['border_light']}, transparent)",
        'margin': '16px 0'
    })


# =============================================================================
# LAYOUT
# =============================================================================

app.layout = html.Div([
    # Stores for state management
    dcc.Store(id='selected-subject-category', data=None),
    dcc.Store(id='selected-relief-category', data=None),
    dcc.Store(id='selected-law-id', data=None),
    dcc.Store(id='current-year-range', data=[1789, 2025]),
    dcc.Download(id='download-csv'),
    
    # Header
    html.Div([
        html.H1(children=[
            html.Span("│", style={'color': COLORS['accent_primary'], 'fontWeight': '300'}),
            "Private Law Database"
        ], style={
            'color': COLORS['text_primary'],
            'margin': '0',
            'padding': '16px 24px',
            'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif',
            'fontWeight': '600',
            'fontSize': '24px',
            'display': 'flex',
            'alignItems': 'center',
            'gap': '12px'
        })
    ], style={
        'backgroundColor': COLORS['bg_dark'],
        'borderBottom': f"1px solid {COLORS['border']}"
    }),
    
    # Main Content
    html.Div([
        # LEFT COLUMN (60%) - Timeline + List of Private Laws
        html.Div([
            # Timeline Panel (includes Filter subsection)
            html.Div([
                html.H2("Timeline", style=section_header_style()),
                
                html.Div(style={'height': '16px'}),
                
                # View Toggle
                html.Div([
                    html.Label("View by: ", style={
                        'color': COLORS['text_secondary'],
                        'marginRight': '12px',
                        'fontSize': '13px'
                    }),
                    dcc.RadioItems(
                        id='timeline-view-toggle',
                        options=[
                            {'label': ' Year', 'value': 'year'},
                            {'label': ' Congress', 'value': 'congress'}
                        ],
                        value='year',
                        inline=True,
                        style={'display': 'inline-flex', 'gap': '20px'},
                        inputStyle={'marginRight': '6px', 'accentColor': COLORS['accent_primary']},
                        labelStyle={'color': COLORS['text_primary'], 'fontSize': '13px', 'cursor': 'pointer'}
                    )
                ], style={'marginBottom': '12px'}),
                
                # Timeline Chart
                dcc.Graph(
                    id='timeline-chart',
                    config={'displayModeBar': False},
                    style={'height': '250px'}
                ),
                
                gradient_divider(),
                
                # Filter Subsection
                html.Div([
                    html.H4("Filter", style={
                        'color': COLORS['text_secondary'],
                        'fontSize': '12px',
                        'fontWeight': '600',
                        'textTransform': 'uppercase',
                        'letterSpacing': '1px',
                        'margin': '0 0 12px 0'
                    }),
                    
                    # Year Range Display
                    html.Div([
                        html.Div([
                            html.Label("FROM", style={
                                'color': COLORS['text_muted'],
                                'fontSize': '10px',
                                'fontWeight': '600',
                                'textTransform': 'uppercase',
                                'letterSpacing': '1px'
                            }),
                            html.Div(id='year-from-display', style={
                                'color': COLORS['accent_primary'],
                                'fontSize': '22px',
                                'fontWeight': '600'
                            })
                        ], style={'display': 'inline-block', 'marginRight': '40px'}),
                        html.Div([
                            html.Label("TO", style={
                                'color': COLORS['text_muted'],
                                'fontSize': '10px',
                                'fontWeight': '600',
                                'textTransform': 'uppercase',
                                'letterSpacing': '1px'
                            }),
                            html.Div(id='year-to-display', style={
                                'color': COLORS['accent_primary'],
                                'fontSize': '22px',
                                'fontWeight': '600'
                            })
                        ], style={'display': 'inline-block'}),
                        
                        # Total Count inline
                        html.Div([
                            html.Span("Total: ", style={
                                'color': COLORS['text_secondary'],
                                'fontSize': '12px'
                            }),
                            html.Span(id='total-laws-count', style={
                                'color': COLORS['accent_primary'],
                                'fontSize': '18px',
                                'fontWeight': '700'
                            })
                        ], style={'display': 'inline-block', 'float': 'right', 'marginTop': '10px'})
                    ], style={'marginBottom': '16px'}),
                    
                    # Range Slider
                    dcc.RangeSlider(
                        id='year-range-slider',
                        min=1789,
                        max=2025,
                        step=1,
                        value=[1789, 2025],
                        marks={
                            1789: {'label': '1789', 'style': {'color': COLORS['text_muted'], 'fontSize': '11px'}},
                            1850: {'label': '1850', 'style': {'color': COLORS['text_muted'], 'fontSize': '11px'}},
                            1900: {'label': '1900', 'style': {'color': COLORS['text_muted'], 'fontSize': '11px'}},
                            1950: {'label': '1950', 'style': {'color': COLORS['text_muted'], 'fontSize': '11px'}},
                            2000: {'label': '2000', 'style': {'color': COLORS['text_muted'], 'fontSize': '11px'}},
                            2025: {'label': '2025', 'style': {'color': COLORS['text_muted'], 'fontSize': '11px'}}
                        },
                        tooltip={'placement': 'bottom', 'always_visible': False}
                    )
                ])
            ], style={**card_style(), 'marginBottom': '20px', 'minHeight': '420px'}),
            
            # List of Private Laws Panel
            html.Div([
                html.Div([
                    html.H2("List of Private Laws", style={**section_header_style(), 'display': 'inline-block', 'marginRight': '20px'}),
                ], style={'marginBottom': '16px'}),
                
                # Search and Controls Row
                html.Div([
                    html.Div([
                        dcc.Input(
                            id='search-input',
                            type='text',
                            placeholder='Search by title, date, or category...',
                            style={
                                'width': '280px',
                                'padding': '8px 12px',
                                'backgroundColor': COLORS['bg_dark'],
                                'border': f"1px solid {COLORS['border']}",
                                'borderRadius': '6px',
                                'color': COLORS['text_primary'],
                                'fontSize': '13px'
                            }
                        ),
                        html.Button('Reset', id='reset-search-btn', style={
                            'marginLeft': '8px',
                            'padding': '8px 16px',
                            'backgroundColor': 'transparent',
                            'border': f"1px solid {COLORS['border']}",
                            'borderRadius': '6px',
                            'color': COLORS['text_secondary'],
                            'cursor': 'pointer',
                            'fontSize': '13px'
                        })
                    ], style={'display': 'inline-flex', 'alignItems': 'center'}),
                    
                    html.Div([
                        html.Label("Show: ", style={'color': COLORS['text_secondary'], 'fontSize': '13px', 'marginRight': '8px'}),
                        dcc.Dropdown(
                            id='page-size-dropdown',
                            options=[
                                {'label': '10', 'value': 10},
                                {'label': '20', 'value': 20},
                                {'label': '50', 'value': 50},
                                {'label': '100', 'value': 100}
                            ],
                            value=20,
                            clearable=False,
                            style={'width': '70px', 'display': 'inline-block'}
                        ),
                        
                        html.Button([
                            '↓ Export CSV'
                        ], id='export-btn', style={
                            'marginLeft': '16px',
                            'padding': '8px 16px',
                            'backgroundColor': COLORS['accent_dark'],
                            'border': 'none',
                            'borderRadius': '6px',
                            'color': 'white',
                            'cursor': 'pointer',
                            'fontSize': '13px',
                            'fontWeight': '500'
                        })
                    ], style={'display': 'inline-flex', 'alignItems': 'center'})
                ], style={
                    'display': 'flex',
                    'justifyContent': 'space-between',
                    'alignItems': 'center',
                    'marginBottom': '16px',
                    'flexWrap': 'wrap',
                    'gap': '12px'
                }),
                
                # Data Table
                html.Div([
                    dash_table.DataTable(
                        id='laws-table',
                        columns=[
                            {'name': 'Congress', 'id': 'congress', 'type': 'numeric'},
                            {'name': 'Vol.', 'id': 'volume', 'type': 'numeric'},
                            {'name': 'Ch.', 'id': 'chapter', 'type': 'numeric'},
                            {'name': 'Title', 'id': 'title'},
                            {'name': 'Date', 'id': 'date_str'},
                            {'name': 'Subject', 'id': 'subject_short'},
                            {'name': 'View', 'id': 'view_btn', 'presentation': 'markdown'}
                        ],
                        page_size=20,
                        page_current=0,
                        page_action='native',
                        sort_action='native',
                        sort_mode='multi',
                        style_table={
                            'overflowX': 'auto',
                            'overflowY': 'auto',
                            'maxHeight': '500px'
                        },
                        style_header={
                            'backgroundColor': COLORS['bg_dark'],
                            'color': COLORS['text_primary'],
                            'fontWeight': '600',
                            'fontSize': '12px',
                            'textTransform': 'uppercase',
                            'letterSpacing': '0.5px',
                            'border': 'none',
                            'borderBottom': f"2px solid {COLORS['border']}",
                            'textAlign': 'left',
                            'padding': '12px 8px'
                        },
                        style_cell={
                            'backgroundColor': COLORS['bg_card'],
                            'color': COLORS['text_primary'],
                            'border': 'none',
                            'borderBottom': f"1px solid {COLORS['border']}",
                            'textAlign': 'left',
                            'padding': '10px 8px',
                            'fontSize': '13px',
                            'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif',
                            'maxWidth': '250px',
                            'overflow': 'hidden',
                            'textOverflow': 'ellipsis'
                        },
                        style_cell_conditional=[
                            {'if': {'column_id': 'congress'}, 'width': '70px', 'textAlign': 'center'},
                            {'if': {'column_id': 'volume'}, 'width': '50px', 'textAlign': 'center'},
                            {'if': {'column_id': 'chapter'}, 'width': '50px', 'textAlign': 'center'},
                            {'if': {'column_id': 'title'}, 'width': '300px'},
                            {'if': {'column_id': 'date_str'}, 'width': '100px'},
                            {'if': {'column_id': 'subject_short'}, 'width': '180px'},
                            {'if': {'column_id': 'view_btn'}, 'width': '60px', 'textAlign': 'center'}
                        ],
                        style_data_conditional=[
                            {
                                'if': {'state': 'active'},
                                'backgroundColor': COLORS['highlight_row'],
                                'border': 'none'
                            }
                        ],
                        markdown_options={'html': True},
                        css=[
                            {'selector': '.dash-table-container', 'rule': 'font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;'},
                            {'selector': '.current-page', 'rule': f'color: {COLORS["text_primary"]} !important;'},
                            {'selector': '.previous-next-container', 'rule': f'color: {COLORS["text_primary"]} !important;'},
                            {'selector': '.page-number', 'rule': f'color: {COLORS["text_primary"]} !important;'}
                        ]
                    )
                ], style={'borderRadius': '6px', 'overflow': 'hidden'})
            ], style=card_style())
        ], style={'width': '60%', 'paddingRight': '20px'}),
        
        # RIGHT COLUMN (40%) - Breakdown + Private Law Information
        html.Div([
            # Breakdown Panel
            html.Div([
                html.H2(id='breakdown-header', children="Breakdown (1789 - 2025)", style=section_header_style()),
                
                html.Div(style={'height': '16px'}),
                
                # Subject Matter Categories Subsection
                html.Div([
                    html.Div([
                        html.Div([
                            html.H3("Subject Matter Category", style=subsection_header_style()),
                            html.P("Click on bar or checkbox to filter", style={
                                'color': COLORS['text_muted'],
                                'fontSize': '11px',
                                'margin': '0',
                                'fontStyle': 'italic'
                            })
                        ]),
                        html.Button('Reset', id='reset-subject-filter-btn', style={
                            'padding': '4px 12px',
                            'backgroundColor': 'transparent',
                            'border': f"1px solid {COLORS['border']}",
                            'borderRadius': '4px',
                            'color': COLORS['text_muted'],
                            'cursor': 'pointer',
                            'fontSize': '11px',
                            'display': 'none'
                        })
                    ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'flex-start', 'marginBottom': '8px'}),
                    
                    # Side-by-side: Bar Chart | Table
                    html.Div([
                        # Bar Chart
                        html.Div([
                            dcc.Graph(
                                id='subject-breakdown-chart',
                                config={'displayModeBar': False},
                                style={'height': '180px'}
                            )
                        ], style={'width': '55%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                        
                        # Table with checkboxes
                        html.Div([
                            html.Div(id='subject-counts-table', style={
                                'maxHeight': '180px',
                                'overflowY': 'auto',
                                'border': f"1px solid {COLORS['border']}",
                                'borderRadius': '4px'
                            })
                        ], style={'width': '45%', 'display': 'inline-block', 'verticalAlign': 'top', 'paddingLeft': '8px'})
                    ], style={'display': 'flex'})
                ]),
                
                gradient_divider(),
                
                # Relief Categories Subsection
                html.Div([
                    html.Div([
                        html.Div([
                            html.H3("Relief Category", style=subsection_header_style()),
                            html.P("Click on bar or checkbox to filter", style={
                                'color': COLORS['text_muted'],
                                'fontSize': '11px',
                                'margin': '0',
                                'fontStyle': 'italic'
                            })
                        ]),
                        html.Button('Reset', id='reset-relief-filter-btn', style={
                            'padding': '4px 12px',
                            'backgroundColor': 'transparent',
                            'border': f"1px solid {COLORS['border']}",
                            'borderRadius': '4px',
                            'color': COLORS['text_muted'],
                            'cursor': 'pointer',
                            'fontSize': '11px',
                            'display': 'none'
                        })
                    ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'flex-start', 'marginBottom': '8px'}),
                    
                    html.Div(id='relief-section-content')
                ])
            ], style={**card_style(), 'marginBottom': '20px', 'minHeight': '420px'}),
            
            # Private Law Information Panel
            html.Div([
                html.H2(id='info-panel-header', children="Private Law Information", style={
                    **section_header_style(),
                    'borderBottomColor': COLORS['border']
                }),
                
                html.Div(style={'height': '16px'}),
                
                html.Div(id='law-info-content', children=[
                    html.Div([
                        html.Span("→", style={
                            'fontSize': '32px',
                            'color': COLORS['text_muted'],
                            'marginBottom': '16px',
                            'display': 'block'
                        }),
                        html.P("Select a private law from the table to view details", style={
                            'color': COLORS['text_muted'],
                            'fontSize': '14px',
                            'margin': '0'
                        })
                    ], style={'textAlign': 'center', 'padding': '60px 20px'})
                ])
            ], style=card_style())
        ], style={'width': '40%'})
    ], style={
        'display': 'flex',
        'padding': '24px',
        'backgroundColor': COLORS['bg_dark'],
        'minHeight': 'calc(100vh - 60px)',
        'alignItems': 'flex-start'
    })
], style={
    'backgroundColor': COLORS['bg_dark'],
    'minHeight': '100vh',
    'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif'
})

# =============================================================================
# CALLBACKS
# =============================================================================

@callback(
    Output('year-from-display', 'children'),
    Output('year-to-display', 'children'),
    Output('current-year-range', 'data'),
    Output('breakdown-header', 'children'),
    Input('year-range-slider', 'value')
)
def update_year_display(year_range):
    """Update year display and store current range."""
    start, end = year_range
    breakdown_header = f"Breakdown ({start} - {end})"
    return str(start), str(end), year_range, breakdown_header


@callback(
    Output('timeline-chart', 'figure'),
    Output('total-laws-count', 'children'),
    Output('subject-breakdown-chart', 'figure'),
    Output('subject-counts-table', 'children'),
    Output('relief-section-content', 'children'),
    Input('year-range-slider', 'value'),
    Input('timeline-view-toggle', 'value'),
    Input('selected-subject-category', 'data'),
    Input('selected-relief-category', 'data')
)
def update_all_charts(year_range, view_type, selected_subject, selected_relief):
    """Update all charts based on filters."""
    start_year, end_year = year_range
    
    # Filter by year range
    filtered_df = df[(df['year'] >= start_year) & (df['year'] <= end_year)]
    
    # Apply category filters if active
    if selected_subject:
        filtered_df = filtered_df[filtered_df['subject_category'].str.contains(selected_subject, na=False, regex=False)]
    if selected_relief:
        filtered_df = filtered_df[filtered_df['relief_category'].str.contains(selected_relief, na=False, regex=False)]
    
    total_count = len(filtered_df)
    
    # Determine timeline bar color based on filter state
    timeline_bar_color = COLORS['filter_orange'] if (selected_subject or selected_relief) else COLORS['bar_default']
    
    # ===== TIMELINE CHART =====
    if view_type == 'year':
        timeline_data = filtered_df.groupby('year').size().reset_index(name='count')
        x_data = timeline_data['year']
        x_title = 'Year'
        hover_template = 'Year: %{x}<br>Laws: %{y:,}<extra></extra>'
    else:
        timeline_data = filtered_df.groupby('congress').size().reset_index(name='count')
        x_data = timeline_data['congress']
        x_title = 'Congress'
        hover_template = 'Congress: %{x}<br>Laws: %{y:,}<extra></extra>'
    
    timeline_fig = go.Figure(data=[
        go.Bar(
            x=x_data,
            y=timeline_data['count'],
            marker_color=timeline_bar_color,
            hovertemplate=hover_template
        )
    ])
    
    timeline_fig.update_layout(
        plot_bgcolor=COLORS['bg_card'],
        paper_bgcolor=COLORS['bg_card'],
        font_color=COLORS['text_primary'],
        margin=dict(l=50, r=20, t=10, b=40),
        xaxis=dict(
            gridcolor=COLORS['border'],
            showgrid=False,
            title=x_title,
            title_font=dict(size=11, color=COLORS['text_secondary'])
        ),
        yaxis=dict(
            gridcolor=COLORS['border'],
            showgrid=True,
            title='Private Laws',
            title_font=dict(size=11, color=COLORS['text_secondary'])
        ),
        hoverlabel=dict(bgcolor=COLORS['bg_elevated'], font_color=COLORS['text_primary']),
        bargap=0.15
    )
    
    # ===== SUBJECT BREAKDOWN =====
    year_filtered_df = df[(df['year'] >= start_year) & (df['year'] <= end_year)]
    subject_counts = count_categories(year_filtered_df, 'subject_category', SUBJECT_CATEGORIES)
    
    sorted_subjects = sorted(subject_counts.items(), key=lambda x: x[1], reverse=True)
    categories = [item[0] for item in sorted_subjects]
    counts = [item[1] for item in sorted_subjects]
    total_assignments = sum(counts)
    percentages = [(c / total_assignments * 100) if total_assignments > 0 else 0 for c in counts]
    
    # Truncated labels for chart
    truncated_cats = [truncate_label(cat, 20) for cat in categories]
    
    bar_colors = []
    for cat in categories:
        if selected_subject:
            if cat == selected_subject:
                bar_colors.append(COLORS['filter_orange'])
            else:
                bar_colors.append(COLORS['bar_muted'])
        else:
            bar_colors.append(COLORS['bar_default'])
    
    subject_fig = go.Figure(data=[
        go.Bar(
            y=truncated_cats[::-1],
            x=percentages[::-1],
            orientation='h',
            marker_color=bar_colors[::-1],
            text=[f'{p:.1f}%' for p in percentages[::-1]],
            textposition='outside',
            textfont=dict(size=9, color=COLORS['text_secondary']),
            hovertemplate='%{customdata}<br>%{x:.1f}%<extra></extra>',
            customdata=categories[::-1]
        )
    ])
    
    subject_fig.update_layout(
        plot_bgcolor=COLORS['bg_card'],
        paper_bgcolor=COLORS['bg_card'],
        font_color=COLORS['text_primary'],
        margin=dict(l=120, r=45, t=5, b=5),
        xaxis=dict(
            showgrid=False,
            showticklabels=False,
            range=[0, max(percentages) * 1.3] if percentages else [0, 100]
        ),
        yaxis=dict(
            showgrid=False,
            tickfont=dict(size=9, color=COLORS['text_secondary'])
        ),
        hoverlabel=dict(bgcolor=COLORS['bg_elevated'], font_color=COLORS['text_primary']),
        bargap=0.25
    )
    
    # Subject counts table with checkboxes
    table_rows = []
    for cat, cnt in sorted_subjects:
        is_selected = cat == selected_subject
        row_bg = COLORS['filter_orange_subtle'] if is_selected else 'transparent'
        text_color = COLORS['filter_orange'] if is_selected else COLORS['text_secondary']
        
        table_rows.append(
            html.Tr([
                html.Td(
                    dcc.Checklist(
                        options=[{'label': '', 'value': cat}],
                        value=[cat] if is_selected else [],
                        id={'type': 'subject-checkbox', 'index': cat},
                        style={'margin': '0'}
                    ),
                    style={'padding': '4px 6px', 'width': '30px', 'textAlign': 'center'}
                ),
                html.Td(
                    truncate_label(cat, 22),
                    title=cat,
                    style={
                        'color': text_color,
                        'padding': '4px 6px',
                        'fontSize': '11px',
                        'cursor': 'pointer'
                    }
                ),
                html.Td(
                    f"{cnt:,}",
                    style={
                        'color': COLORS['accent_primary'],
                        'textAlign': 'right',
                        'padding': '4px 6px',
                        'fontSize': '11px',
                        'fontWeight': '600'
                    }
                )
            ], style={'backgroundColor': row_bg, 'borderBottom': f"1px solid {COLORS['divider']}"})
        )
    
    subject_table = html.Table([
        html.Thead(html.Tr([
            html.Th("", style={
                'width': '30px',
                'padding': '6px',
                'backgroundColor': COLORS['bg_dark'],
                'borderBottom': f"1px solid {COLORS['border']}"
            }),
            html.Th("Category", style={
                'textAlign': 'left',
                'color': COLORS['text_primary'],
                'backgroundColor': COLORS['bg_dark'],
                'padding': '6px',
                'fontSize': '10px',
                'fontWeight': '600',
                'textTransform': 'uppercase',
                'borderBottom': f"1px solid {COLORS['border']}"
            }),
            html.Th("Laws", style={
                'textAlign': 'right',
                'color': COLORS['text_primary'],
                'backgroundColor': COLORS['bg_dark'],
                'padding': '6px',
                'fontSize': '10px',
                'fontWeight': '600',
                'textTransform': 'uppercase',
                'borderBottom': f"1px solid {COLORS['border']}"
            })
        ])),
        html.Tbody(table_rows)
    ], style={'width': '100%', 'borderCollapse': 'collapse', 'fontSize': '11px'})
    
    # ===== RELIEF BREAKDOWN =====
    relief_counts = count_categories(year_filtered_df, 'relief_category', RELIEF_CATEGORIES)
    has_relief_data = sum(relief_counts.values()) > 0
    
    if has_relief_data:
        sorted_relief = sorted(relief_counts.items(), key=lambda x: x[1], reverse=True)
        r_categories = [item[0] for item in sorted_relief]
        r_counts = [item[1] for item in sorted_relief]
        r_total = sum(r_counts)
        r_percentages = [(c / r_total * 100) if r_total > 0 else 0 for c in r_counts]
        
        r_truncated = [truncate_label(cat, 20) for cat in r_categories]
        
        r_bar_colors = []
        for cat in r_categories:
            if selected_relief:
                if cat == selected_relief:
                    r_bar_colors.append(COLORS['filter_orange'])
                else:
                    r_bar_colors.append(COLORS['bar_muted'])
            else:
                r_bar_colors.append(COLORS['bar_default'])
        
        relief_fig = go.Figure(data=[
            go.Bar(
                y=r_truncated[::-1],
                x=r_percentages[::-1],
                orientation='h',
                marker_color=r_bar_colors[::-1],
                text=[f'{p:.1f}%' for p in r_percentages[::-1]],
                textposition='outside',
                textfont=dict(size=9, color=COLORS['text_secondary']),
                hovertemplate='%{customdata}<br>%{x:.1f}%<extra></extra>',
                customdata=r_categories[::-1]
            )
        ])
        
        relief_fig.update_layout(
            plot_bgcolor=COLORS['bg_card'],
            paper_bgcolor=COLORS['bg_card'],
            font_color=COLORS['text_primary'],
            margin=dict(l=120, r=45, t=5, b=5),
            height=180,
            xaxis=dict(showgrid=False, showticklabels=False, range=[0, max(r_percentages) * 1.3] if r_percentages else [0, 100]),
            yaxis=dict(showgrid=False, tickfont=dict(size=9, color=COLORS['text_secondary'])),
            hoverlabel=dict(bgcolor=COLORS['bg_elevated'], font_color=COLORS['text_primary']),
            bargap=0.25
        )
        
        # Relief table
        r_table_rows = []
        for cat, cnt in sorted_relief:
            is_selected = cat == selected_relief
            row_bg = COLORS['filter_orange_subtle'] if is_selected else 'transparent'
            text_color = COLORS['filter_orange'] if is_selected else COLORS['text_secondary']
            
            r_table_rows.append(
                html.Tr([
                    html.Td(
                        dcc.Checklist(
                            options=[{'label': '', 'value': cat}],
                            value=[cat] if is_selected else [],
                            id={'type': 'relief-checkbox', 'index': cat},
                            style={'margin': '0'}
                        ),
                        style={'padding': '4px 6px', 'width': '30px', 'textAlign': 'center'}
                    ),
                    html.Td(
                        truncate_label(cat, 22),
                        title=cat,
                        style={
                            'color': text_color,
                            'padding': '4px 6px',
                            'fontSize': '11px',
                            'cursor': 'pointer'
                        }
                    ),
                    html.Td(
                        f"{cnt:,}",
                        style={
                            'color': COLORS['accent_primary'],
                            'textAlign': 'right',
                            'padding': '4px 6px',
                            'fontSize': '11px',
                            'fontWeight': '600'
                        }
                    )
                ], style={'backgroundColor': row_bg, 'borderBottom': f"1px solid {COLORS['divider']}"})
            )
        
        relief_table = html.Table([
            html.Thead(html.Tr([
                html.Th("", style={
                    'width': '30px',
                    'padding': '6px',
                    'backgroundColor': COLORS['bg_dark'],
                    'borderBottom': f"1px solid {COLORS['border']}"
                }),
                html.Th("Category", style={
                    'textAlign': 'left',
                    'color': COLORS['text_primary'],
                    'backgroundColor': COLORS['bg_dark'],
                    'padding': '6px',
                    'fontSize': '10px',
                    'fontWeight': '600',
                    'textTransform': 'uppercase',
                    'borderBottom': f"1px solid {COLORS['border']}"
                }),
                html.Th("Laws", style={
                    'textAlign': 'right',
                    'color': COLORS['text_primary'],
                    'backgroundColor': COLORS['bg_dark'],
                    'padding': '6px',
                    'fontSize': '10px',
                    'fontWeight': '600',
                    'textTransform': 'uppercase',
                    'borderBottom': f"1px solid {COLORS['border']}"
                })
            ])),
            html.Tbody(r_table_rows)
        ], style={'width': '100%', 'borderCollapse': 'collapse', 'fontSize': '11px'})
        
        relief_content = html.Div([
            html.Div([
                dcc.Graph(
                    id='relief-breakdown-chart',
                    figure=relief_fig,
                    config={'displayModeBar': False},
                    style={'height': '180px'}
                )
            ], style={'width': '55%', 'display': 'inline-block', 'verticalAlign': 'top'}),
            html.Div([
                html.Div([relief_table], style={
                    'maxHeight': '180px',
                    'overflowY': 'auto',
                    'border': f"1px solid {COLORS['border']}",
                    'borderRadius': '4px'
                })
            ], style={'width': '45%', 'display': 'inline-block', 'verticalAlign': 'top', 'paddingLeft': '8px'})
        ], style={'display': 'flex'})
    else:
        relief_content = html.Div([
            html.Div([
                html.Span("📊", style={'fontSize': '36px', 'marginBottom': '12px', 'display': 'block'}),
                html.P("Relief category data coming soon", style={
                    'color': COLORS['text_muted'],
                    'fontSize': '13px',
                    'margin': '0 0 4px 0'
                }),
                html.P("This section will populate automatically once data is available.", style={
                    'color': COLORS['text_muted'],
                    'fontSize': '11px',
                    'margin': '0'
                })
            ], style={
                'textAlign': 'center',
                'padding': '40px 20px',
                'backgroundColor': COLORS['bg_dark'],
                'borderRadius': '6px',
                'border': f"1px dashed {COLORS['border']}"
            })
        ])
    
    return timeline_fig, f"{total_count:,}", subject_fig, subject_table, relief_content


@callback(
    Output('laws-table', 'data'),
    Output('laws-table', 'page_size'),
    Output('laws-table', 'style_data_conditional'),
    Input('year-range-slider', 'value'),
    Input('search-input', 'value'),
    Input('selected-subject-category', 'data'),
    Input('selected-relief-category', 'data'),
    Input('page-size-dropdown', 'value'),
    Input('selected-law-id', 'data')
)
def update_table(year_range, search_value, selected_subject, selected_relief, page_size, selected_law_id):
    """Update table based on all filters."""
    start_year, end_year = year_range
    
    filtered_df = df[(df['year'] >= start_year) & (df['year'] <= end_year)].copy()
    
    if selected_subject:
        filtered_df = filtered_df[filtered_df['subject_category'].str.contains(selected_subject, na=False, regex=False)]
    if selected_relief:
        filtered_df = filtered_df[filtered_df['relief_category'].str.contains(selected_relief, na=False, regex=False)]
    
    if search_value:
        search_lower = search_value.lower()
        mask = (
            filtered_df['title'].str.lower().str.contains(search_lower, na=False) |
            filtered_df['date'].astype(str).str.contains(search_lower, na=False) |
            filtered_df['subject_category'].str.lower().str.contains(search_lower, na=False) |
            filtered_df['relief_category'].str.lower().str.contains(search_lower, na=False)
        )
        filtered_df = filtered_df[mask]
    
    if pd.api.types.is_datetime64_any_dtype(filtered_df['date']):
        filtered_df['date_str'] = filtered_df['date'].dt.strftime('%Y-%m-%d')
    else:
        filtered_df['date_str'] = filtered_df['date'].astype(str)
    
    filtered_df['subject_short'] = filtered_df['subject_category'].apply(
        lambda x: (str(x)[:30] + '...') if len(str(x)) > 30 else str(x)
    )
    
    filtered_df['view_btn'] = '→'
    
    table_data = filtered_df[['id', 'congress', 'volume', 'chapter', 'title', 'date_str', 'subject_short', 'view_btn']].to_dict('records')
    
    style_conditional = [
        {
            'if': {'state': 'active'},
            'backgroundColor': COLORS['highlight_row'],
            'border': 'none'
        }
    ]
    
    if selected_law_id:
        style_conditional.append({
            'if': {'filter_query': f'{{id}} = {selected_law_id}'},
            'backgroundColor': COLORS['highlight_row'],
            'color': COLORS['text_primary']
        })
    
    return table_data, page_size, style_conditional


@callback(
    Output('selected-law-id', 'data'),
    Output('info-panel-header', 'style'),
    Output('law-info-content', 'children'),
    Input('laws-table', 'active_cell'),
    State('laws-table', 'data'),
    State('laws-table', 'page_current'),
    State('laws-table', 'page_size'),
    State('laws-table', 'derived_virtual_data')
)
def update_law_info(active_cell, table_data, page_current, page_size, virtual_data):
    """Update info panel when a row is clicked - FIXED for pagination."""
    default_header_style = {
        **section_header_style(),
        'borderBottomColor': COLORS['border']
    }
    
    default_content = html.Div([
        html.Div([
            html.Span("→", style={
                'fontSize': '32px',
                'color': COLORS['text_muted'],
                'marginBottom': '16px',
                'display': 'block'
            }),
            html.P("Select a private law from the table to view details", style={
                'color': COLORS['text_muted'],
                'fontSize': '14px',
                'margin': '0'
            })
        ], style={'textAlign': 'center', 'padding': '60px 20px'})
    ])
    
    if not active_cell:
        return None, default_header_style, default_content
    
    # Get the row index on the current page
    row_on_page = active_cell['row']
    
    # Calculate the actual row index in the full data
    # active_cell['row'] is relative to the current page, so we need to add the page offset
    actual_row_idx = (page_current * page_size) + row_on_page
    
    # Use derived_virtual_data if available (respects sorting/filtering), otherwise use table_data
    data_source = virtual_data if virtual_data else table_data
    
    if not data_source or actual_row_idx >= len(data_source):
        return None, default_header_style, default_content
    
    row_data = data_source[actual_row_idx]
    law_id = row_data['id']
    
    # Get full record from original dataframe
    matching_records = df[df['id'] == law_id]
    if matching_records.empty:
        return None, default_header_style, default_content
    
    full_record = matching_records.iloc[0]
    
    highlighted_header_style = {
        **section_header_style(),
        'borderBottomColor': COLORS['highlight_row']
    }
    
    # Format date
    if pd.api.types.is_datetime64_any_dtype(type(full_record['date'])) or hasattr(full_record['date'], 'strftime'):
        try:
            date_display = full_record['date'].strftime('%B %d, %Y')
        except:
            date_display = str(full_record['date'])
    else:
        date_display = str(full_record['date'])
    
    congress_num = int(full_record['congress'])
    congress_display = f"{congress_num}{get_ordinal_suffix(congress_num)}"
    
    label_style = {
        'color': COLORS['text_muted'],
        'fontSize': '11px',
        'fontWeight': '600',
        'textTransform': 'uppercase',
        'letterSpacing': '0.5px',
        'display': 'block',
        'marginBottom': '4px'
    }
    
    value_style = {
        'color': COLORS['text_primary'],
        'fontSize': '15px',
        'fontWeight': '500'
    }
    
    info_content = html.Div([
        html.Div([
            html.Span("Title", style=label_style),
            html.Div(full_record['title'], style={**value_style, 'fontSize': '16px', 'lineHeight': '1.4'})
        ], style={'marginBottom': '20px'}),
        
        html.Div([
            html.Div([
                html.Span("Congress", style=label_style),
                html.Div(congress_display, style=value_style)
            ], style={'display': 'inline-block', 'width': '30%'}),
            html.Div([
                html.Span("Volume", style=label_style),
                html.Div(str(full_record['volume']), style=value_style)
            ], style={'display': 'inline-block', 'width': '30%'}),
            html.Div([
                html.Span("Chapter", style=label_style),
                html.Div(str(full_record['chapter']), style=value_style)
            ], style={'display': 'inline-block', 'width': '30%'})
        ], style={'marginBottom': '20px'}),
        
        html.Div([
            html.Span("Date Enacted", style=label_style),
            html.Div(date_display, style=value_style)
        ], style={'marginBottom': '20px'}),
        
        html.Div([
            html.Span("Subject Matter Category", style=label_style),
            html.Div(full_record['subject_category'] or "Not categorized", style={
                **value_style,
                'color': COLORS['accent_primary'] if full_record['subject_category'] else COLORS['text_muted']
            })
        ], style={'marginBottom': '20px'}),
        
        html.Div([
            html.Span("Relief Category", style=label_style),
            html.Div(full_record['relief_category'] or "Not categorized", style={
                **value_style,
                'color': COLORS['accent_primary'] if full_record['relief_category'] else COLORS['text_muted']
            })
        ], style={'marginBottom': '20px'}),
        
        html.Div([
            html.Span("Summary", style=label_style),
            html.P(full_record['summary'] or "No summary available.", style={
                'color': COLORS['text_primary'],
                'fontSize': '14px',
                'lineHeight': '1.6',
                'margin': '4px 0 0 0'
            })
        ], style={'marginBottom': '24px'}),
        
        html.Div([
            html.A(
                html.Button("View PDF", style={
                    'backgroundColor': COLORS['accent_primary'],
                    'color': 'white',
                    'border': 'none',
                    'padding': '10px 20px',
                    'borderRadius': '6px',
                    'cursor': 'pointer',
                    'fontSize': '13px',
                    'fontWeight': '500',
                    'marginRight': '12px'
                }),
                href=full_record['pdf_link'] if full_record['pdf_link'] else '#',
                target='_blank'
            ),
            html.A(
                html.Button("View on Congress.gov", style={
                    'backgroundColor': 'transparent',
                    'color': COLORS['text_primary'],
                    'border': f"1px solid {COLORS['border']}",
                    'padding': '10px 20px',
                    'borderRadius': '6px',
                    'cursor': 'pointer',
                    'fontSize': '13px',
                    'fontWeight': '500'
                }),
                href=full_record['details_link'] if full_record['details_link'] else '#',
                target='_blank'
            )
        ])
    ])
    
    return law_id, highlighted_header_style, info_content


@callback(
    Output('selected-subject-category', 'data'),
    Output('reset-subject-filter-btn', 'style'),
    Input('subject-breakdown-chart', 'clickData'),
    Input('reset-subject-filter-btn', 'n_clicks'),
    Input({'type': 'subject-checkbox', 'index': dash.ALL}, 'value'),
    State('selected-subject-category', 'data')
)
def handle_subject_selection(click_data, reset_clicks, checkbox_values, current_selection):
    """Handle clicks on subject breakdown chart or checkboxes."""
    triggered = ctx.triggered_id
    
    button_hidden = {
        'padding': '4px 12px',
        'backgroundColor': 'transparent',
        'border': f"1px solid {COLORS['border']}",
        'borderRadius': '4px',
        'color': COLORS['text_muted'],
        'cursor': 'pointer',
        'fontSize': '11px',
        'display': 'none'
    }
    
    button_visible = {**button_hidden, 'display': 'inline-block'}
    
    # Reset button clicked
    if triggered == 'reset-subject-filter-btn':
        return None, button_hidden
    
    # Chart clicked
    if triggered == 'subject-breakdown-chart' and click_data:
        # Get the original category name from customdata
        clicked_category = click_data['points'][0].get('customdata', click_data['points'][0]['y'])
        if clicked_category == current_selection:
            return None, button_hidden
        return clicked_category, button_visible
    
    # Checkbox clicked
    if isinstance(triggered, dict) and triggered.get('type') == 'subject-checkbox':
        clicked_category = triggered['index']
        # Find which checkbox was checked
        for val in checkbox_values:
            if val and clicked_category in val:
                if clicked_category == current_selection:
                    return None, button_hidden
                return clicked_category, button_visible
        # Checkbox was unchecked
        if clicked_category == current_selection:
            return None, button_hidden
    
    return current_selection, button_visible if current_selection else button_hidden


@callback(
    Output('selected-relief-category', 'data'),
    Output('reset-relief-filter-btn', 'style'),
    Input('relief-breakdown-chart', 'clickData'),
    Input('reset-relief-filter-btn', 'n_clicks'),
    Input({'type': 'relief-checkbox', 'index': dash.ALL}, 'value'),
    State('selected-relief-category', 'data')
)
def handle_relief_selection(click_data, reset_clicks, checkbox_values, current_selection):
    """Handle clicks on relief breakdown chart or checkboxes."""
    triggered = ctx.triggered_id
    
    button_hidden = {
        'padding': '4px 12px',
        'backgroundColor': 'transparent',
        'border': f"1px solid {COLORS['border']}",
        'borderRadius': '4px',
        'color': COLORS['text_muted'],
        'cursor': 'pointer',
        'fontSize': '11px',
        'display': 'none'
    }
    
    button_visible = {**button_hidden, 'display': 'inline-block'}
    
    if triggered == 'reset-relief-filter-btn':
        return None, button_hidden
    
    if triggered == 'relief-breakdown-chart' and click_data:
        clicked_category = click_data['points'][0].get('customdata', click_data['points'][0]['y'])
        if clicked_category == current_selection:
            return None, button_hidden
        return clicked_category, button_visible
    
    if isinstance(triggered, dict) and triggered.get('type') == 'relief-checkbox':
        clicked_category = triggered['index']
        for val in checkbox_values:
            if val and clicked_category in val:
                if clicked_category == current_selection:
                    return None, button_hidden
                return clicked_category, button_visible
        if clicked_category == current_selection:
            return None, button_hidden
    
    return current_selection, button_visible if current_selection else button_hidden


@callback(
    Output('search-input', 'value'),
    Input('reset-search-btn', 'n_clicks'),
    prevent_initial_call=True
)
def reset_search(n_clicks):
    return ''


@callback(
    Output('download-csv', 'data'),
    Input('export-btn', 'n_clicks'),
    State('year-range-slider', 'value'),
    State('search-input', 'value'),
    State('selected-subject-category', 'data'),
    State('selected-relief-category', 'data'),
    prevent_initial_call=True
)
def export_csv(n_clicks, year_range, search_value, selected_subject, selected_relief):
    start_year, end_year = year_range
    
    filtered_df = df[(df['year'] >= start_year) & (df['year'] <= end_year)].copy()
    
    if selected_subject:
        filtered_df = filtered_df[filtered_df['subject_category'].str.contains(selected_subject, na=False, regex=False)]
    if selected_relief:
        filtered_df = filtered_df[filtered_df['relief_category'].str.contains(selected_relief, na=False, regex=False)]
    
    if search_value:
        search_lower = search_value.lower()
        mask = (
            filtered_df['title'].str.lower().str.contains(search_lower, na=False) |
            filtered_df['date'].astype(str).str.contains(search_lower, na=False) |
            filtered_df['subject_category'].str.lower().str.contains(search_lower, na=False) |
            filtered_df['relief_category'].str.lower().str.contains(search_lower, na=False)
        )
        filtered_df = filtered_df[mask]
    
    export_cols = ['congress', 'volume', 'chapter', 'title', 'date', 'year', 'subject_category', 'relief_category', 'summary', 'pdf_link', 'details_link']
    export_df = filtered_df[[c for c in export_cols if c in filtered_df.columns]]
    
    return dcc.send_data_frame(export_df.to_csv, f"private_laws_{start_year}_{end_year}.csv", index=False)


# =============================================================================
# RUN SERVER
# =============================================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("  Private Law Database Dashboard v3")
    print("="*60)
    print(f"\n  ✓ Loaded {len(df):,} records")
    print(f"  ✓ Year range: {df['year'].min()} - {df['year'].max()}")
    print("\n  Open your browser to: http://127.0.0.1:8050")
    print("\n  Press Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    app.run(debug=True, port=8050)