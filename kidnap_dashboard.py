# Configure matplotlib before import
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import plotly.express as px
import streamlit as st
from datetime import datetime




# Set page config
st.set_page_config(
    page_title="Nigeria Kidnapping Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load data
@st.cache_data
def load_data():
    return pd.read_csv('kidnaps.csv')

df = load_data()

# Convert month numbers to names for better display
month_map = {
    1: 'January', 2: 'February', 3: 'March', 4: 'April',
    5: 'May', 6: 'June', 7: 'July', 8: 'August',
    9: 'September', 10: 'October', 11: 'November', 12: 'December'
}
df['month_name'] = df['month'].map(month_map)

# Sidebar filters
st.sidebar.title("Filters")
selected_years = st.sidebar.multiselect(
    "Select Years",
    options=sorted(df['year'].unique()),
    default=sorted(df['year'].unique())
)

selected_states = st.sidebar.multiselect(
    "Select States",
    options=sorted(df['state'].unique()),
    default=['FCT', 'KADUNA', 'ZAMFARA', 'KATSINA']
)

# Filter data based on selections
filtered_df = df[
    (df['year'].isin(selected_years)) & 
    (df['state'].isin(selected_states))
]

# Main dashboard
st.title("Nigeria Kidnapping Incidents Dashboard")
st.markdown("""
    Interactive analysis of kidnapping incidents across Nigerian states (2024-2025)
""")

# Key Metrics
st.header("Key Metrics")
col1, col2, col3, col4 = st.columns(4)
with col1:
    total_incidents = filtered_df['incidents'].sum()
    st.metric("Total Incidents", f"{total_incidents:,}")

with col2:
    total_victims = filtered_df['victims'].sum()
    st.metric("Total Victims", f"{total_victims:,}")

with col3:
    avg_victims_per_incident = round(total_victims / total_incidents, 1) if total_incidents > 0 else 0
    st.metric("Avg Victims per Incident", avg_victims_per_incident)

with col4:
    max_state = filtered_df.groupby('state')['incidents'].sum().idxmax()
    st.metric("Highest State", max_state)

# Time Series Analysis
st.header("Monthly Trends")
tab1, tab2, tab3 = st.tabs(["Incidents", "Victims", "Comparison"])

with tab1:
    fig = px.line(
        filtered_df.groupby(['year', 'month_name', 'month'])['incidents'].sum().reset_index(),
        x='month_name',
        y='incidents',
        color='year',
        title="Monthly Incidents by Year",
        labels={'incidents': 'Number of Incidents', 'month_name': 'Month'},
        category_orders={"month_name": list(month_map.values())}
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    fig = px.line(
        filtered_df.groupby(['year', 'month_name', 'month'])['victims'].sum().reset_index(),
        x='month_name',
        y='victims',
        color='year',
        title="Monthly Victims by Year",
        labels={'victims': 'Number of Victims', 'month_name': 'Month'},
        category_orders={"month_name": list(month_map.values())}
    )
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    fig = px.line(
        filtered_df.groupby(['year', 'month_name', 'month']).agg({
            'incidents': 'sum',
            'victims': 'sum'
        }).reset_index(),
        x='month_name',
        y=['incidents', 'victims'],
        color='year',
        title="Incidents vs Victims Comparison",
        labels={'value': 'Count', 'month_name': 'Month'},
        category_orders={"month_name": list(month_map.values())}
    )
    st.plotly_chart(fig, use_container_width=True)

# State Analysis
st.header("State-Level Analysis")
col1, col2 = st.columns(2)

with col1:
    state_incidents = filtered_df.groupby('state')['incidents'].sum().sort_values(ascending=False)
    fig = px.bar(
        state_incidents.reset_index(),
        x='state',
        y='incidents',
        title="Total Incidents by State",
        labels={'incidents': 'Number of Incidents', 'state': 'State'}
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    state_victims = filtered_df.groupby('state')['victims'].sum().sort_values(ascending=False)
    fig = px.bar(
        state_victims.reset_index(),
        x='state',
        y='victims',
        title="Total Victims by State",
        labels={'victims': 'Number of Victims', 'state': 'State'}
    )
    st.plotly_chart(fig, use_container_width=True)

# Heatmap of Incidents by Month and State
st.header("Incidents Heatmap")
heatmap_data = filtered_df.pivot_table(
    index='state',
    columns='month_name',
    values='incidents',
    aggfunc='sum'
)[list(month_map.values())]  # Ensure correct month order

fig, ax = plt.subplots(figsize=(12, 8))
sns.heatmap(
    heatmap_data,
    cmap='YlOrRd',
    annot=True,
    fmt='g',
    linewidths=.5,
    ax=ax
)
ax.set_title("Monthly Incidents by State")
st.pyplot(fig)

# State Comparison Over Time
st.header("State Comparison Over Time")
selected_comparison_states = st.multiselect(
    "Select states to compare:",
    options=sorted(df['state'].unique()),
    default=['KADUNA', 'ZAMFARA', 'KATSINA', 'FCT']
)

if selected_comparison_states:
    comparison_df = filtered_df[filtered_df['state'].isin(selected_comparison_states)]
    
    fig = px.line(
        comparison_df.groupby(['year', 'month_name', 'month', 'state'])['incidents'].sum().reset_index(),
        x='month_name',
        y='incidents',
        color='state',
        line_dash='year',
        title="State Comparison: Monthly Incidents",
        labels={'incidents': 'Number of Incidents', 'month_name': 'Month'},
        category_orders={"month_name": list(month_map.values())}
    )
    st.plotly_chart(fig, use_container_width=True)

# Data Table
st.header("Raw Data")
st.dataframe(filtered_df.sort_values(['year', 'month', 'state']))

# Download button
st.download_button(
    label="Download Filtered Data as CSV",
    data=filtered_df.to_csv(index=False),
    file_name=f"kidnapping_data_{datetime.now().strftime('%Y%m%d')}.csv",
    mime='text/csv'
)