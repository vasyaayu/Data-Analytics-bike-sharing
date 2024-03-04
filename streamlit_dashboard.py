import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st

# Set up the page
st.set_page_config(page_title="Bike-Sharing Performance Dashboard", page_icon=":bar_chart:", layout="wide")

# Load Dataset
df = pd.read_csv('https://raw.githubusercontent.com/vasyaayu/Data-Analytics-bike-sharing/a05db24b2ee4567b3256478d27ecffb4e6abc170/data/hour.csv')
dfn = pd.read_csv('https://raw.githubusercontent.com/vasyaayu/Data-Analytics-bike-sharing/6a99896ee87ad616fcfca33bd1d9d76a6e7d8f10/data/bsn.csv')
df['dteday'] = pd.to_datetime(df['dteday'], format='%Y-%m-%d')
dfn['dteday'] = pd.to_datetime(dfn['dteday'], format='%Y-%m-%d')

st.header('Bike-sharing Performance Dashboard :sparkles:')

col1, col2, col3 = st.columns(3)

with col1:
    total_registered = df.registered.sum()
    st.metric("Total Registered", value=total_registered)

with col2:
    total_casual = df.casual.sum()
    st.metric("Total Casual", value=total_casual)

with col3:
    total_count = df.cnt.sum()
    st.metric("Total Count", value=total_count)


# Create Helper Functions
def create_weekend_weekday_df(df):
    df['day_type'] = df['dteday'].dt.dayofweek.apply(lambda x: 'Weekend' if x >= 5 else 'Weekday')
    weekend_weekday_df = df.groupby(["dteday", "day_type"])["cnt"].sum().reset_index()
    return weekend_weekday_df

df_monthly = df.resample('M', on='dteday').sum()
weekend_weekday_df = create_weekend_weekday_df(df)

def create_seasonal_users_df(df):
    seasonal_users_df = df.groupby("season").agg({
        "casual": "sum",
        "registered": "sum"
    }).reset_index()
    seasonal_users_df = pd.melt(seasonal_users_df,
                                 id_vars=['season'],
                                 value_vars=['casual', 'registered'],
                                 var_name='user_type',
                                 value_name='count')
    seasonal_users_df['season'] = seasonal_users_df['season'].map({1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'})
    return seasonal_users_df

def create_daily_users_df(df):
    daily_users_df = df.groupby("dteday").agg({
        "cnt": "sum"
    }).reset_index()
    
    return daily_users_df

def create_temperature_users_df(dfn):
    cold_days = dfn[dfn['temp'] < 10]
    cool_days = dfn[(dfn['temp'] >= 10) & (dfn['temp'] < 20)]
    warm_days = dfn[(dfn['temp'] >= 20) & (dfn['temp'] < 30)]
    hot_days = dfn[dfn['temp'] >= 30]
    
    total_rides = [
        cold_days['cnt'].sum(),
        cool_days['cnt'].sum(),
        warm_days['cnt'].sum(),
        hot_days['cnt'].sum()
    ]
    
    temperature_conditions = ['Cold', 'Cool', 'Warm', 'Hot']
    
    temperature_users_df = pd.DataFrame({
        'Temperature Condition': temperature_conditions,
        'Total Rides': total_rides
    })
    
    return temperature_users_df

# ----- SIDEBAR -----
with st.sidebar:
    # add capital bikeshare logo
    st.image("https://raw.githubusercontent.com/vasyaayu/Data-Analytics-bike-sharing/26ca9770086e7212357bae9a95336b6d28d44e88/assets/bikeshare.jpg")
    st.sidebar.header("Filter:")
    
    min_date = df["dteday"].min().date()
    max_date = df["dteday"].max().date()

    # start_date & end_date from date_input
    start_date, end_date = st.date_input(
        label="Date Filter", min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    # Button to apply filters
    apply_button = st.button(label="Apply Filters")

# Preparing data for plot
main_df = df[
    (df["dteday"] >= pd.Timestamp(start_date)) &
    (df["dteday"] <= pd.Timestamp(end_date))
]

main_dfn = dfn[
    (dfn["dteday"] >= pd.Timestamp(start_date)) &
    (dfn["dteday"] <= pd.Timestamp(end_date))
]

# assign main_df to helper functions
weekend_weekday_df = create_weekend_weekday_df(main_df)
seasonal_users_df = create_seasonal_users_df(main_df)
daily_users_df = create_daily_users_df(main_df)
temperature_users_df = create_temperature_users_df(main_dfn)

# Plotting
if not weekend_weekday_df.empty:
    weekend_weekday_df['next_day'] = weekend_weekday_df['dteday'].shift(-1)
    weekend_weekday_df = weekend_weekday_df.dropna()
    weekend_weekday_df = weekend_weekday_df[weekend_weekday_df['dteday'].dt.month == weekend_weekday_df['next_day'].dt.month]

    fig3 = px.line(weekend_weekday_df,
              x='dteday',
              y='cnt',
              color='day_type',
              title='Count of Bikeshare Riders on Weekday and Weekend').update_layout(xaxis_title='', yaxis_title='Total Rides')

    st.plotly_chart(fig3, use_container_width=True)

if not seasonal_users_df.empty:
    fig = px.bar(seasonal_users_df, x='season', y='count', color='user_type',
                 barmode='group', title='Comparison of Casual and Registered Users by Season',
                 labels={'count': 'Total Rides'})
    st.plotly_chart(fig, use_container_width=True)

if 'daily_users_df' in locals():
    fig = px.line(daily_users_df, x='dteday', y='cnt',
              title='Overall Count of Bikeshare Riders', labels={'cnt': 'Total Rides', 'dteday': ''})
    st.plotly_chart(fig, use_container_width=True)

if 'temperature_users_df' in locals():
    color_map = {'Cold': 'blue', 'Cool': '#0568ff', 'Warm': '#CA3433', 'Hot': 'red'}
    fig = px.bar(temperature_users_df, x='Temperature Condition', y='Total Rides',
                 title='Count of Rides by Temperature Condition', labels={'Total Rides': 'Total Rides'},
                 color='Temperature Condition', color_discrete_map=color_map)
    st.plotly_chart(fig, use_container_width=True)
