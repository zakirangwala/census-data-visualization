import dash
from dash import html, dcc, callback, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path

# Load the processed data
data_dir = Path(__file__).parent / "data"
processed_data = pd.read_pickle(data_dir / "processed" / "processed_data.pkl")

# Initialize the Dash app
app = dash.Dash(__name__)

# App layout
app.layout = html.Div([
    html.H1("Census Data Interactive Dashboard", className="header-title"),

    # Tabs for different visualizations
    dcc.Tabs([
        # Tab 1: Essential Services Distribution
        dcc.Tab(label="Essential Services", children=[
            html.Div([
                html.H3("Distribution of Essential Services Across Canada"),
                dcc.RadioItems(
                    id='service-type',
                    options=[
                        {'label': 'All Services', 'value': 'all'},
                        {'label': 'Nurses', 'value': 'Nurses'},
                        {'label': 'Police Officers', 'value': 'Police Officers'},
                        {'label': 'Firefighters', 'value': 'Firefighters'}
                    ],
                    value='all',
                    inline=True
                ),
                html.Div([
                    dcc.Graph(id='essential-services-graph'),
                    html.Div(id='service-stats', style={'margin-top': '20px'})
                ])
            ])
        ]),

        # Tab 2: Employment by Gender
        dcc.Tab(label="Employment by Gender", children=[
            html.Div([
                html.H3("Employment Statistics by Gender and NOC Groups"),
                dcc.Dropdown(
                    id='noc-category',
                    options=[{'label': cat, 'value': cat}
                             for cat in processed_data['noc_categories']['occupation'].unique()],
                    value=processed_data['noc_categories']['occupation'].iloc[0]
                ),
                dcc.Graph(id='gender-employment-graph')
            ])
        ]),

        # Tab 3: Engineering Manpower
        dcc.Tab(label="Engineering Manpower", children=[
            html.Div([
                html.H3("Engineering Manpower Analysis"),
                dcc.Dropdown(
                    id='engineering-type',
                    options=[
                        {'label': 'Computer Engineers', 'value': 'Computer'},
                        {'label': 'Mechanical Engineers', 'value': 'Mechanical'},
                        {'label': 'Electrical Engineers', 'value': 'Electrical'}
                    ],
                    value='Computer'
                ),
                dcc.Slider(
                    id='manpower-threshold',
                    min=0,
                    max=30000,
                    step=1000,
                    value=10000,
                    marks={i: f'{i:,}' for i in range(0, 35000, 5000)}
                ),
                dcc.Graph(id='engineering-graph')
            ])
        ]),

        # Tab 4: Additional Insights
        dcc.Tab(label="Additional Insights", children=[
            html.Div([
                html.H3("Workforce Distribution Across Major Sectors"),
                dcc.Graph(id='additional-insights-graph')
            ])
        ])
    ])
])


@callback(
    [Output('essential-services-graph', 'figure'),
     Output('service-stats', 'children')],
    Input('service-type', 'value')
)
def update_essential_services(service_type):
    # Create a copy to avoid modifying original
    df = processed_data['essential_services'].copy()

    # Calculate percentages
    df['men_pct'] = (df['men'] / df['total'] * 100).round(1)
    df['women_pct'] = (df['women'] / df['total'] * 100).round(1)

    if service_type == 'all':
        # Create a stacked bar chart showing all services
        fig = go.Figure()

        # Add bars for men and women
        fig.add_trace(go.Bar(
            name='Men',
            x=df['service_type'],
            y=df['men'],
            marker_color='#2E86C1',
            text=[f"{pct:.1f}%" for pct in df['men_pct']],
            textposition='auto',
        ))

        fig.add_trace(go.Bar(
            name='Women',
            x=df['service_type'],
            y=df['women'],
            marker_color='#E74C3C',
            text=[f"{pct:.1f}%" for pct in df['women_pct']],
            textposition='auto',
        ))

        fig.update_layout(
            title='Distribution of Essential Service Workers by Gender',
            xaxis_title='Service Type',
            yaxis_title='Number of Workers',
            barmode='stack',
            showlegend=True,
            height=500
        )

        # Create summary statistics
        stats_html = html.Div([
            html.H4("Summary Statistics"),
            html.Table([
                html.Tr([
                    html.Th("Service Type"),
                    html.Th("Total Workers"),
                    html.Th("Men (%)"),
                    html.Th("Women (%)")
                ])
            ] + [
                html.Tr([
                    html.Td(row['service_type']),
                    html.Td(f"{row['total']:,.0f}"),
                    html.Td(f"{row['men_pct']:.1f}%"),
                    html.Td(f"{row['women_pct']:.1f}%")
                ]) for _, row in df.iterrows()
            ], style={
                'width': '100%',
                'border': '1px solid black',
                'border-collapse': 'collapse',
                'text-align': 'center'
            })
        ])

    else:
        # Filter for specific service
        df_filtered = df[df['service_type'] == service_type]

        # Create a detailed breakdown for the selected service
        fig = go.Figure()

        fig.add_trace(go.Bar(
            name='Men',
            x=['Men'],
            y=[df_filtered['men'].iloc[0]],
            marker_color='#2E86C1',
            text=f"{df_filtered['men_pct'].iloc[0]:.1f}%",
            textposition='auto',
        ))

        fig.add_trace(go.Bar(
            name='Women',
            x=['Women'],
            y=[df_filtered['women'].iloc[0]],
            marker_color='#E74C3C',
            text=f"{df_filtered['women_pct'].iloc[0]:.1f}%",
            textposition='auto',
        ))

        fig.update_layout(
            title=f'Gender Distribution in {service_type}',
            yaxis_title='Number of Workers',
            barmode='group',
            height=500
        )

        # Create detailed statistics for the selected service
        stats_html = html.Div([
            html.H4(f"Statistics for {service_type}"),
            html.P([
                f"Total Workers: {df_filtered['total'].iloc[0]:,.0f}",
                html.Br(),
                f"Men: {df_filtered['men'].iloc[0]:,.0f} ({df_filtered['men_pct'].iloc[0]:.1f}%)",
                html.Br(),
                f"Women: {df_filtered['women'].iloc[0]:,.0f} ({df_filtered['women_pct'].iloc[0]:.1f}%)"
            ])
        ])

    return fig, stats_html


@callback(
    Output('gender-employment-graph', 'figure'),
    Input('noc-category', 'value')
)
def update_gender_employment(category):
    df = processed_data['noc_categories']
    df_filtered = df[df['occupation'] == category]

    fig = go.Figure(data=[
        go.Bar(name='Men', x=['Men'], y=[df_filtered['men'].iloc[0]]),
        go.Bar(name='Women', x=['Women'], y=[df_filtered['women'].iloc[0]])
    ])

    fig.update_layout(
        title=f'Gender Distribution in {category}',
        yaxis_title='Number of Workers',
        barmode='group'
    )
    return fig


@callback(
    Output('engineering-graph', 'figure'),
    [Input('engineering-type', 'value'),
     Input('manpower-threshold', 'value')]
)
def update_engineering_graph(eng_type, threshold):
    df = processed_data['engineering']
    df_filtered = df[df['engineering_type'] == eng_type]

    fig = px.bar(
        df_filtered,
        x=['total', 'men', 'women'],
        y='occupation',
        orientation='h',
        title=f'{eng_type} Engineers Distribution',
        labels={'value': 'Number of Workers', 'occupation': 'Occupation'}
    )

    fig.add_vline(x=threshold, line_dash="dash", line_color="red",
                  annotation_text=f"Threshold: {threshold:,}")
    return fig


@callback(
    Output('additional-insights-graph', 'figure'),
    Input('additional-insights-graph', 'id')
)
def update_additional_insights(_):
    df = processed_data['noc_categories']

    fig = px.pie(
        df,
        values='total',
        names='occupation',
        title='Distribution of Workforce Across Major Sectors'
    )
    return fig


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
