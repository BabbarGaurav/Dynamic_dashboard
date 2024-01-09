
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
spends_df = df2.groupby(['customer_id', 'month']).sum().groupby('customer_id').agg({'spend': 'median'}).reset_index()
bins = list(range(20000, 100000, 10000))
labels = ['20k-30k', '30k-40k', '40k-50k', '50k-60k', '60k-70k', '70k-80k', '80k-90k']
df1['income_group']= pd.cut(df1['avg_income'], bins= bins, labels=labels, right=False)

# filtered_df = pd.merge(filtered_df, spends_df, on = 'customer_id', how = 'inner')

logo = 'https://avatars.githubusercontent.com/u/65004296?s=200&v=4'
st.set_page_config(page_title='Income Analysis', layout='wide')
st.sidebar.header('Choose your filters: ')
st.sidebar.markdown("""
        <style>
               .block-container {
                    padding-top: 1rem;
                }
        </style>
        """, unsafe_allow_html=True)

#occupation_f = st.sidebar.multiselect('Pick the occupation', df1['occupation'].unique())
with st.sidebar:
    occupation_f = sac.chip(label = 'Pick the occupation', items=dict.fromkeys(df1['occupation'].unique()), size='xs', align='start', multiple=True, direction = 'horizontal')
    
    age_group_f = sac.chip(label = 'Pick the age group', items=dict.fromkeys(df1['age_group'].unique()), size = 'xs', align = 'start', multiple = True, direction = 'horizontal')
       
    income_group_f = sac.chip(label = 'Pick the Income group', items=dict.fromkeys(df1['income_group'].unique()), size = 'xs', align = 'start', multiple = True, direction = 'horizontal')

st.markdown("""
        <style>
               .block-container {
                    padding-top: 2rem;
                    padding-left: 3rem;
                }
        </style>
        """, unsafe_allow_html=True)
city_f = sac.chip(items=dict.fromkeys(df1['city'].unique()), radius='xs', size='md', align='start', multiple=True, variant='light', direction='horizontal')

filtered_df = df1.copy()

filtered_df = filtering_function(filtered_df, occupation_f, age_group_f, income_group_f, city_f)

col1, col2 = st.columns((0.5,0.5))

with col1:

    # Gender & Marital Status Distribution

        cmap = ['#221f1f', '#b20710', '#e50914', '#f5f5f1']
        matrix = filtered_df[['marital status', 'gender']].value_counts(normalize=True).reset_index(name = 'perct').set_index(['marital status', 'gender']).unstack(fill_value=0).mul(100).round(2)
        matrix_fig = go.Figure(go.Heatmap(
            z=matrix.values,
            x=matrix.columns.levels[1],
            y=matrix.index,
            text=matrix.values,
            texttemplate= '<b>%{text}%</b>',
            hoverinfo="text",
            colorscale=cmap,
            textfont = dict(size=15),
        ))

        matrix_fig.update_xaxes(side= 'top', tickfont= dict(size= 16))
        matrix_fig.update_yaxes(tickfont= dict(size= 15))

        matrix_fig.update_layout(
            title='<b>Gender & Marital Status Distribution<b>',
            height = 200,
            width =600,
            margin = dict(l=20, b=20, t=100)
        )

        st.plotly_chart(matrix_fig, user_container_width = True)

    # Gender Distribution    
    
        gen = pd.DataFrame(filtered_df.groupby(['gender'])['gender'].size().apply(lambda x: (x*100)/len(filtered_df)).round(2)).T

        fig_gender = go.Figure()

        fig_gender.add_trace(
            go.Bar(
                x= gen['Female'],
                orientation = 'h',
                marker = dict(
                    color= '#b20710',
                    line_color = 'black'),
                text = [f"<b>Female: <br>{(gen['Female'][0])}%<b>"],
                textfont = dict(size=15),
                name='Female',
                insidetextanchor='middle',
        ))

        fig_gender.add_trace(
            go.Bar(
                x= gen['Male'],
                orientation = 'h',
                marker= dict(
                    color= '#221f1f',
                    line_color = 'black'),
                text= [f"<b>Male: <br>{(gen['Male'][0])}%<b>"],
                textfont = dict(size=15),
                name= 'Male',
                insidetextanchor='middle',
            ))


        fig_gender.update_xaxes(visible = False, range = [0,100])
        fig_gender.update_yaxes(visible = False)

        fig_gender.update_layout(barmode='stack',
                                 xaxis_title="Gender",
                                 showlegend = False,
                                 hovermode='closest',
                                 margin = dict(l=50, t=20, b= 30),
                                 #autosize = True,
                                 height = 125,
                                 width = 550
                                )
        st.plotly_chart(fig_gender, user_container_width = True)




with col2:
    
    #Occupation Distribution
    
        occupation_df = filtered_df["occupation"].value_counts(normalize=True).sort_index().mul(100).round(2)
        colors_occupation = ['#b20710' if occupation == max(occupation_df) else '#f5f5f1' for occupation in occupation_df]
        occupation_df_fig = make_subplots(rows=1, cols=2, column_widths=[0.5, 0.5], shared_yaxes=True, horizontal_spacing=.02)

        occupation_df_fig.add_trace(go.Bar(
            y = [val.replace(" ", "<br>") for val in occupation_df.index],
            x = occupation_df,
            marker_color = colors_occupation,
            marker_line_color = '#221f1f',
            text = occupation_df.values,
            texttemplate = '<b>%{text}%<b>',
            textposition="inside",
            cliponaxis=False,
            orientation='h'
            ), row=1, col=1
        )

        # Unique occupations in the DataFrame
        filtered_df["occupation_modified"] = filtered_df['occupation'].apply(lambda x: x.replace(" ", "<br>"))

        # Unique occupations in the DataFrame
        occupations = filtered_df['occupation_modified'].unique()

        # Loop through each occupation and add a Box trace
        for i, occupation in enumerate(occupations):
            occupation_df_fig.add_trace(go.Box(
                x=filtered_df[filtered_df['occupation_modified'] == occupation]['avg_income'],
                name=occupation,
                marker_color='#f5f5f1',
            ), row=1, col=2)

        # Add a vertical line at the median of 'avg_income'
        median_income = filtered_df['avg_income'].median()
        occupation_df_fig.add_vline(x=median_income, line_dash='dot',
                                    annotation_text=f'Median Income <br>{median_income}',
                                    annotation_position="top", line_color="#b20710")

        occupation_df_fig.update_layout(showlegend=False, title = '<b> Occupation Distribution <b>')
        occupation_df_fig.update_xaxes(range=[0,max(occupation_df)+5], row=1, col=1)
        occupation_df_fig.update_xaxes(range=[np.round(min(filtered_df['avg_income']), -4), np.round(max(filtered_df['avg_income']), -4)], row=1, col=2)

        st.plotly_chart(occupation_df_fig, user_container_width = True)
        
        
col3, col4 = st.columns((0.5,0.5))
    
with col3:

        bins = list(range(20000, 100000, 10000))
        labels = ['20k-30k', '30k-40k', '40k-50k', '50k-60k', '60k-70k', '70k-80k', '80k-90k']

        income_df = filtered_df['income_group'].value_counts(sort=False, normalize = True).mul(100).round(2)


        # Your existing code for creating graph2
        max_values = income_df.nlargest(2)
        colors_income = ['#b20710' if value in max_values.values else '#f5f5f1' for value in income_df]
        x_values = [str(interval) for interval in income_df.index]

        inc_fig = go.Figure(go.Bar(
            x=x_values,
            y=income_df,
            marker_color=colors_income,
            marker_line_color = '#221f1f',
            text = income_df.values,
            texttemplate = '<b>%{text}%<b>',
            textposition="outside"
        ))

        # Update layout to match the format of graph1
        inc_fig.update_layout(
            bargap=0.3,
            title='<b>Income Distribution<b>',
            xaxis_title='Average Income',
            yaxis_title='Frequency',
            width = 600,
            margin=dict(t=30,b=100)
        )

        inc_fig.update_xaxes(tickmode = 'array', tickvals=x_values, ticktext=labels)
        inc_fig.update_yaxes(range=[0,max(income_df)+5])

        st.plotly_chart(inc_fig, user_container_width = True)
        

with col4:
        age_df = filtered_df["age_group"].value_counts(normalize=True).sort_index().mul(100).round(2)
        colors_age = ['#b20710' if age_group == max(age_df) else '#f5f5f1' for age_group in age_df]

        age_df_fig = make_subplots(rows=1, cols=2, column_widths=[0.45, 0.55], shared_yaxes=True, horizontal_spacing=.06)
        median_income = int(filtered_df['avg_income'].median())

        # Unique occupations in the DataFrame
        age_grps = filtered_df['age_group'].unique()

        # Loop through each occupation and add a Box trace
        for i, age_grp in enumerate(age_grps, start=0):
            age_df_fig.add_trace(go.Box(
                x=filtered_df[filtered_df['age_group'] == age_grp]['avg_income'],
                name=age_grp,
                marker_color='#f5f5f1',
            ), row=1, col=2)

        age_df_fig.add_vline(x=median_income, line_dash='dot', annotation_text=f'Median Income <br> {median_income}', annotation_position="top", line_color="#b20710")


        age_df_fig.add_trace(go.Bar(
            y = age_df.index,
            x = age_df,
            marker_color = colors_age,
            marker_line_color = '#221f1f',
            text = age_df.values,
            texttemplate = '<b>%{text}%<b>',
            textposition="inside",
            orientation='h'
        ),row=1, col=1)

        age_df_fig.update_layout(showlegend=False, title = '<b> Age Distribution <b>', margin=dict(t=30,b=100))
        age_df_fig.update_xaxes(range=[0,max(age_df)+5])
        age_df_fig.update_xaxes(range=[np.round(min(filtered_df['avg_income']), -4), np.round(max(filtered_df['avg_income']), -4)], row=1, col=2)

        st.plotly_chart(age_df_fig, user_container_width = True)


