import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit_antd_components as sac
from plotly.subplots import make_subplots
import tarfile


def filtering_function(filtered_df, occupation_f, age_group_f, income_group_f, city_f):
    # global filtered_df
    if not occupation_f and not age_group_f and not income_group_f and not city_f:
         return df1.copy()
    else:
        if occupation_f:
            filtered_df = filtered_df[filtered_df['occupation'].isin(occupation_f)]
        if age_group_f:
            filtered_df = filtered_df[filtered_df['age_group'].isin(age_group_f)]
        if income_group_f:
            filtered_df = filtered_df[filtered_df['income_group'].isin(income_group_f)]
        if city_f:
            filtered_df = filtered_df[filtered_df['city'].isin(city_f)]
    return filtered_df

tar_gz_file_path = "fact_spends.tar.gz"
csv_file_name = "fact_spends.csv"
with tarfile.open(tar_gz_file_path, 'r:gz') as tar:
    tar.extract(csv_file_name)

df2 = pd.read_csv(csv_file_name)
df1 = pd.read_csv('dim_customers.csv')
st.set_page_config(page_title='Income Analysis', layout='wide')
st.sidebar.markdown("""
        <style>
               .block-container {
                    padding-top: 1rem;
                }
        </style>
        """, unsafe_allow_html=True)


# Calculate average spend by category and payment gateway
avg_spend_by_category_gateway = df2.groupby(['category', 'payment_type'])['spend'].median().reset_index()

# Calculate the total spend for each category to calculate percentages
total_spend_by_category = avg_spend_by_category_gateway.groupby('category')['spend'].sum().reset_index()

# Merge with the average spend DataFrame to calculate percentages
avg_spend_by_category_gateway = pd.merge(avg_spend_by_category_gateway, total_spend_by_category,
                                         on='category', suffixes=('_avg', '_total'))

# Calculate percentage of average spend for each category and payment gateway
avg_spend_by_category_gateway['percentage'] = (avg_spend_by_category_gateway['spend_avg'] /
                                               avg_spend_by_category_gateway['spend_total']) * 100

# Define the color order for payment types
payment_type_order = df2['payment_type'].unique()

# Create a percentage stacked horizontal bar graph using go.Figure
fig_percentage_stacked = go.Figure()

for payment_type in payment_type_order:
    data_subset = avg_spend_by_category_gateway[avg_spend_by_category_gateway['payment_type'] == payment_type]

    fig_percentage_stacked.add_trace(
        go.Bar(
            x=data_subset['percentage'],
            y=data_subset['category'],
            orientation='h',
            name=payment_type,
            text=data_subset['percentage'].round(2).astype(str) + '%',  # Text for the percentage
            textposition='inside',  # Place text inside the bars
            marker_color=cmap[payment_type_order.tolist().index(payment_type)],

        )
    )

    # Update layout
    fig_percentage_stacked.update_layout(
        xaxis_title='Percentage',
        barmode='stack',
        autosize=True,
        margin=dict(t=40, b=20)
    )
    st.plotly_chart(fig_percentage_stacked , user_container_width = True)
