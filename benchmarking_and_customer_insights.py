"""
Benchmarking & Customer Insights Dashboard
Competitive pricing analysis and customer behavior analytics
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from db_connection import run_query, get_filter_options


def benchmarking_and_customer_insights():
    st.title("📊 Benchmarking & Customer Insights")
    st.markdown(
        "Competitive pricing intelligence and customer behavior analysis")
    st.markdown("---")

    # Create tabs for better organization
    tab1, tab2, tab3 = st.tabs(
        ["💰 Price Benchmarking", "🏪 Competitor Analysis", "👥 Customer Insights"])

    # ============================================
    # TAB 1: PRICE BENCHMARKING
    # ============================================
    with tab1:
        st.markdown("## 💰 Price Comparison with Competitors")

        # Filters
        col1, col2, col3 = st.columns(3)

        with col1:
            brands = ["All"] + get_filter_options("Products", "BRAND")
            selected_brand = st.selectbox(
                "Filter by Brand", brands, key="bench_brand")

        with col2:
            comparison_options = ["All", "Above Benchmark",
                                  "Below Benchmark", "At Benchmark"]
            comparison_filter = st.selectbox(
                "Price Comparison", comparison_options, key="price_comp")

        with col3:
            search_text = st.text_input(
                "Search Product", placeholder="Enter product name...", key="price_search_bench")

        # Build filters
        brand_filter = f"AND p.BRAND = '{selected_brand}'" if selected_brand != "All" else ""

        # Price comparison query
        price_comparison_query = f"""
        SELECT
            p.PRODUCT_TITLE,
            p.BRAND,
            pr.PRODUCT_PRICE,
            pr.BENCHMARK_BASE_PRICE,
            pr.BENCHMARK_SITE_PRICE,
            ROUND(pr.PRODUCT_PRICE - pr.BENCHMARK_SITE_PRICE, 2) as price_difference,
            ROUND(((pr.PRODUCT_PRICE - pr.BENCHMARK_SITE_PRICE) / NULLIF(pr.BENCHMARK_SITE_PRICE, 0)) * 100, 2) as price_diff_pct,
            CASE
                WHEN pr.PRODUCT_PRICE > pr.BENCHMARK_SITE_PRICE THEN 'Above Benchmark'
                WHEN pr.PRODUCT_PRICE < pr.BENCHMARK_SITE_PRICE THEN 'Below Benchmark'
                ELSE 'At Benchmark'
            END AS PRICE_COMPARISON,
            b.BENCHMARK_STORE
        FROM Products p
        JOIN Pricing pr ON p.ITEM_ID = pr.ITEM_ID
        JOIN Benchmark b ON pr.BENCHMARK_ID = b.BENCHMARK_ID
        WHERE pr.BENCHMARK_SITE_PRICE IS NOT NULL
        {brand_filter}
        ORDER BY price_diff_pct DESC
        """

        price_comparison_df = run_query(price_comparison_query)

        if price_comparison_df is not None and not price_comparison_df.empty:
            # Apply additional filters
            if comparison_filter != "All":
                price_comparison_df = price_comparison_df[
                    price_comparison_df['PRICE_COMPARISON'] == comparison_filter
                ]

            if search_text:
                price_comparison_df = price_comparison_df[
                    price_comparison_df['PRODUCT_TITLE'].str.contains(
                        search_text, case=False, na=False)
                ]

            if not price_comparison_df.empty:
                # Key metrics
                col1, col2, col3, col4 = st.columns(4)

                at_benchmark = len(
                    price_comparison_df[price_comparison_df['PRICE_COMPARISON'] == 'At Benchmark'])
                below_benchmark = len(
                    price_comparison_df[price_comparison_df['PRICE_COMPARISON'] == 'Below Benchmark'])
                above_benchmark = len(
                    price_comparison_df[price_comparison_df['PRICE_COMPARISON'] == 'Above Benchmark'])
                avg_diff = price_comparison_df['PRICE_DIFF_PCT'].mean()

                with col1:
                    st.metric("✅ At Benchmark", at_benchmark)

                with col2:
                    st.metric("📉 Below Benchmark", below_benchmark)
                    st.caption("More competitive")

                with col3:
                    st.metric("📈 Above Benchmark", above_benchmark)
                    st.caption("Premium pricing")

                with col4:
                    st.metric("Avg Price Difference", f"{avg_diff:+.1f}%")

                st.markdown("---")

                # Visualization
                col1, col2 = st.columns([2, 1])

                with col1:
                    # Price comparison scatter plot
                    fig = px.scatter(
                        price_comparison_df.head(50),
                        x='BENCHMARK_SITE_PRICE',
                        y='PRODUCT_PRICE',
                        color='PRICE_COMPARISON',
                        hover_name='PRODUCT_TITLE',
                        hover_data={
                            'BRAND': True,
                            'BENCHMARK_STORE': True,
                            'PRICE_DIFFERENCE': ':$.2f',
                            'PRICE_DIFF_PCT': ':+.1f%'
                        },
                        labels={
                            'BENCHMARK_SITE_PRICE': 'Competitor Price ($)',
                            'PRODUCT_PRICE': 'Our Price ($)'
                        },
                        title='Price Positioning vs Competitors',
                        color_discrete_map={
                            'Above Benchmark': '#e74c3c',
                            'At Benchmark': '#f39c12',
                            'Below Benchmark': '#2ecc71'
                        }
                    )

                    # Add diagonal line (price parity)
                    max_price = max(price_comparison_df['BENCHMARK_SITE_PRICE'].max(),
                                    price_comparison_df['PRODUCT_PRICE'].max())
                    fig.add_trace(go.Scatter(
                        x=[0, max_price],
                        y=[0, max_price],
                        mode='lines',
                        line=dict(color='gray', dash='dash', width=2),
                        name='Price Parity',
                        showlegend=True
                    ))

                    fig.update_layout(height=450, plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, width='stretch')

                with col2:
                    # Price difference distribution
                    st.markdown("### 📊 Price Gap Analysis")

                    fig_hist = px.histogram(
                        price_comparison_df,
                        x='PRICE_DIFF_PCT',
                        nbins=20,
                        labels={'PRICE_DIFF_PCT': 'Price Difference (%)'},
                        color_discrete_sequence=['#3498db']
                    )
                    fig_hist.add_vline(
                        x=0, line_dash="dash", line_color="red", annotation_text="Parity")
                    fig_hist.update_layout(
                        height=250,
                        showlegend=False,
                        yaxis_title='Count',
                        plot_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig_hist, width='stretch')

                    # Insights
                    if avg_diff > 5:
                        st.warning(
                            f"⚠️ Our prices are {avg_diff:.1f}% higher on average. Consider price optimization.")
                    elif avg_diff < -5:
                        st.success(
                            f"✅ We're {abs(avg_diff):.1f}% more competitive on pricing!")
                    else:
                        st.info(
                            f"✓ Prices are well-aligned with market ({avg_diff:+.1f}%)")

                st.markdown("---")

                # Detailed table
                st.markdown("### 📋 Detailed Price Comparison")

                display_df = price_comparison_df.copy()
                display_df['PRODUCT_PRICE'] = display_df['PRODUCT_PRICE'].apply(
                    lambda x: f"${x:.2f}")
                display_df['BENCHMARK_SITE_PRICE'] = display_df['BENCHMARK_SITE_PRICE'].apply(
                    lambda x: f"${x:.2f}")
                display_df['PRICE_DIFFERENCE'] = display_df['PRICE_DIFFERENCE'].apply(
                    lambda x: f"${x:+.2f}")
                display_df['PRICE_DIFF_PCT'] = display_df['PRICE_DIFF_PCT'].apply(
                    lambda x: f"{x:+.1f}%")

                display_df = display_df[['PRODUCT_TITLE', 'BRAND', 'PRODUCT_PRICE',
                                        'BENCHMARK_SITE_PRICE', 'PRICE_DIFFERENCE',
                                         'PRICE_DIFF_PCT', 'PRICE_COMPARISON', 'BENCHMARK_STORE']]

                display_df.columns = ['Product', 'Brand', 'Our Price', 'Competitor Price',
                                      'Difference', 'Diff %', 'Status', 'Competitor']

                st.dataframe(
                    display_df,
                    width='stretch',
                    hide_index=True,
                    height=400
                )
            else:
                st.warning(
                    "❌ No products found matching your criteria. Please adjust filters.")
        else:
            st.warning("No price comparison data available")

    # ============================================
    # TAB 2: COMPETITOR ANALYSIS
    # ============================================
    with tab2:
        st.markdown("## 🏪 Competitor Pricing Trends")

        # Filters
        col1, col2, col3 = st.columns(3)

        with col1:
            brand_names = get_filter_options(
                "Benchmark", "BENCHMARK_BRAND_NAME")
            if brand_names:
                selected_comp_brand = st.selectbox(
                    "Select Brand", brand_names, key="comp_brand")
            else:
                st.error("No competitor brands found")
                st.stop()

        with col2:
            stores = get_filter_options("Benchmark", "BENCHMARK_STORE")
            selected_stores = st.multiselect(
                "Select Competitor Store(s)",
                stores,
                default=stores[:3] if len(stores) >= 3 else stores,
                key="comp_stores"
            )

        with col3:
            date_range = st.date_input(
                "Date Range",
                value=(datetime.now() - timedelta(days=90), datetime.now()),
                key="comp_date_range"
            )

        if len(date_range) == 2 and selected_stores:
            start_date, end_date = date_range

            # Competitor pricing trend query
            competitor_pricing_query = f"""
            SELECT
                b.BENCHMARK_BRAND_NAME,
                b.BENCHMARK_STORE,
                b.BENCHMARK_CATG,
                b.BENCHMARK_SUBCATG,
                pr.BENCHMARK_SITE_PRICE,
                pr.PRICE_SCRAPE_DATE,
                b.BENCHMARK_ITEM_SUB_DESC
            FROM Benchmark b
            JOIN Pricing pr ON b.BENCHMARK_ID = pr.BENCHMARK_ID
            WHERE pr.BENCHMARK_SITE_PRICE IS NOT NULL
                AND b.BENCHMARK_BRAND_NAME = '{selected_comp_brand}'
                AND b.BENCHMARK_STORE IN ({','.join([f"'{store}'" for store in selected_stores])})
                AND pr.PRICE_SCRAPE_DATE BETWEEN '{start_date}' AND '{end_date}'
            ORDER BY pr.PRICE_SCRAPE_DATE
            """

            competitor_df = run_query(competitor_pricing_query)

            if competitor_df is not None and not competitor_df.empty:
                # Aggregate by date and store
                trend_data = competitor_df.groupby(['PRICE_SCRAPE_DATE', 'BENCHMARK_STORE']).agg({
                    'BENCHMARK_SITE_PRICE': ['mean', 'min', 'max', 'count']
                }).reset_index()

                trend_data.columns = [
                    'Date', 'Store', 'Avg_Price', 'Min_Price', 'Max_Price', 'Product_Count']

                # KPIs
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Avg Competitor Price",
                              f"${trend_data['Avg_Price'].mean():.2f}")

                with col2:
                    st.metric(
                        "Price Range", f"${trend_data['Min_Price'].min():.2f} - ${trend_data['Max_Price'].max():.2f}")

                with col3:
                    st.metric("Products Tracked", int(
                        competitor_df['BENCHMARK_ITEM_SUB_DESC'].nunique()))

                with col4:
                    price_volatility = trend_data['Avg_Price'].std()
                    st.metric("Price Volatility", f"${price_volatility:.2f}")

                st.markdown("---")

                # Line chart for trends
                fig = px.line(
                    trend_data,
                    x='Date',
                    y='Avg_Price',
                    color='Store',
                    title=f'{selected_comp_brand} Pricing Trends Across Competitors',
                    labels={'Avg_Price': 'Average Price ($)', 'Date': 'Date'},
                    markers=True
                )

                fig.update_layout(
                    height=450,
                    hovermode='x unified',
                    plot_bgcolor='rgba(0,0,0,0)'
                )

                st.plotly_chart(fig, width='stretch')

                st.markdown("---")

                # Category performance
                st.markdown("### 📊 Price Distribution by Category")

                category_pricing = competitor_df.groupby('BENCHMARK_CATG').agg({
                    'BENCHMARK_SITE_PRICE': ['mean', 'count']
                }).reset_index()
                category_pricing.columns = [
                    'Category', 'Avg_Price', 'Product_Count']
                category_pricing = category_pricing.sort_values(
                    'Avg_Price', ascending=False)

                fig_cat = px.bar(
                    category_pricing,
                    x='Avg_Price',
                    y='Category',
                    orientation='h',
                    text='Avg_Price',
                    color='Product_Count',
                    labels={
                        'Avg_Price': 'Average Price ($)', 'Product_Count': 'Products'},
                    color_continuous_scale='Viridis'
                )

                fig_cat.update_traces(
                    texttemplate='$%{text:.2f}', textposition='outside')
                fig_cat.update_layout(height=400, plot_bgcolor='rgba(0,0,0,0)')

                st.plotly_chart(fig_cat, width='stretch')

                st.markdown("---")

                # Store comparison
                st.markdown("### 🏬 Store-wise Price Comparison")

                store_comparison = competitor_df.groupby('BENCHMARK_STORE').agg({
                    'BENCHMARK_SITE_PRICE': ['mean', 'min', 'max', 'count']
                }).reset_index()
                store_comparison.columns = [
                    'Store', 'Avg_Price', 'Min_Price', 'Max_Price', 'Products']

                display_store = store_comparison.copy()
                display_store['Avg_Price'] = display_store['Avg_Price'].apply(
                    lambda x: f"${x:.2f}")
                display_store['Min_Price'] = display_store['Min_Price'].apply(
                    lambda x: f"${x:.2f}")
                display_store['Max_Price'] = display_store['Max_Price'].apply(
                    lambda x: f"${x:.2f}")

                st.dataframe(
                    display_store,
                    width='stretch',
                    hide_index=True
                )
            else:
                st.warning("No competitor data available for selected filters")
        else:
            st.info("👆 Please select at least one store and a valid date range")

        st.markdown("---")

        # Benchmark category performance (sunburst)
        st.markdown("### 🎯 Market Share by Category")

        benchmark_category_query = """
        SELECT
            b.BENCHMARK_CATG,
            b.BENCHMARK_SUBCATG,
            b.BENCHMARK_STORE,
            COUNT(DISTINCT b.BENCHMARK_ID) as product_count,
            AVG(pr.BENCHMARK_SITE_PRICE) as avg_price
        FROM Benchmark b
        JOIN Pricing pr ON b.BENCHMARK_ID = pr.BENCHMARK_ID
        WHERE pr.BENCHMARK_SITE_PRICE IS NOT NULL
        GROUP BY b.BENCHMARK_CATG, b.BENCHMARK_SUBCATG, b.BENCHMARK_STORE
        ORDER BY product_count DESC
        """

        benchmark_cat_df = run_query(benchmark_category_query)

        if benchmark_cat_df is not None and not benchmark_cat_df.empty:
            fig_sunburst = px.sunburst(
                benchmark_cat_df,
                path=['BENCHMARK_CATG', 'BENCHMARK_SUBCATG', 'BENCHMARK_STORE'],
                values='PRODUCT_COUNT',
                color='AVG_PRICE',
                color_continuous_scale='RdYlGn_r',
                title='Product Distribution: Category → Subcategory → Store',
                hover_data={'PRODUCT_COUNT': ':,', 'AVG_PRICE': ':$.2f'}
            )

            fig_sunburst.update_layout(height=600)
            st.plotly_chart(fig_sunburst, width='stretch')
        else:
            st.warning("No benchmark category data available")

    # ============================================
    # TAB 3: CUSTOMER INSIGHTS
    # ============================================
    with tab3:
        st.markdown("## 👥 Customer Behavior Analytics")

        # Date filter
        col1, col2 = st.columns(2)
        with col1:
            customer_date_range = st.date_input(
                "Select Analysis Period",
                value=(datetime.now() - timedelta(days=180), datetime.now()),
                key="customer_date"
            )

        if len(customer_date_range) == 2:
            cust_start, cust_end = customer_date_range

            # ========== PAYMENT METHODS ==========
            st.markdown("### 💳 Payment Method Preferences")

            payment_methods_query = f"""
            SELECT
                s.PAYMENT_METHOD,
                COUNT(s.SALE_ID) AS total_transactions,
                SUM(s.TOTAL_SALE_AMOUNT) AS total_revenue,
                AVG(s.TOTAL_SALE_AMOUNT) AS avg_transaction_value
            FROM Sales s
            WHERE s.SALE_DATE BETWEEN '{cust_start}' AND '{cust_end}'
            GROUP BY s.PAYMENT_METHOD
            ORDER BY total_transactions DESC
            """

            payment_df = run_query(payment_methods_query)

            if payment_df is not None and not payment_df.empty:
                col1, col2 = st.columns([1, 2])

                with col1:
                    # Pie chart
                    fig_payment = px.pie(
                        payment_df,
                        values='TOTAL_TRANSACTIONS',
                        names='PAYMENT_METHOD',
                        title='Payment Method Distribution',
                        hole=0.4,
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    fig_payment.update_traces(
                        textposition='inside', textinfo='percent+label')
                    fig_payment.update_layout(height=350)
                    st.plotly_chart(fig_payment, width='stretch')

                with col2:
                    # Bar chart for revenue
                    fig_payment_rev = px.bar(
                        payment_df,
                        x='PAYMENT_METHOD',
                        y='TOTAL_REVENUE',
                        color='AVG_TRANSACTION_VALUE',
                        title='Revenue by Payment Method',
                        labels={
                            'TOTAL_REVENUE': 'Total Revenue ($)', 'PAYMENT_METHOD': 'Payment Method'},
                        text='TOTAL_REVENUE',
                        color_continuous_scale='Blues'
                    )
                    fig_payment_rev.update_traces(
                        texttemplate='$%{text:,.0f}', textposition='outside')
                    fig_payment_rev.update_layout(
                        height=350, showlegend=False, plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_payment_rev, width='stretch')

                # Insights
                top_payment = payment_df.iloc[0]
                st.info(
                    f"💡 **Top Payment Method:** {top_payment['PAYMENT_METHOD']} accounts for {(top_payment['TOTAL_TRANSACTIONS']/payment_df['TOTAL_TRANSACTIONS'].sum()*100):.1f}% of all transactions")

            st.markdown("---")

            # ========== CUSTOMER SEGMENTATION ==========
            st.markdown("### 📂 Customer Segmentation (RFM Analysis)")

            customer_segmentation_query = f"""
            SELECT
                s.CUSTOMER_ID,
                COUNT(DISTINCT s.SALE_ID) AS purchase_frequency,
                SUM(s.TOTAL_SALE_AMOUNT) AS total_spending,
                AVG(s.TOTAL_SALE_AMOUNT) AS avg_order_value,
                MAX(s.SALE_DATE) AS last_purchase_date,
                DATEDIFF(day, MAX(s.SALE_DATE), CURRENT_DATE) AS days_since_last_purchase
            FROM Sales s
            WHERE s.SALE_DATE BETWEEN '{cust_start}' AND '{cust_end}'
            GROUP BY s.CUSTOMER_ID
            ORDER BY total_spending DESC
            """

            customer_seg_df = run_query(customer_segmentation_query)

            if customer_seg_df is not None and not customer_seg_df.empty:
                # Calculate segments
                freq_median = customer_seg_df['PURCHASE_FREQUENCY'].median()
                spend_median = customer_seg_df['TOTAL_SPENDING'].median()

                def segment_customer(row):
                    if row['PURCHASE_FREQUENCY'] >= freq_median and row['TOTAL_SPENDING'] >= spend_median:
                        return 'VIP Customers'
                    elif row['PURCHASE_FREQUENCY'] >= freq_median:
                        return 'Frequent Buyers'
                    elif row['TOTAL_SPENDING'] >= spend_median:
                        return 'High Spenders'
                    else:
                        return 'Occasional Buyers'

                customer_seg_df['SEGMENT'] = customer_seg_df.apply(
                    segment_customer, axis=1)

                # Segment distribution
                col1, col2, col3, col4 = st.columns(4)

                segment_counts = customer_seg_df['SEGMENT'].value_counts()

                with col1:
                    vip_count = segment_counts.get('VIP Customers', 0)
                    st.metric("👑 VIP Customers", vip_count)
                    st.caption("High freq + High spend")

                with col2:
                    freq_count = segment_counts.get('Frequent Buyers', 0)
                    st.metric("🔄 Frequent Buyers", freq_count)
                    st.caption("High frequency")

                with col3:
                    high_count = segment_counts.get('High Spenders', 0)
                    st.metric("💎 High Spenders", high_count)
                    st.caption("High spending")

                with col4:
                    occasional_count = segment_counts.get(
                        'Occasional Buyers', 0)
                    st.metric("👤 Occasional Buyers", occasional_count)
                    st.caption("Need engagement")

                st.markdown("---")

                # Visualization
                col1, col2 = st.columns(2)

                with col1:
                    # Scatter plot
                    fig_rfm = px.scatter(
                        customer_seg_df.head(500),
                        x='PURCHASE_FREQUENCY',
                        y='TOTAL_SPENDING',
                        size='AVG_ORDER_VALUE',
                        color='SEGMENT',
                        hover_data={'CUSTOMER_ID': True,
                                    'DAYS_SINCE_LAST_PURCHASE': True},
                        labels={
                            'PURCHASE_FREQUENCY': 'Purchase Frequency',
                            'TOTAL_SPENDING': 'Total Spending ($)',
                            'SEGMENT': 'Customer Segment'
                        },
                        title='Customer Segmentation Matrix',
                        color_discrete_map={
                            'VIP Customers': '#2ecc71',
                            'Frequent Buyers': '#3498db',
                            'High Spenders': '#9b59b6',
                            'Occasional Buyers': '#95a5a6'
                        }
                    )

                    # Add quadrant lines
                    fig_rfm.add_hline(
                        y=spend_median, line_dash="dash", line_color="gray")
                    fig_rfm.add_vline(
                        x=freq_median, line_dash="dash", line_color="gray")

                    fig_rfm.update_layout(
                        height=450, plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_rfm, width='stretch')

                with col2:
                    # Segment value breakdown
                    segment_value = customer_seg_df.groupby('SEGMENT').agg({
                        'TOTAL_SPENDING': 'sum',
                        'CUSTOMER_ID': 'count'
                    }).reset_index()
                    segment_value.columns = [
                        'Segment', 'Total_Revenue', 'Customer_Count']
                    segment_value['Revenue_Per_Customer'] = segment_value['Total_Revenue'] / \
                        segment_value['Customer_Count']

                    fig_seg_value = px.bar(
                        segment_value,
                        x='Segment',
                        y='Total_Revenue',
                        color='Revenue_Per_Customer',
                        title='Revenue by Customer Segment',
                        labels={
                            'Total_Revenue': 'Total Revenue ($)', 'Revenue_Per_Customer': 'Rev/Customer'},
                        text='Total_Revenue',
                        color_continuous_scale='Teal'
                    )
                    fig_seg_value.update_traces(
                        texttemplate='$%{text:,.0f}', textposition='outside')
                    fig_seg_value.update_layout(
                        height=450, plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_seg_value, width='stretch')

                st.markdown("---")

                # Customer lifetime value insights
                st.markdown("### 💰 Customer Lifetime Value (CLV) Analysis")

                col1, col2, col3 = st.columns(3)

                # Filter options
                with col1:
                    min_spending_filter = st.number_input(
                        "Min Total Spending ($)",
                        min_value=0,
                        value=0,
                        step=100,
                        key="min_spend_clv"
                    )

                with col2:
                    min_freq_filter = st.number_input(
                        "Min Purchase Frequency",
                        min_value=0,
                        value=0,
                        step=1,
                        key="min_freq_clv"
                    )

                with col3:
                    segment_filter = st.multiselect(
                        "Filter by Segment",
                        options=customer_seg_df['SEGMENT'].unique(),
                        default=customer_seg_df['SEGMENT'].unique(),
                        key="segment_filter_clv"
                    )

                # Apply filters
                filtered_customers = customer_seg_df[
                    (customer_seg_df['TOTAL_SPENDING'] >= min_spending_filter) &
                    (customer_seg_df['PURCHASE_FREQUENCY'] >= min_freq_filter) &
                    (customer_seg_df['SEGMENT'].isin(segment_filter))
                ]

                if not filtered_customers.empty:
                    st.success(
                        f"✅ Showing {len(filtered_customers)} customers matching criteria")

                    # Top customers table
                    top_customers = filtered_customers.head(20).copy()
                    top_customers['TOTAL_SPENDING'] = top_customers['TOTAL_SPENDING'].apply(
                        lambda x: f"${x:,.2f}")
                    top_customers['AVG_ORDER_VALUE'] = top_customers['AVG_ORDER_VALUE'].apply(
                        lambda x: f"${x:.2f}")
                    top_customers['LAST_PURCHASE_DATE'] = pd.to_datetime(
                        top_customers['LAST_PURCHASE_DATE']).dt.strftime('%Y-%m-%d')

                    display_customers = top_customers[['CUSTOMER_ID', 'SEGMENT', 'PURCHASE_FREQUENCY',
                                                       'TOTAL_SPENDING', 'AVG_ORDER_VALUE',
                                                       'DAYS_SINCE_LAST_PURCHASE', 'LAST_PURCHASE_DATE']]

                    display_customers.columns = ['Customer ID', 'Segment', 'Orders', 'Total Spent',
                                                 'Avg Order Value', 'Days Since Last', 'Last Purchase']

                    st.dataframe(
                        display_customers,
                        width='stretch',
                        hide_index=True,
                        height=400
                    )

                    # CLV insights
                    avg_clv = filtered_customers['TOTAL_SPENDING'].mean()
                    top_10_percent_clv = filtered_customers.nlargest(
                        int(len(filtered_customers) * 0.1), 'TOTAL_SPENDING')['TOTAL_SPENDING'].sum()
                    total_clv = filtered_customers['TOTAL_SPENDING'].sum()

                    st.info(f"""
                    💡 **CLV Insights:** 
                    • Average CLV: ${avg_clv:,.2f} | 
                    • Top 10% contribute: ${top_10_percent_clv:,.2f} ({(top_10_percent_clv/total_clv*100):.1f}% of total revenue) | 
                    • Total Customer Value: ${total_clv:,.2f}
                    """)
                else:
                    st.warning("No customers match the selected criteria")
            else:
                st.warning("No customer data available")
        else:
            st.info("👆 Please select a valid date range")

    # Footer
    st.markdown("---")
    st.caption(
        f"💡 Dashboard updated in real-time | Last refreshed: {datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}")
