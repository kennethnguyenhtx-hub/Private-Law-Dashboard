"""
Layout components for Private Laws Dashboard
"""

from dash import dcc, html, dash_table
from styles import COLORS, section_header_style, subsection_header_style, card_style, gradient_divider


def create_layout():
    """Create the main dashboard layout."""
    return html.Div([
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
                # Timeline Panel
                _create_timeline_panel(),
                # List of Private Laws Panel
                _create_laws_list_panel()
            ], style={'width': '60%', 'paddingRight': '20px'}),
            
            # RIGHT COLUMN (40%) - Breakdown + Private Law Information
            html.Div([
                # Breakdown Panel
                _create_breakdown_panel(),
                # Private Law Information Panel
                _create_info_panel()
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


def _create_timeline_panel():
    """Create the timeline panel with filter controls."""
    return html.Div([
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
    ], style={**card_style(), 'marginBottom': '20px', 'minHeight': '420px'})


def _create_laws_list_panel():
    """Create the laws list panel with search and table."""
    return html.Div([
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


def _create_breakdown_panel():
    """Create the breakdown panel with subject and relief categories."""
    return html.Div([
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
    ], style={**card_style(), 'marginBottom': '20px', 'minHeight': '420px'})


def _create_info_panel():
    """Create the private law information panel."""
    return html.Div([
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
