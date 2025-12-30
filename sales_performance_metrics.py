"""
Sales Performance Dashboard
Comprehensive sales analytics with KPIs, trends, and insights
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from db_connection import run_query, get_filter_options


def sales_performance_metrics():
    st.title("📈 Sales Performance Dashboard")
    st.markdown("Track revenue, orders, and sales trends across your business")
    st.markdown("---")

    # ============================================
    # FILTERS SECTION
    # ============================================
    st.markdown("### 🔍 Filters")

    col1, col2, col3 = st.columns(3)

    with col1:
        # Date range filter
        default_start = datetime.now() - timedelta(days=90)
        default_end = datetime.now()
        date_range = st.date_input(
            "Select Date Range",
            value=(default_start, default_end),
            key="sales_date_filter"
        )

    with col2:
        # Brand filter
        brands = ["All"] + get_filter_options("Products", "BRAND")
        selected_brand = st.selectbox(
            "Filter by Brand", brands, key="sales_brand")

    with col3:
        # Merchant filter
        merchants = [
            "All"] + get_filter_options("Third_Party_Merchants", "THIRD_PARTY_MERCHANT_NAME")
        selected_merchant = st.selectbox(
            "Filter by Merchant", merchants, key="sales_merchant")

    # Validate date range
    if len(date_range) != 2:
        st.error("⚠️ Please select both start and end dates")
        st.stop()

    start_date, end_date = date_range

    if start_date > end_date:
        st.error("⚠️ Start date must be before end date")
        st.stop()

    # Calculate comparison period
    period_days = (end_date - start_date).days
    prev_start = start_date - timedelta(days=period_days)
    prev_end = start_date

    # Build filter conditions
    brand_filter = f"AND p.BRAND = '{selected_brand}'" if selected_brand != "All" else ""
    merchant_filter = f"AND m.THIRD_PARTY_MERCHANT_NAME = '{selected_merchant}'" if selected_merchant != "All" else ""

    st.markdown("---")

    # ============================================
    # KEY PERFORMANCE INDICATORS
    # ============================================
    st.markdown("## 🎯 Key Performance Indicators")

    kpi_query = f"""
    WITH CurrentPeriod AS (
        SELECT
            SUM(s.TOTAL_SALE_AMOUNT) as total_revenue,
            COUNT(DISTINCT s.SALE_ID) as total_orders,
            COUNT(DISTINCT s.CUSTOMER_ID) as unique_customers,
            AVG(s.TOTAL_SALE_AMOUNT) as avg_order_value,
            SUM(s.QUANTITY_SOLD) as units_sold,
            SUM(s.DISCOUNT_APPLIED) as total_discounts
        FROM Sales s
        JOIN Products p ON s.ITEM_ID = p.ITEM_ID
        JOIN Third_Party_Merchants m ON s.MERCHANT_ID = m.MERCHANT_ID
        WHERE s.SALE_DATE BETWEEN '{start_date}' AND '{end_date}'
        {brand_filter}
        {merchant_filter}
    ),
    PreviousPeriod AS (
        SELECT
            SUM(s.TOTAL_SALE_AMOUNT) as prev_revenue,
            COUNT(DISTINCT s.SALE_ID) as prev_orders,
            AVG(s.TOTAL_SALE_AMOUNT) as prev_aov,
            COUNT(DISTINCT s.CUSTOMER_ID) as prev_customers
        FROM Sales s
        JOIN Products p ON s.ITEM_ID = p.ITEM_ID
        JOIN Third_Party_Merchants m ON s.MERCHANT_ID = m.MERCHANT_ID
        WHERE s.SALE_DATE BETWEEN '{prev_start}' AND '{prev_end}'
        {brand_filter}
        {merchant_filter}
    )
    SELECT 
        cp.*,
        pp.prev_revenue,
        pp.prev_orders,
        pp.prev_aov,
        pp.prev_customers,
        ROUND(((cp.total_revenue - pp.prev_revenue) / NULLIF(pp.prev_revenue, 0)) * 100, 2) as revenue_growth,
        ROUND(((cp.avg_order_value - pp.prev_aov) / NULLIF(pp.prev_aov, 0)) * 100, 2) as aov_growth,
        ROUND(((cp.unique_customers - pp.prev_customers) / NULLIF(pp.prev_customers, 0)) * 100, 2) as customer_growth
    FROM CurrentPeriod cp, PreviousPeriod pp
    """

    kpi_df = run_query(kpi_query)

    if kpi_df is not None and not kpi_df.empty:
        row = kpi_df.iloc[0]

        # Display KPIs in columns
        col1, col2, col3, col4, col5, col6 = st.columns(6)

        with col1:
            st.metric(
                "💰 Total Revenue",
                f"${row['TOTAL_REVENUE']:,.0f}",
                f"{row['REVENUE_GROWTH']:+.1f}%",
                delta_color="normal"
            )

        with col2:
            st.metric(
                "🛒 Total Orders",
                f"{int(row['TOTAL_ORDERS']):,}",
                f"{int(row['TOTAL_ORDERS'] - row['PREV_ORDERS']):+,}",
                delta_color="normal"
            )

        with col3:
            st.metric(
                "📊 Avg Order Value",
                f"${row['AVG_ORDER_VALUE']:.2f}",
                f"{row['AOV_GROWTH']:+.1f}%",
                delta_color="normal"
            )

        with col4:
            st.metric(
                "👥 Unique Customers",
                f"{int(row['UNIQUE_CUSTOMERS']):,}",
                f"{row['CUSTOMER_GROWTH']:+.1f}%",
                delta_color="normal"
            )

        with col5:
            conversion_rate = (row['TOTAL_ORDERS'] / row['UNIQUE_CUSTOMERS']
                               * 100) if row['UNIQUE_CUSTOMERS'] > 0 else 0
            st.metric(
                "📈 Conversion Rate",
                f"{conversion_rate:.1f}%"
            )

        with col6:
            avg_discount = (
                row['TOTAL_DISCOUNTS'] / row['TOTAL_ORDERS']) if row['TOTAL_ORDERS'] > 0 else 0
            st.metric(
                "💸 Avg Discount",
                f"${avg_discount:.2f}"
            )

        # Additional insights
        st.info(f"""
        📊 **Period Summary:** {period_days} days | 
        📦 **Units Sold:** {int(row['UNITS_SOLD']):,} | 
        💵 **Revenue per Customer:** ${(row['TOTAL_REVENUE']/row['UNIQUE_CUSTOMERS']):.2f} | 
        🎯 **Discount Rate:** {(row['TOTAL_DISCOUNTS']/row['TOTAL_REVENUE']*100):.1f}%
        """)
    else:
        st.warning("⚠️ No sales data available for the selected period")

    st.markdown("---")

    # ============================================
    # SALES TREND ANALYSIS
    # ============================================
    st.markdown("## 📊 Sales Trend Analysis")

    col1, col2 = st.columns([2, 1])

    with col1:
        # Daily sales trend with moving average
        trend_query = f"""
        SELECT 
            s.SALE_DATE,
            SUM(s.TOTAL_SALE_AMOUNT) as daily_revenue,
            COUNT(DISTINCT s.SALE_ID) as daily_orders,
            AVG(s.TOTAL_SALE_AMOUNT) as avg_order_value
        FROM Sales s
        JOIN Products p ON s.ITEM_ID = p.ITEM_ID
        JOIN Third_Party_Merchants m ON s.MERCHANT_ID = m.MERCHANT_ID
        WHERE s.SALE_DATE BETWEEN '{start_date}' AND '{end_date}'
        {brand_filter}
        {merchant_filter}
        GROUP BY s.SALE_DATE
        ORDER BY s.SALE_DATE
        """

        trend_df = run_query(trend_query)

        if trend_df is not None and not trend_df.empty:
            # Calculate 7-day moving average
            trend_df['MA7_REVENUE'] = trend_df['DAILY_REVENUE'].rolling(
                window=7, min_periods=1).mean()
            trend_df['MA7_ORDERS'] = trend_df['DAILY_ORDERS'].rolling(
                window=7, min_periods=1).mean()

            # Create dual-axis chart
            fig = go.Figure()

            # Revenue bars
            fig.add_trace(go.Bar(
                x=trend_df['SALE_DATE'],
                y=trend_df['DAILY_REVENUE'],
                name='Daily Revenue',
                marker_color='rgba(52, 152, 219, 0.6)',
                yaxis='y',
                hovertemplate='<b>%{x|%b %d, %Y}</b><br>Revenue: $%{y:,.0f}<extra></extra>'
            ))

            # Revenue moving average line
            fig.add_trace(go.Scatter(
                x=trend_df['SALE_DATE'],
                y=trend_df['MA7_REVENUE'],
                name='7-Day Avg Revenue',
                line=dict(color='#e74c3c', width=3),
                yaxis='y',
                hovertemplate='<b>%{x|%b %d}</b><br>7-Day Avg: $%{y:,.0f}<extra></extra>'
            ))

            # Orders line (secondary axis)
            fig.add_trace(go.Scatter(
                x=trend_df['SALE_DATE'],
                y=trend_df['DAILY_ORDERS'],
                name='Daily Orders',
                line=dict(color='#2ecc71', width=2, dash='dot'),
                yaxis='y2',
                hovertemplate='<b>%{x|%b %d}</b><br>Orders: %{y}<extra></extra>'
            ))

            fig.update_layout(
                title='Revenue & Orders Trend Over Time',
                xaxis=dict(title='Date', showgrid=True),
                yaxis=dict(title='Revenue ($)', side='left', showgrid=True),
                yaxis2=dict(title='Orders', overlaying='y',
                            side='right', showgrid=False),
                hovermode='x unified',
                height=450,
                showlegend=True,
                legend=dict(
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='right',
                    x=1
                ),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )

            st.plotly_chart(fig, width='stretch')
        else:
            st.warning("No trend data available")

    with col2:
        # Sales distribution by day of week
        if trend_df is not None and not trend_df.empty:
            trend_df['DAY_OF_WEEK'] = pd.to_datetime(
                trend_df['SALE_DATE']).dt.day_name()
            day_order = ['Monday', 'Tuesday', 'Wednesday',
                         'Thursday', 'Friday', 'Saturday', 'Sunday']

            dow_df = trend_df.groupby('DAY_OF_WEEK').agg({
                'DAILY_REVENUE': 'sum',
                'DAILY_ORDERS': 'sum'
            }).reindex(day_order)

            fig_dow = px.bar(
                dow_df,
                y=dow_df.index,
                x='DAILY_REVENUE',
                orientation='h',
                title='Sales by Day of Week',
                labels={
                    'DAILY_REVENUE': 'Total Revenue ($)', 'DAY_OF_WEEK': ''},
                color='DAILY_REVENUE',
                color_continuous_scale='Blues',
                text='DAILY_REVENUE'
            )

            fig_dow.update_traces(
                texttemplate='$%{text:,.0f}',
                textposition='outside'
            )

            fig_dow.update_layout(
                height=450,
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)'
            )

            st.plotly_chart(fig_dow, width='stretch')

    st.markdown("---")

    # ============================================
    # CATEGORY & BRAND PERFORMANCE
    # ============================================
    st.markdown("## 🏷️ Category & Brand Performance")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Top 10 Categories by Revenue")

        category_query = f"""
        SELECT 
            SPLIT_PART(p.TAXONOMY, ' > ', 1) AS CATEGORY,
            SUM(s.TOTAL_SALE_AMOUNT) as revenue,
            COUNT(DISTINCT s.SALE_ID) as orders,
            SUM(s.QUANTITY_SOLD) as units_sold,
            ROUND(SUM(s.TOTAL_SALE_AMOUNT) / COUNT(DISTINCT s.SALE_ID), 2) as aov
        FROM Sales s
        JOIN Products p ON s.ITEM_ID = p.ITEM_ID
        JOIN Third_Party_Merchants m ON s.MERCHANT_ID = m.MERCHANT_ID
        WHERE s.SALE_DATE BETWEEN '{start_date}' AND '{end_date}'
        {brand_filter}
        {merchant_filter}
        GROUP BY CATEGORY
        ORDER BY revenue DESC
        LIMIT 10
        """

        cat_df = run_query(category_query)

        if cat_df is not None and not cat_df.empty:
            fig = px.bar(
                cat_df,
                x='REVENUE',
                y='CATEGORY',
                orientation='h',
                labels={'REVENUE': 'Revenue ($)', 'CATEGORY': ''},
                color='REVENUE',
                color_continuous_scale='Teal',
                text='REVENUE',
                hover_data={'ORDERS': ':,', 'UNITS_SOLD': ':,', 'AOV': ':$.2f'}
            )
            fig.update_traces(
                texttemplate='$%{text:,.0f}', textposition='outside')
            fig.update_layout(height=400, showlegend=False,
                              plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, width='stretch')

    with col2:
        st.markdown("### Top 10 Brands by Revenue")

        brand_query = f"""
        SELECT 
            p.BRAND,
            SUM(s.TOTAL_SALE_AMOUNT) as revenue,
            COUNT(DISTINCT s.SALE_ID) as orders,
            SUM(s.QUANTITY_SOLD) as units_sold
        FROM Sales s
        JOIN Products p ON s.ITEM_ID = p.ITEM_ID
        JOIN Third_Party_Merchants m ON s.MERCHANT_ID = m.MERCHANT_ID
        WHERE s.SALE_DATE BETWEEN '{start_date}' AND '{end_date}'
        {merchant_filter}
        GROUP BY p.BRAND
        ORDER BY revenue DESC
        LIMIT 10
        """

        brand_df = run_query(brand_query)

        if brand_df is not None and not brand_df.empty:
            fig = px.pie(
                brand_df,
                values='REVENUE',
                names='BRAND',
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate='<b>%{label}</b><br>Revenue: $%{value:,.0f}<br>Share: %{percent}<extra></extra>'
            )
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, width='stretch')

    st.markdown("---")

    # ============================================
    # TOP PERFORMING PRODUCTS
    # ============================================
    st.markdown("## 🏆 Top Performing Products")

    top_products_query = f"""
    SELECT 
        p.PRODUCT_TITLE,
        p.BRAND,
        SUM(s.TOTAL_SALE_AMOUNT) as revenue,
        SUM(s.QUANTITY_SOLD) as units_sold,
        COUNT(DISTINCT s.SALE_ID) as orders,
        AVG(s.SALE_PRICE) as avg_price,
        COALESCE(AVG(r.ITEM_REVIEW_RATING), 0) as avg_rating
    FROM Sales s
    JOIN Products p ON s.ITEM_ID = p.ITEM_ID
    JOIN Third_Party_Merchants m ON s.MERCHANT_ID = m.MERCHANT_ID
    LEFT JOIN Reviews r ON p.ITEM_ID = r.ITEM_ID
    WHERE s.SALE_DATE BETWEEN '{start_date}' AND '{end_date}'
    {brand_filter}
    {merchant_filter}
    GROUP BY p.PRODUCT_TITLE, p.BRAND
    ORDER BY revenue DESC
    LIMIT 20
    """

    top_products_df = run_query(top_products_query)

    if top_products_df is not None and not top_products_df.empty:
        # Format for display
        display_df = top_products_df.copy()
        display_df['REVENUE'] = display_df['REVENUE'].apply(
            lambda x: f"${x:,.0f}")
        display_df['UNITS_SOLD'] = display_df['UNITS_SOLD'].apply(
            lambda x: f"{int(x):,}")
        display_df['AVG_PRICE'] = display_df['AVG_PRICE'].apply(
            lambda x: f"${x:.2f}")
        display_df['AVG_RATING'] = display_df['AVG_RATING'].apply(
            lambda x: f"{x:.2f}⭐")

        display_df.columns = ['Product', 'Brand', 'Revenue',
                              'Units Sold', 'Orders', 'Avg Price', 'Rating']

        st.dataframe(
            display_df,
            width='stretch',
            hide_index=True,
            height=400
        )
    else:
        st.warning("No product data available")

    st.markdown("---")

    # ============================================
    # MERCHANT PERFORMANCE
    # ============================================
    st.markdown("## 🏪 Merchant Performance Analysis")

    merchant_query = f"""
    SELECT 
        m.THIRD_PARTY_MERCHANT_NAME,
        SUM(s.TOTAL_SALE_AMOUNT) as revenue,
        COUNT(DISTINCT s.SALE_ID) as orders,
        AVG(s.TOTAL_SALE_AMOUNT) as aov,
        SUM(s.QUANTITY_SOLD) as units_sold,
        SUM(s.DISCOUNT_APPLIED) as total_discounts,
        ROUND((SUM(s.DISCOUNT_APPLIED) / SUM(s.TOTAL_SALE_AMOUNT)) * 100, 2) as discount_rate
    FROM Sales s
    JOIN Products p ON s.ITEM_ID = p.ITEM_ID
    JOIN Third_Party_Merchants m ON s.MERCHANT_ID = m.MERCHANT_ID
    WHERE s.SALE_DATE BETWEEN '{start_date}' AND '{end_date}'
    {brand_filter}
    GROUP BY m.THIRD_PARTY_MERCHANT_NAME
    ORDER BY revenue DESC
    """

    merchant_df = run_query(merchant_query)

    if merchant_df is not None and not merchant_df.empty:
        # Create visualization
        col1, col2 = st.columns([2, 1])

        with col1:
            fig = px.bar(
                merchant_df,
                x='THIRD_PARTY_MERCHANT_NAME',
                y='REVENUE',
                color='AOV',
                labels={
                    'REVENUE': 'Total Revenue ($)', 'THIRD_PARTY_MERCHANT_NAME': 'Merchant', 'AOV': 'Avg Order Value'},
                title='Merchant Revenue Performance',
                color_continuous_scale='Viridis',
                text='REVENUE'
            )
            fig.update_traces(
                texttemplate='$%{text:,.0f}', textposition='outside')
            fig.update_layout(height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig, width='stretch')

        with col2:
            # Top merchant metrics
            top_merchant = merchant_df.iloc[0]
            st.markdown(f"### 🥇 Top Merchant")
            st.markdown(f"**{top_merchant['THIRD_PARTY_MERCHANT_NAME']}**")
            st.metric("Revenue", f"${top_merchant['REVENUE']:,.0f}")
            st.metric("Orders", f"{int(top_merchant['ORDERS']):,}")
            st.metric("AOV", f"${top_merchant['AOV']:.2f}")
            st.metric("Discount Rate", f"{top_merchant['DISCOUNT_RATE']:.1f}%")

        # Detailed table
        st.markdown("### Detailed Merchant Breakdown")
        display_merchant_df = merchant_df.copy()
        display_merchant_df['REVENUE'] = display_merchant_df['REVENUE'].apply(
            lambda x: f"${x:,.0f}")
        display_merchant_df['AOV'] = display_merchant_df['AOV'].apply(
            lambda x: f"${x:.2f}")
        display_merchant_df['TOTAL_DISCOUNTS'] = display_merchant_df['TOTAL_DISCOUNTS'].apply(
            lambda x: f"${x:,.0f}")
        display_merchant_df['DISCOUNT_RATE'] = display_merchant_df['DISCOUNT_RATE'].apply(
            lambda x: f"{x:.1f}%")

        display_merchant_df.columns = [
            'Merchant', 'Revenue', 'Orders', 'AOV', 'Units Sold', 'Total Discounts', 'Discount Rate']

        st.dataframe(
            display_merchant_df,
            width='stretch',
            hide_index=True,
            height=300
        )
    else:
        st.warning("No merchant data available")

    # Footer
    st.markdown("---")
    st.caption(
        f"💡 Dashboard updated in real-time | Last refreshed: {datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}")
