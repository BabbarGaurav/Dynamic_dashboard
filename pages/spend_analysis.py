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
