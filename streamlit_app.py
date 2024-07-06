import streamlit as st

import os
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Define the folder containing the datasets
folder = "/Users/limjiajing/Library/CloudStorage/GoogleDrive-34944909m@gmail.com/My Drive/ICT305 Virtualisation/Assignment 2/HDB Dataset"

# Update file paths to include the folder
file_paths = {
    "1": os.path.join(folder, "1-LocationData.csv"),
    "2": os.path.join(folder, "2-LocationData.csv"),
    "3": os.path.join(folder, "3-LocationData.csv"),
    "4": os.path.join(folder, "4-LocationData.csv"),
    "5": os.path.join(folder, "5-LocationData.csv")
}

# Verify file existence and load data
dataframes = {}
for year, path in file_paths.items():
    absolute_path = os.path.abspath(path)
    print(f"Checking file: {absolute_path}")
    if os.path.exists(absolute_path):
        dataframes[year] = pd.read_csv(absolute_path)
    else:
        print(f"File not found: {absolute_path}")

# Concatenate dataframes and perform initial cleaning
if dataframes:
    df = pd.concat(dataframes.values(), ignore_index=True)
    df = df.dropna()
    df['month'] = pd.to_datetime(df['month'])
else:
    print("No data available to load.")
    df = pd.DataFrame(columns=['month', 'resale_price', 'latitude', 'longitude', 'flat_type', 'town', 'floor_area_sqm', 'lease_commence_date', 'storey_range', 'closest_mrt_dist'])

# Calculate 'hdb_age' based on the current year and 'lease_commence_date'
current_year = pd.to_datetime('now').year
df['hdb_age'] = current_year - df['lease_commence_date']

# Convert 'storey_range' to a numerical feature, e.g., '01 TO 03' -> 2 (average storey)
df['storey_avg'] = df['storey_range'].str.extract('(\d+ TO \d+)')[0].apply(
    lambda x: (int(x.split(' TO ')[0]) + int(x.split(' TO ')[1])) / 2 if pd.notnull(x) else None
)

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout of the Dash app
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Resale Flat Prices Dashboard", className="text-center mb-4"), width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.DatePickerRange(
                id='date-range',
                start_date=df['month'].min() if not df.empty else None,
                end_date=df['month'].max() if not df.empty else None,
                display_format='YYYY-MM-DD'
            )
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='price-trend')
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='resale-price-distribution')
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='average-resale-price')
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='resale-prices-by-flat-type')
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='resale-prices-by-town')
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='floor-area-vs-resale-price')
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='resale-price-vs-mrt-distance')
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='correlation-heatmap')
        ], width=12)
    ])
])

# Callback to update the price trend graph based on date range
@app.callback(
    Output('price-trend', 'figure'),
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_graph(start_date, end_date):
    # Check if the dataframe is empty
    if df.empty:
        return px.line(title='No data available')
    # Filter the dataframe based on the selected date range
    filtered_df = df[(df['month'] >= start_date) & (df['month'] <= end_date)]
    # Create the line plot
    fig = px.line(filtered_df, x='month', y='resale_price', title='Price Trend Over Time')
    return fig

# Callback to update the resale price distribution histogram based on date range
@app.callback(
    Output('resale-price-distribution', 'figure'),
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_resale_price_distribution(start_date, end_date):
    # Check if the dataframe is empty
    if df.empty:
        return px.histogram(title='No data available')
    # Filter the dataframe based on the selected date range
    filtered_df = df[(df['month'] >= start_date) & (df['month'] <= end_date)]
    # Create the histogram
    fig = px.histogram(filtered_df, x='resale_price', nbins=50, title='Distribution of Resale Prices', marginal='box')
    return fig

# Callback to update the average resale price line chart based on date range
@app.callback(
    Output('average-resale-price', 'figure'),
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_average_resale_price(start_date, end_date):
    # Check if the dataframe is empty
    if df.empty:
        return px.line(title='No data available')
    # Filter the dataframe based on the selected date range
    filtered_df = df[(df['month'] >= start_date) & (df['month'] <= end_date)]
    # Calculate the average resale price by month and flat type
    average_resale_price = filtered_df.groupby(['month', 'flat_type'])['resale_price'].mean().reset_index()
    # Create the line plot
    fig = px.line(average_resale_price, x='month', y='resale_price', color='flat_type', title='Average Resale Prices Over Time by Flat Type')
    return fig

# Callback to update the resale prices by flat type box plot based on date range
@app.callback(
    Output('resale-prices-by-flat-type', 'figure'),
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_resale_prices_by_flat_type(start_date, end_date):
    # Check if the dataframe is empty
    if df.empty:
        return px.box(title='No data available')
    # Filter the dataframe based on the selected date range
    filtered_df = df[(df['month'] >= start_date) & (df['month'] <= end_date)]
    # Create the box plot
    fig = px.box(filtered_df, x='flat_type', y='resale_price', title='Resale Prices by Flat Type')
    return fig

# Callback to update the resale prices by town box plot based on date range
@app.callback(
    Output('resale-prices-by-town', 'figure'),
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_resale_prices_by_town(start_date, end_date):
    # Check if the dataframe is empty
    if df.empty:
        return px.box(title='No data available')
    # Filter the dataframe based on the selected date range
    filtered_df = df[(df['month'] >= start_date) & (df['month'] <= end_date)]
    # Create the box plot
    fig = px.box(filtered_df, x='town', y='resale_price', title='Resale Prices by Town')
    fig.update_xaxes(tickangle=45)
    return fig

# Callback to update the floor area vs resale price scatter plot based on date range
@app.callback(
    Output('floor-area-vs-resale-price', 'figure'),
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_floor_area_vs_resale_price(start_date, end_date):
    # Check if the dataframe is empty
    if df.empty:
        return px.scatter(title='No data available')
    # Filter the dataframe based on the selected date range
    filtered_df = df[(df['month'] >= start_date) & (df['month'] <= end_date)]
    # Create the scatter plot
    fig = px.scatter(filtered_df, x='floor_area_sqm', y='resale_price', color='flat_type', title='Floor Area vs Resale Price by Flat Type')
    return fig

# Callback to update the resale price vs MRT distance scatter plot based on date range
@app.callback(
    Output('resale-price-vs-mrt-distance', 'figure'),
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_resale_price_vs_mrt_distance(start_date, end_date):
    # Check if the dataframe is empty
    if df.empty:
        return px.scatter(title='No data available')
    # Filter the dataframe based on the selected date range
    filtered_df = df[(df['month'] >= start_date) & (df['month'] <= end_date)]
    # Create the scatter plot
    fig = px.scatter(filtered_df, x='closest_mrt_dist', y='resale_price', title='Resale Price vs Distance to Nearest MRT', labels={'resale_price':'Resale Price (SGD)'})
    return fig

# Callback to update the correlation heatmap based on date range
@app.callback(
    Output('correlation-heatmap', 'figure'),
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_correlation_heatmap(start_date, end_date):
    # Check if the dataframe is empty
    if df.empty:
        return px.imshow([[0]], title='No data available')
    # Filter the dataframe based on the selected date range
    filtered_df = df[(df['month'] >= start_date) & (df['month'] <= end_date)]
    # Select numeric columns and calculate correlation matrix
    numeric_df = filtered_df.select_dtypes(include='number')
    corr = numeric_df.corr()
    # Create the heatmap
    fig = px.imshow(corr, text_auto=True, aspect='auto', title='Correlation Heatmap')
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

