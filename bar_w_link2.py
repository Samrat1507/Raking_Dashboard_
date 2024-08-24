import gspread
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import base64

# Google Sheets API setup
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name(r'C:\Users\KIIT\Desktop\Raking_Dashboard\dashboard-432911-740fa73ea89c.json', scope)
client = gspread.authorize(creds)

# Fetching data from Google Sheets
spreadsheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1RkARFZeSAL79kjdE9muNTdZZkf4xsVmQW3geUV_rqsQ/edit?gid=0#gid=0")
sheet = spreadsheet.get_worksheet(0)
data = pd.DataFrame(sheet.get_all_records())

# Filter data based on required columns
columns = ["KEYWORD", "Belongs to", "Rank - 19th Aug", "Rank - 14th Aug", "Rank - 13th Aug", "Rank - 12th Aug", "Rank - 5th Aug", "Rank - 22nd July"]
filtered_data = data[columns]

# Streamlit app layout
st.title("Keyword Rankings Dashboard")

selected_category = st.selectbox("Select a Category", options=filtered_data['Belongs to'].unique())
search_query = st.text_input("Search keywords...")
graph_type = st.selectbox("Select Graph Type", options=['Bar', 'Line', 'Scatter'])

data_to_use = filtered_data.copy()

if search_query:
    data_to_use = data_to_use[data_to_use['KEYWORD'].str.contains(search_query, case=False)]

if selected_category:
    data_to_use = data_to_use[data_to_use['Belongs to'] == selected_category]

st.markdown(f"### Rankings for {selected_category or 'All Categories'}")

fig = go.Figure()
dates = ["Rank - 19th Aug", "Rank - 14th Aug", "Rank - 13th Aug", "Rank - 12th Aug", "Rank - 5th Aug", "Rank - 22nd July"]
colors = px.colors.sequential.Viridis

for i, date in enumerate(dates):
    if graph_type == 'Bar':
        fig.add_trace(go.Bar(
            x=data_to_use['KEYWORD'],
            y=data_to_use[date],
            name=date,
            marker=dict(color=colors[i], opacity=1 - i * 0.2)
        ))
    elif graph_type == 'Line':
        fig.add_trace(go.Scatter(
            x=data_to_use['KEYWORD'],
            y=data_to_use[date],
            mode='lines+markers',
            name=date,
            line=dict(color=colors[i])
        ))
    elif graph_type == 'Scatter':
        fig.add_trace(go.Scatter(
            x=data_to_use['KEYWORD'],
            y=data_to_use[date],
            mode='markers',
            name=date,
            marker=dict(color=colors[i])
        ))

fig.update_layout(
    barmode='stack' if graph_type == 'Bar' else 'overlay',
    yaxis=dict(title='Rank'),
    plot_bgcolor='white',
    paper_bgcolor='white',
    template='plotly_white',
    height=600,  # Increase the size of the graph
    width=1000
)

st.plotly_chart(fig)

# Detailed view dropdown
selected_keyword = st.selectbox("Select a Keyword for Detailed View", options=data_to_use['KEYWORD'].unique())

if selected_keyword:
    detailed_data = data_to_use[data_to_use['KEYWORD'] == selected_keyword]

    detailed_fig = go.Figure()

    for i, date in enumerate(dates):
        detailed_fig.add_trace(go.Bar(
            x=[date],
            y=detailed_data[date],
            name=date,
            marker=dict(color=colors[i])
        ))

    detailed_fig.update_layout(
        barmode='group',
        title=f'Detailed Rankings for {selected_keyword}',
        yaxis=dict(title='Rank'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        template='plotly_white',
        height=400,
        width=600
    )

    st.plotly_chart(detailed_fig)

if st.button("Export to CSV"):
    csv = data_to_use.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="filtered_data.csv">Download CSV</a>'
    st.markdown(href, unsafe_allow_html=True)
