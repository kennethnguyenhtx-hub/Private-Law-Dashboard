"""
Callback functions for Private Laws Dashboard
"""

import dash
from dash import dcc, html, callback, Input, Output, State, ctx
import plotly.graph_objects as go
import pandas as pd

from styles import (
    COLORS, section_header_style, label_style, value_style,
    button_hidden_style, button_visible_style
)
from config import SUBJECT_CATEGORIES, RELIEF_CATEGORIES
from data_loader import truncate_label, count_categories, get_ordinal_suffix


def register_callbacks(app, df):
    """Register all callbacks with the app instance."""
    
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
        """Update info panel when a row is clicked."""
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
        
        row_on_page = active_cell['row']
        actual_row_idx = (page_current * page_size) + row_on_page
        data_source = virtual_data if virtual_data else table_data
        
        if not data_source or actual_row_idx >= len(data_source):
            return None, default_header_style, default_content
        
        row_data = data_source[actual_row_idx]
        law_id = row_data['id']
        
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
        
        info_content = html.Div([
            html.Div([
                html.Span("Title", style=label_style()),
                html.Div(full_record['title'], style={**value_style(), 'fontSize': '16px', 'lineHeight': '1.4'})
            ], style={'marginBottom': '20px'}),
            
            html.Div([
                html.Div([
                    html.Span("Congress", style=label_style()),
                    html.Div(congress_display, style=value_style())
                ], style={'display': 'inline-block', 'width': '30%'}),
                html.Div([
                    html.Span("Volume", style=label_style()),
                    html.Div(str(full_record['volume']), style=value_style())
                ], style={'display': 'inline-block', 'width': '30%'}),
                html.Div([
                    html.Span("Chapter", style=label_style()),
                    html.Div(str(full_record['chapter']), style=value_style())
                ], style={'display': 'inline-block', 'width': '30%'})
            ], style={'marginBottom': '20px'}),
            
            html.Div([
                html.Span("Date Enacted", style=label_style()),
                html.Div(date_display, style=value_style())
            ], style={'marginBottom': '20px'}),
            
            html.Div([
                html.Span("Subject Matter Category", style=label_style()),
                html.Div(full_record['subject_category'] or "Not categorized", style={
                    **value_style(),
                    'color': COLORS['accent_primary'] if full_record['subject_category'] else COLORS['text_muted']
                })
            ], style={'marginBottom': '20px'}),
            
            html.Div([
                html.Span("Relief Category", style=label_style()),
                html.Div(full_record['relief_category'] or "Not categorized", style={
                    **value_style(),
                    'color': COLORS['accent_primary'] if full_record['relief_category'] else COLORS['text_muted']
                })
            ], style={'marginBottom': '20px'}),
            
            html.Div([
                html.Span("Summary", style=label_style()),
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
        
        # Reset button clicked
        if triggered == 'reset-subject-filter-btn':
            return None, button_hidden_style()
        
        # Chart clicked
        if triggered == 'subject-breakdown-chart' and click_data:
            clicked_category = click_data['points'][0].get('customdata', click_data['points'][0]['y'])
            if clicked_category == current_selection:
                return None, button_hidden_style()
            return clicked_category, button_visible_style()
        
        # Checkbox clicked
        if isinstance(triggered, dict) and triggered.get('type') == 'subject-checkbox':
            clicked_category = triggered['index']
            for val in checkbox_values:
                if val and clicked_category in val:
                    if clicked_category == current_selection:
                        return None, button_hidden_style()
                    return clicked_category, button_visible_style()
            if clicked_category == current_selection:
                return None, button_hidden_style()
        
        return current_selection, button_visible_style() if current_selection else button_hidden_style()

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
        
        if triggered == 'reset-relief-filter-btn':
            return None, button_hidden_style()
        
        if triggered == 'relief-breakdown-chart' and click_data:
            clicked_category = click_data['points'][0].get('customdata', click_data['points'][0]['y'])
            if clicked_category == current_selection:
                return None, button_hidden_style()
            return clicked_category, button_visible_style()
        
        if isinstance(triggered, dict) and triggered.get('type') == 'relief-checkbox':
            clicked_category = triggered['index']
            for val in checkbox_values:
                if val and clicked_category in val:
                    if clicked_category == current_selection:
                        return None, button_hidden_style()
                    return clicked_category, button_visible_style()
            if clicked_category == current_selection:
                return None, button_hidden_style()
        
        return current_selection, button_visible_style() if current_selection else button_hidden_style()

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
