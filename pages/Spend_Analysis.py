
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

st.sidebar.markdown("""
    <style>
        .sidebar .sidebar-content {
            padding-left: 1rem !important;
        }
    </style>
    """, unsafe_allow_html=True)


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
                    padding-left: 3rem;
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
df3_mean = filtered_df.groupby(['customer_id', 'age_group', 'city', 'occupation', 'gender',
       'marital status', 'avg_income', 'avg_spend', 'category',
       'payment_type'])['spend'].mean().reset_index().round(0)
category_df = df3_mean.groupby(['customer_id', 'category'])['spend'].sum().reset_index().groupby('category')['spend'].mean().reset_index().round(0)#.sort_values(by='spend', ascending = False)
max_values_category = category_df.nlargest(3,'spend')
colors_category = ['#b20710' if value in max_values_category['spend'].values else '#f5f5f1' for value in category_df['spend']]

cmap = ['#221f1f', '#b20710', '#e50914', '#f5f5f1']

col1, col2 = st.columns([0.5,0.5])

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
        margin=dict(t=20, r=0, b=100),
        legend=dict(
            orientation='h',
            x=0.19,
            y=1.11),
    )

    category_fig = go.Figure(
    go.Bar(x=category_df['spend'],
           y=category_df['category'],
           orientation = 'h',
           marker_color = colors_category,
           marker_line_color = '#221f1f',
           text = category_df['spend'],
           texttemplate = '%{text}',
           textposition="inside",
          )
    )

    category_fig.update_layout(margin= dict(t=35, b=100),xaxis_title='Percentage')
    category_fig.update_xaxes(range=[0,6000])
    
    tab1, tab2 = st.tabs(["Average category spend", " Category spend by payment mode"])

    with tab1:
        st.plotly_chart(category_fig, use_container_width=True)

    with tab2:
        st.plotly_chart(fig_percentage_stacked, use_container_width=True)

with col2:
    
    median_avg_spend = filtered_df.groupby(['category', 'payment_type'])['spend'].median().reset_index()

    fig_scatter = px.scatter(
        median_avg_spend,
        y='category',
        x='payment_type',
        size='spend',
        color_discrete_sequence=['#e50914'],  # Set the color to white
        labels={'category': '', 'payment_type': '', 'spend': 'Median<br>Avg<br>Spend'},
    )

    fig_scatter.update_layout(title = '<br>   Average Category Spend <br>',
        margin=dict(t=100),
    )
    
    st.plotly_chart(fig_scatter, use_container_width=True)

col3, col4 = st.columns([0.5, 0.5])

with col3:
    
    payment_type_df = filtered_df.groupby(['customer_id', 'age_group', 'city', 'occupation', 'gender',
           'marital status', 'avg_income', 'category', 'payment_type']).agg({'spend':'median', 
            'avg_spend':'max', 'avg_inc_utl':'max'}).reset_index().groupby(['customer_id', 'age_group', 'city', 'occupation', 'gender',
           'marital status', 'avg_income', 'payment_type']).agg({'spend':'sum','avg_spend':'max', 'avg_inc_utl':'max'}).reset_index()
    credit_spend_df = payment_type_df[payment_type_df['payment_type'] == 'Credit Card'].copy()
    credit_spend_df['credit_utl'] = (credit_spend_df['spend']*100 / credit_spend_df['avg_spend']).round(2)
    

    quad_fig = go.Figure(data=go.Scatter(x = credit_spend_df['avg_inc_utl'], y=credit_spend_df['avg_spend'], mode = 'markers', marker = dict(size = 3, color = 'white')))

    quad_fig.update_layout(autosize = False)

    high_spend_points = credit_spend_df[
        (credit_spend_df['avg_spend'] > 22000) &
        (credit_spend_df['avg_inc_utl'] > 37)
    ]

    # Calculate the percentage of markers captured
    percentage_captured = len(high_spend_points) / len(credit_spend_df) * 100

    # Add Annotation Box
    quad_fig.add_shape(
        type='rect',
        x0=35,
        x1=75.05,
        y0=22000,
        y1=52600,
        line=dict(color='red'),
        fillcolor='rgba(255, 0, 0, 0)'
    )

    # Add Text above Annotation
    quad_fig.add_annotation(
        x=40 + 5,
        y=50000 + 50,
        text=f'{percentage_captured:.2f}%',
        showarrow=False,
        font=dict(size=15, color= 'white'),
    )
    quad_fig.update_layout(margin=dict(t=25),
                           title='<b>Income Utilisation & Average Spend<b>',
                           xaxis_title='Income Utilisation %',
                           yaxis_title='Average Spend',
                           )
    quad_fig.update_xaxes(range=[0, 80])
    quad_fig.update_yaxes(range=[0, 55000])
    st.plotly_chart(quad_fig, use_container_width=True)

with col4:
    
    quad_fig2 = go.Figure(data=go.Scatter(x = credit_spend_df['credit_utl'], y=credit_spend_df['avg_income'], mode = 'markers', marker = dict(size = 3, color = 'white')))

    quad_fig2.update_layout(autosize = False)

    high_spend_points2 = credit_spend_df[
        (credit_spend_df['avg_income'] > 50000) &
        (credit_spend_df['credit_utl'] > 35)
    ]

    # Calculate the percentage of markers captured
    percentage_captured2 = len(high_spend_points2) / len(credit_spend_df) * 100

    # Add Annotation Box
    quad_fig2.add_shape(
        type='rect',
        x0=35,
        x1=50.50,
        y0=50000,
        y1=86600,
        line=dict(color='red'),
        fillcolor='rgba(255, 0, 0, 0)'
    )

    # Add Text above Annotation
    quad_fig2.add_annotation(
        x=37 + 5,
        y=82000,
        text=f'{percentage_captured2:.2f}%',
        showarrow=False,
        font=dict(size=15, color= 'white'),
    )
    quad_fig2.update_layout(margin=dict(t=25, l=100),
                           title='<b>Credit Utilisation & Average Income<b>',
                           xaxis_title='Credit Utilisation %',
                           yaxis_title='Average Income',
                           )    
    quad_fig2.update_xaxes(range=[20,55])
    quad_fig2.update_yaxes(range=[0, 90000])

    st.plotly_chart(quad_fig2, use_container_width=True)
