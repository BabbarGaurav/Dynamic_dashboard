import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit_antd_components as sac
import tarfile


def filtering_function(filtered_df, occupation_f, age_group_f, income_group_f, city_f):
    # global filtered_df
    if not occupation_f and not age_group_f and not income_group_f and not city_f:
        return df3.copy()
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

df1 = pd.read_csv('dim_customers.csv')
df2 = pd.read_csv(csv_file_name)
df3 = pd.merge(df1, df2, on='customer_id', how='inner')
spends_df = df3.groupby(['customer_id', 'category', 'payment_type'])['spend'].median().reset_index().groupby('customer_id')['spend'].sum().reset_index(name='avg_spend')
df3 = pd.merge(df3, spends_df, on = 'customer_id', how = 'inner')
df3['avg_inc_utl'] = (df3['avg_spend']/df3['avg_income']*100).round(2)
bins = list(range(20000, 100000, 10000))
labels = ['20k-30k', '30k-40k', '40k-50k', '50k-60k', '60k-70k', '70k-80k', '80k-90k']
df3['income_group'] = pd.cut(df3['avg_income'], bins=bins, labels=labels, right=False)

st.set_page_config(page_title='Spend Analysis', layout='wide')
st.sidebar.header('Choose your filters: ')

with st.sidebar:
    occupation_f = sac.chip(label='Pick the occupation', items=dict.fromkeys(df3['occupation'].unique()), size='xs',
                            align='start', multiple=True, direction='horizontal')

    age_group_f = sac.chip(label='Pick the age group', items=dict.fromkeys(df3['age_group'].unique()), size='xs',
                           align='start', multiple=True, direction='horizontal')

    income_group_f = sac.chip(label='Pick the Income group', items=dict.fromkeys(df3['income_group'].unique()),
                              size='xs', align='start', multiple=True, direction='horizontal')

st.markdown("""
        <style>
               .block-container {
                    padding-top: 2rem;
                    padding-right: 2rem;
                }
        </style>
        """, unsafe_allow_html=True)
city_f = sac.chip(items=dict.fromkeys(df1['city'].unique()), radius='xs', size='sm', align='start', multiple=True,
                  variant='light', direction='horizontal')

filtered_df = df3.copy()

filtered_df = filtering_function(filtered_df, occupation_f, age_group_f, income_group_f, city_f)

# Calculate average spend by category and payment gateway
avg_spend_by_category_gateway = filtered_df.groupby(['category', 'payment_type'])['spend'].median().reset_index()

# Calculate the total spend for each category to calculate percentages
total_spend_by_category = avg_spend_by_category_gateway.groupby('category')['spend'].sum().reset_index()

# Merge with the average spend DataFrame to calculate percentages
avg_spend_by_category_gateway = pd.merge(avg_spend_by_category_gateway, total_spend_by_category,
                                         on='category', suffixes=('_avg', '_total'))

# Calculate percentage of average spend for each category and payment gateway
avg_spend_by_category_gateway['percentage'] = (avg_spend_by_category_gateway['spend_avg'] /
                                               avg_spend_by_category_gateway['spend_total']) * 100

# Define the color order for payment types
payment_type_order = df3['payment_type'].unique()

cmap = ['#221f1f', '#b20710', '#e50914', '#f5f5f1']

col1,_ = st.columns([1, 0.1])

with col1:
    fig_percentage_stacked = go.Figure()

    for payment_type in payment_type_order:
        data_subset = avg_spend_by_category_gateway[avg_spend_by_category_gateway['payment_type'] == payment_type]

        fig_percentage_stacked.add_trace(
            go.Bar(
                x=data_subset['percentage'],
                y=data_subset['category'],
                orientation='h',
                name=payment_type,
                text=data_subset['percentage'].round(2).astype(str) + '%',
                textposition='inside',
                marker_color=cmap[payment_type_order.tolist().index(payment_type)],
            )
        )

    # Update layout
    fig_percentage_stacked.update_layout(
        xaxis_title='Percentage',
        barmode='stack',
        margin=dict(t=20),
        legend=dict(
            orientation='h',
            x=0.29,
            y=1.15),
    )

    median_avg_spend = filtered_df.groupby(['category', 'payment_type'])['spend'].median().reset_index()

    fig_scatter = px.scatter(
        median_avg_spend,
        y='category',
        x='payment_type',
        size='spend',
        color_discrete_sequence=['white'],  # Set the color to white
        labels={'category': '', 'payment_type': '', 'spend': 'Median<br>Avg<br>Spend'},
    )

    fig_scatter.update_layout(
        margin=dict(t=20),
    )

    tab1, tab2 = st.tabs(["Percentage Spend on Category by payment mode", " Absolute Spend on Category by payment mode"])

    with tab1:
        st.plotly_chart(fig_percentage_stacked, use_container_width=True)

    with tab2:
        st.plotly_chart(fig_scatter, use_container_width=True)


col2,_ = st.columns([1,0.1])

with col2:
    payment_type_df = filtered_df.groupby(['customer_id', 'category', 'payment_type']).agg(
        {'spend': 'median', 'avg_spend': 'max', 'avg_inc_utl': 'max'}).reset_index().groupby(
        ['customer_id', 'payment_type']).agg({'spend': 'sum', 'avg_spend': 'max', 'avg_inc_utl': 'max'}).reset_index()
    credit_spend_df = payment_type_df[payment_type_df['payment_type'] == 'Credit Card'].copy()
    credit_spend_df['credit_utl'] = (credit_spend_df['spend'] * 100 / credit_spend_df['avg_spend']).round(2)

    quad_fig = go.Figure(data=go.Scatter(x=credit_spend_df['avg_inc_utl'], y=credit_spend_df['credit_utl'], mode='markers',
                                         marker=dict(size=3, color='#f5f5f1')))

    quad_fig.update_layout(margin=dict(t=40),
                           title='<b>Income Utilisation & Credit Utilisation Spread<b>',
                           xaxis_title='Income Utilisation %',
                           yaxis_title='Credit Utilisation %',
                           )
    quad_fig.update_xaxes(range=[15, 80])
    quad_fig.update_yaxes(range=[20, 55])

    st.plotly_chart(quad_fig, use_container_width=True)
