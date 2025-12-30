"""
Product Performance & Inventory Analytics Dashboard
Track product sales, inventory health, reviews, and profitability
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from db_connection import run_query, get_filter_options

def product_performance_metrics():
    st.title("📦 Product Performance & Inventory Analytics")
    st.markdown("Comprehensive product insights, inventory health, and customer satisfaction metrics")
    st.markdown("---")
    
    # ============================================
    # FILTERS SECTION
    # ============================================
    col1, col2 = st.columns(2)
    
    with col1:
        # Brand filter
        brands = ["All"] + get_filter_options("Products", "BRAND")
        selected_brand = st.selectbox("Filter by Brand", options=brands, key="product_brand")
    
    with col2:
        # Category filter
        categories = ["All"] + get_filter_options("Benchmark", "BENCHMARK_CATG")
        selected_category = st.selectbox("Filter by Category", options=categories, key="product_category")
    
    # Build filter conditions
    brand_filter = f"AND p.BRAND = '{selected_brand}'" if selected_brand != "All" else ""
    category_filter = f"AND SPLIT_PART(p.TAXONOMY, ' > ', 1) = '{selected_category}'" if selected_category != "All" else ""
    
    st.markdown("---")
    
    # ============================================
    # INVENTORY HEALTH METRICS
    # ============================================
    st.markdown("## 📊 Inventory Health Dashboard")
    
    inventory_query = f"""
    WITH InventoryMetrics AS (
        SELECT
            COUNT(DISTINCT p.ITEM_ID) as total_products,
            SUM(CASE WHEN a.AVAILABILITY_INDICATOR = 'IN_STOCK' THEN 1 ELSE 0 END) as in_stock,
            SUM(CASE WHEN a.AVAILABILITY_INDICATOR = 'OUT_OF_STOCK' THEN 1 ELSE 0 END) as out_of_stock,
            SUM(CASE WHEN a.AVAILABILITY_INDICATOR = 'LIMITED_STOCK' THEN 1 ELSE 0 END) as limited_stock,
            AVG(pr.PRODUCT_PRICE) as avg_price
        FROM Products p
        LEFT JOIN Availability a ON p.ITEM_ID = a.ITEM_ID
        LEFT JOIN Pricing pr ON p.ITEM_ID = pr.ITEM_ID
        WHERE 1=1 {brand_filter} {category_filter}
    ),
    SalesVelocity AS (
        SELECT
            AVG(daily_sales) as avg_daily_sales,
            SUM(daily_revenue) as total_revenue_30d
        FROM (
            SELECT 
                s.SALE_DATE,
                SUM(s.QUANTITY_SOLD) as daily_sales,
                SUM(s.TOTAL_SALE_AMOUNT) as daily_revenue
            FROM Sales s
            JOIN Products p ON s.ITEM_ID = p.ITEM_ID
            WHERE s.SALE_DATE >= CURRENT_DATE - 30
            {brand_filter} {category_filter}
            GROUP BY s.SALE_DATE
        )
    )
    SELECT * FROM InventoryMetrics, SalesVelocity
    """
    
    inv_df = run_query(inventory_query)
    
    if inv_df is not None and not inv_df.empty:
        row = inv_df.iloc[0]
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            stock_rate = (row['IN_STOCK'] / row['TOTAL_PRODUCTS'] * 100) if row['TOTAL_PRODUCTS'] > 0 else 0
            st.metric(
                "✅ In-Stock Rate",
                f"{stock_rate:.1f}%",
                f"{int(row['IN_STOCK'])} products"
            )
        
        with col2:
            st.metric(
                "⚠️ Limited Stock",
                int(row['LIMITED_STOCK']),
                delta_color="off"
            )
        
        with col3:
            st.metric(
                "❌ Out of Stock",
                int(row['OUT_OF_STOCK']),
                delta_color="inverse"
            )
        
        with col4:
            st.metric(
                "📦 Avg Daily Sales",
                f"{row['AVG_DAILY_SALES']:.0f} units"
            )
        
        with col5:
            st.metric(
                "💰 Revenue (30d)",
                f"${row['TOTAL_REVENUE_30D']:,.0f}"
            )
        
        # Availability breakdown pie chart
        avail_data = pd.DataFrame({
            'Status': ['In Stock', 'Limited Stock', 'Out of Stock'],
            'Count': [row['IN_STOCK'], row['LIMITED_STOCK'], row['OUT_OF_STOCK']]
        })
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            fig_avail = px.pie(
                avail_data,
                values='Count',
                names='Status',
                title='Inventory Status Distribution',
                color='Status',
                color_discrete_map={
                    'In Stock': '#2ecc71',
                    'Limited Stock': '#f39c12',
                    'Out of Stock': '#e74c3c'
                },
                hole=0.4
            )
            fig_avail.update_traces(textposition='inside', textinfo='percent+label')
            fig_avail.update_layout(height=350, showlegend=True)
            st.plotly_chart(fig_avail, width='stretch')
        
        with col2:
            st.markdown("### 🎯 Inventory Insights")
            
            if row['OUT_OF_STOCK'] > 0:
                st.error(f"⚠️ **Attention Required:** {int(row['OUT_OF_STOCK'])} products are out of stock")
            
            if row['LIMITED_STOCK'] > 0:
                st.warning(f"📦 **Restock Soon:** {int(row['LIMITED_STOCK'])} products have limited stock")
            
            if stock_rate >= 90:
                st.success(f"✅ **Excellent Stock Health:** {stock_rate:.1f}% in-stock rate")
            elif stock_rate >= 75:
                st.info(f"👍 **Good Stock Health:** {stock_rate:.1f}% in-stock rate")
            else:
                st.warning(f"⚠️ **Stock Needs Attention:** Only {stock_rate:.1f}% in-stock rate")
            
            # Quick stock lookup
            st.markdown("---")
            product_search = st.text_input(
                "🔍 Quick Stock Check",
                placeholder="Search product name...",
                key="quick_stock_search"
            )
            
            if product_search:
                stock_check_query = f"""
                SELECT 
                    p.PRODUCT_TITLE,
                    p.SKU,
                    a.AVAILABILITY_INDICATOR,
                    pr.PRODUCT_PRICE
                FROM Products p
                LEFT JOIN Availability a ON p.ITEM_ID = a.ITEM_ID
                LEFT JOIN Pricing pr ON p.ITEM_ID = pr.ITEM_ID
                WHERE LOWER(p.PRODUCT_TITLE) LIKE LOWER('%{product_search}%')
                {brand_filter} {category_filter}
                LIMIT 5
                """
                
                stock_results = run_query(stock_check_query)
                
                if stock_results is not None and not stock_results.empty:
                    for _, prod in stock_results.iterrows():
                        status = prod['AVAILABILITY_INDICATOR']
                        if status == 'IN_STOCK':
                            st.success(f"✅ **{prod['PRODUCT_TITLE'][:50]}** | ${prod['PRODUCT_PRICE']:.2f} | SKU: {prod['SKU']}")
                        elif status == 'LIMITED_STOCK':
                            st.warning(f"⚠️ **{prod['PRODUCT_TITLE'][:50]}** | ${prod['PRODUCT_PRICE']:.2f} | SKU: {prod['SKU']}")
                        else:
                            st.error(f"❌ **{prod['PRODUCT_TITLE'][:50]}** | ${prod['PRODUCT_PRICE']:.2f} | SKU: {prod['SKU']}")
                else:
                    st.info("No products found")
    
    st.markdown("---")
    
    # ============================================
    # TOP SELLING PRODUCTS
    # ============================================
    st.markdown("## 🏆 Top Selling Products")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        top_products_query = f"""
        SELECT
            p.PRODUCT_TITLE,
            p.BRAND,
            SUM(s.QUANTITY_SOLD) AS total_quantity_sold,
            SUM(s.TOTAL_SALE_AMOUNT) AS total_revenue,
            COUNT(DISTINCT s.SALE_ID) AS total_orders,
            AVG(s.SALE_PRICE) AS avg_sale_price,
            COALESCE(AVG(r.ITEM_REVIEW_RATING), 0) AS avg_rating
        FROM Sales s
        JOIN Products p ON s.ITEM_ID = p.ITEM_ID
        LEFT JOIN Reviews r ON p.ITEM_ID = r.ITEM_ID
        WHERE s.SALE_DATE >= CURRENT_DATE - 90
        {brand_filter} {category_filter}
        GROUP BY p.PRODUCT_TITLE, p.BRAND
        ORDER BY total_quantity_sold DESC
        LIMIT 15
        """
        
        top_df = run_query(top_products_query)
        
        if top_df is not None and not top_df.empty:
            fig = go.Figure()
            
            # Add bars for quantity sold
            fig.add_trace(go.Bar(
                x=top_df['PRODUCT_TITLE'].str[:30] + '...',
                y=top_df['TOTAL_QUANTITY_SOLD'],
                name='Units Sold',
                marker_color='#3498db',
                text=top_df['TOTAL_QUANTITY_SOLD'],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Units Sold: %{y:,}<br>Revenue: $%{customdata[0]:,.0f}<extra></extra>',
                customdata=top_df[['TOTAL_REVENUE']]
            ))
            
            fig.update_layout(
                title='Top 15 Products by Quantity Sold (Last 90 Days)',
                xaxis_title='',
                yaxis_title='Units Sold',
                height=450,
                xaxis_tickangle=-45,
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, width='stretch')
    
    with col2:
        if top_df is not None and not top_df.empty:
            st.markdown("### 📊 Top 3 Bestsellers")
            
            for idx, row in top_df.head(3).iterrows():
                rank = ["🥇", "🥈", "🥉"][idx]
                st.markdown(f"#### {rank} {row['PRODUCT_TITLE'][:40]}")
                
                metric_col1, metric_col2 = st.columns(2)
                with metric_col1:
                    st.metric("Units", f"{int(row['TOTAL_QUANTITY_SOLD']):,}")
                    st.metric("Revenue", f"${row['TOTAL_REVENUE']:,.0f}")
                with metric_col2:
                    st.metric("Orders", f"{int(row['TOTAL_ORDERS']):,}")
                    st.metric("Rating", f"{row['AVG_RATING']:.2f}⭐")
                
                st.markdown("---")
    
    st.markdown("---")
    
    # ============================================
    # PRODUCT PROFITABILITY MATRIX
    # ============================================
    st.markdown("## 💰 Product Profitability Matrix")
    st.markdown("Analyze products based on revenue performance and sales volume")
    
    profitability_query = f"""
    SELECT 
        p.PRODUCT_TITLE,
        p.BRAND,
        SUM(s.TOTAL_SALE_AMOUNT) as revenue,
        SUM(s.QUANTITY_SOLD) as units_sold,
        AVG(s.SALE_PRICE) as avg_price,
        COUNT(DISTINCT s.SALE_ID) as orders,
        COALESCE(AVG(r.ITEM_REVIEW_RATING), 0) as avg_rating,
        SUM(s.TOTAL_SALE_AMOUNT) / NULLIF(SUM(s.QUANTITY_SOLD), 0) as revenue_per_unit
    FROM Sales s
    JOIN Products p ON s.ITEM_ID = p.ITEM_ID
    LEFT JOIN Reviews r ON p.ITEM_ID = r.ITEM_ID
    WHERE s.SALE_DATE >= CURRENT_DATE - 90
    {brand_filter} {category_filter}
    GROUP BY p.PRODUCT_TITLE, p.BRAND
    HAVING SUM(s.QUANTITY_SOLD) > 0
    ORDER BY revenue DESC
    LIMIT 100
    """
    
    prof_df = run_query(profitability_query)
    
    if prof_df is not None and not prof_df.empty:
        # Create bubble chart
        fig = px.scatter(
            prof_df.head(50),
            x='UNITS_SOLD',
            y='REVENUE',
            size='AVG_RATING',
            color='AVG_PRICE',
            hover_name='PRODUCT_TITLE',
            hover_data={
                'BRAND': True,
                'REVENUE': ':$,.0f',
                'UNITS_SOLD': ':,',
                'AVG_RATING': ':.2f',
                'AVG_PRICE': ':$,.2f',
                'ORDERS': ':,'
            },
            labels={
                'UNITS_SOLD': 'Units Sold (Last 90 Days)',
                'REVENUE': 'Total Revenue ($)',
                'AVG_PRICE': 'Avg Price ($)',
                'AVG_RATING': 'Rating'
            },
            title='Product Performance: Revenue vs Volume (Bubble size = Rating)',
            color_continuous_scale='Viridis',
            size_max=40
        )
        
        # Add quadrant lines
        median_revenue = prof_df['REVENUE'].median()
        median_units = prof_df['UNITS_SOLD'].median()
        
        fig.add_hline(
            y=median_revenue,
            line_dash="dash",
            line_color="gray",
            annotation_text="Median Revenue",
            annotation_position="right"
        )
        
        fig.add_vline(
            x=median_units,
            line_dash="dash",
            line_color="gray",
            annotation_text="Median Volume",
            annotation_position="top"
        )
        
        fig.update_layout(height=550, plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, width='stretch')
        
        # Quadrant analysis
        col1, col2, col3, col4 = st.columns(4)
        
        high_rev_high_vol = len(prof_df[(prof_df['REVENUE'] >= median_revenue) & (prof_df['UNITS_SOLD'] >= median_units)])
        high_rev_low_vol = len(prof_df[(prof_df['REVENUE'] >= median_revenue) & (prof_df['UNITS_SOLD'] < median_units)])
        low_rev_high_vol = len(prof_df[(prof_df['REVENUE'] < median_revenue) & (prof_df['UNITS_SOLD'] >= median_units)])
        low_rev_low_vol = len(prof_df[(prof_df['REVENUE'] < median_revenue) & (prof_df['UNITS_SOLD'] < median_units)])
        
        with col1:
            st.metric("⭐ Stars (High Rev/High Vol)", high_rev_high_vol)
            st.caption("Best performers - invest more")
        
        with col2:
            st.metric("💎 Premium (High Rev/Low Vol)", high_rev_low_vol)
            st.caption("High-value items")
        
        with col3:
            st.metric("🔄 Volume (Low Rev/High Vol)", low_rev_high_vol)
            st.caption("Popular but low margin")
        
        with col4:
            st.metric("⚠️ Question Marks", low_rev_low_vol)
            st.caption("Needs evaluation")
        
        st.info(f"💡 **Strategic Insight:** You have {high_rev_high_vol} star products generating high revenue with strong volume. Focus on maintaining inventory and marketing for these items.")
    
    st.markdown("---")
    
    # ============================================
    # AVERAGE SALE PRICE ANALYSIS
    # ============================================
    st.markdown("## 💰 Price Analysis & Distribution")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        avg_price_query = f"""
        SELECT
            p.PRODUCT_TITLE,
            p.BRAND,
            AVG(s.SALE_PRICE) AS avg_sale_price,
            COUNT(s.SALE_ID) AS total_sales,
            MIN(s.SALE_PRICE) AS min_price,
            MAX(s.SALE_PRICE) AS max_price,
            STDDEV(s.SALE_PRICE) AS price_stddev
        FROM Sales s
        JOIN Products p ON s.ITEM_ID = p.ITEM_ID
        WHERE s.SALE_DATE >= CURRENT_DATE - 90
        {brand_filter} {category_filter}
        GROUP BY p.PRODUCT_TITLE, p.BRAND
        ORDER BY avg_sale_price DESC
        LIMIT 30
        """
        
        avg_price_df = run_query(avg_price_query)
        
        if avg_price_df is not None and not avg_price_df.empty:
            # Filter controls
            search_term = st.text_input(
                "🔍 Search Products",
                placeholder="Enter product name...",
                key="price_search"
            )
            
            filtered_df = avg_price_df.copy()
            
            if search_term:
                filtered_df = filtered_df[filtered_df['PRODUCT_TITLE'].str.contains(search_term, case=False, na=False)]
            
            # Price range filter
            min_price_filter, max_price_filter = st.slider(
                "Filter by Average Price Range",
                min_value=float(avg_price_df['AVG_SALE_PRICE'].min()),
                max_value=float(avg_price_df['AVG_SALE_PRICE'].max()),
                value=(float(avg_price_df['AVG_SALE_PRICE'].min()), float(avg_price_df['AVG_SALE_PRICE'].max())),
                key="price_range_slider"
            )
            
            filtered_df = filtered_df[
                (filtered_df['AVG_SALE_PRICE'] >= min_price_filter) &
                (filtered_df['AVG_SALE_PRICE'] <= max_price_filter)
            ]
            
            if not filtered_df.empty:
                # Limit display
                num_products = st.slider("Number of products to display", 5, 30, 15, key="price_display_count")
                display_df = filtered_df.head(num_products)
                
                # Calculate error ranges for min-max
                display_df['ERROR_MINUS'] = display_df['AVG_SALE_PRICE'] - display_df['MIN_PRICE']
                display_df['ERROR_PLUS'] = display_df['MAX_PRICE'] - display_df['AVG_SALE_PRICE']
                
                # Create bar chart with error bars
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    x=display_df['PRODUCT_TITLE'].str[:30] + '...',
                    y=display_df['AVG_SALE_PRICE'],
                    name='Avg Price',
                    error_y=dict(
                        type='data',
                        symmetric=False,
                        array=display_df['ERROR_PLUS'],
                        arrayminus=display_df['ERROR_MINUS'],
                        color='rgba(255, 0, 0, 0.3)',
                        thickness=1.5,
                        width=4,
                    ),
                    marker=dict(
                        color=display_df['TOTAL_SALES'],
                        colorscale='Blues',
                        showscale=True,
                        colorbar=dict(title="Sales Count")
                    ),
                    text=display_df['AVG_SALE_PRICE'].round(2),
                    textposition='outside',
                    hovertemplate='<b>%{x}</b><br>Avg: $%{y:.2f}<br>Range: $%{customdata[0]:.2f} - $%{customdata[1]:.2f}<br>Sales: %{customdata[2]}<extra></extra>',
                    customdata=display_df[['MIN_PRICE', 'MAX_PRICE', 'TOTAL_SALES']]
                ))
                
                fig.update_layout(
                    title="Product Pricing: Average with Min-Max Range",
                    xaxis_title='',
                    yaxis_title='Price ($)',
                    height=500,
                    xaxis_tickangle=-45,
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                
                st.plotly_chart(fig, width='stretch')
            else:
                st.warning("No products match your search criteria")
    
    with col2:
        if avg_price_df is not None and not avg_price_df.empty:
            st.markdown("### 📊 Price Statistics")
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Highest Avg Price", f"${avg_price_df['AVG_SALE_PRICE'].max():.2f}")
                st.metric("Lowest Avg Price", f"${avg_price_df['AVG_SALE_PRICE'].min():.2f}")
            with col_b:
                st.metric("Mean Price", f"${avg_price_df['AVG_SALE_PRICE'].mean():.2f}")
                st.metric("Median Price", f"${avg_price_df['AVG_SALE_PRICE'].median():.2f}")
            
            st.markdown("---")
            st.markdown("### 📈 Price Distribution")
            
            # Price distribution histogram
            fig_dist = px.histogram(
                avg_price_df,
                x='AVG_SALE_PRICE',
                nbins=20,
                labels={'AVG_SALE_PRICE': 'Average Sale Price ($)'},
                color_discrete_sequence=['#3498db']
            )
            fig_dist.update_layout(
                height=300,
                showlegend=False,
                yaxis_title='Number of Products',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_dist, width='stretch')
            
            # Price categories
            st.markdown("### 💵 Price Segments")
            price_segments = pd.cut(
                avg_price_df['AVG_SALE_PRICE'],
                bins=[0, 50, 100, 200, float('inf')],
                labels=['Budget (<$50)', 'Mid-range ($50-100)', 'Premium ($100-200)', 'Luxury (>$200)']
            ).value_counts()
            
            for segment, count in price_segments.items():
                st.metric(segment, count)
    
    st.markdown("---")
    
    # ============================================
    # PRODUCT REVIEW INSIGHTS
    # ============================================
    st.markdown("## ⭐ Customer Reviews & Ratings Analysis")
    
    review_query = f"""
    SELECT
        p.PRODUCT_TITLE,
        p.BRAND,
        AVG(r.ITEM_REVIEW_RATING) AS avg_rating,
        SUM(r.ITEM_REVIEW_COUNT) AS total_reviews,
        COUNT(DISTINCT p.ITEM_ID) AS product_count,
        AVG(pr.PRODUCT_PRICE) as avg_price
    FROM Reviews r
    JOIN Products p ON r.ITEM_ID = p.ITEM_ID
    LEFT JOIN Pricing pr ON p.ITEM_ID = pr.ITEM_ID
    WHERE 1=1 {brand_filter} {category_filter}
    GROUP BY p.PRODUCT_TITLE, p.BRAND
    HAVING AVG(r.ITEM_REVIEW_RATING) IS NOT NULL
    ORDER BY avg_rating DESC, total_reviews DESC
    """
    
    review_df = run_query(review_query)
    
    if review_df is not None and not review_df.empty:
        # Key metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        avg_overall = review_df['AVG_RATING'].mean()
        total_products = len(review_df)
        highly_rated = len(review_df[review_df['AVG_RATING'] >= 4.0])
        total_reviews = int(review_df['TOTAL_REVIEWS'].sum())
        poorly_rated = len(review_df[review_df['AVG_RATING'] < 3.0])
        
        with col1:
            st.metric("📊 Overall Avg Rating", f"{avg_overall:.2f}⭐")
        
        with col2:
            st.metric("🏆 Highest Rated", f"{review_df['AVG_RATING'].max():.2f}⭐")
        
        with col3:
            st.metric("✅ Highly Rated (≥4.0)", f"{highly_rated}/{total_products}")
        
        with col4:
            st.metric("📝 Total Reviews", f"{total_reviews:,}")
        
        with col5:
            st.metric("⚠️ Needs Attention (<3.0)", poorly_rated, delta_color="inverse")
        
        st.markdown("---")
        
        # Visualizations
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.markdown("### 📊 Rating vs Review Volume")
            
            # Scatter plot
            fig_scatter = px.scatter(
                review_df.head(50),
                x='AVG_RATING',
                y='TOTAL_REVIEWS',
                size='TOTAL_REVIEWS',
                color='AVG_RATING',
                hover_name='PRODUCT_TITLE',
                hover_data={
                    'BRAND': True,
                    'AVG_RATING': ':.2f',
                    'TOTAL_REVIEWS': ':,',
                    'AVG_PRICE': ':$.2f'
                },
                labels={
                    'AVG_RATING': 'Average Rating',
                    'TOTAL_REVIEWS': 'Number of Reviews'
                },
                color_continuous_scale='RdYlGn',
                size_max=50
            )
            
            # Add threshold lines
            fig_scatter.add_hline(
                y=review_df['TOTAL_REVIEWS'].median(),
                line_dash="dash",
                line_color="gray",
                annotation_text="Median Reviews"
            )
            fig_scatter.add_vline(
                x=4.0,
                line_dash="dash",
                line_color="orange",
                annotation_text="4.0 Threshold"
            )
            
            fig_scatter.update_layout(
                height=400,
                xaxis_range=[review_df['AVG_RATING'].min() - 0.2, 5.2],
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig_scatter, width='stretch')
            
            # Insight
            high_rating_high_reviews = len(review_df[
                (review_df['AVG_RATING'] >= 4.0) &
                (review_df['TOTAL_REVIEWS'] >= review_df['TOTAL_REVIEWS'].median())
            ])
            
            st.success(f"💡 **Star Performers:** {high_rating_high_reviews} products have both high ratings (≥4.0) AND above-median review counts!")
        
        with col2:
            st.markdown("### 🎯 Rating Distribution")
            
            # Create rating categories
            review_df['RATING_CATEGORY'] = pd.cut(
                review_df['AVG_RATING'],
                bins=[0, 2, 3, 4, 5],
                labels=['Poor (0-2)', 'Fair (2-3)', 'Good (3-4)', 'Excellent (4-5)']
            )
            
            rating_dist = review_df['RATING_CATEGORY'].value_counts().sort_index()
            
            # Donut chart
            fig_pie = go.Figure(data=[go.Pie(
                labels=rating_dist.index,
                values=rating_dist.values,
                hole=0.5,
                marker=dict(colors=['#e74c3c', '#f39c12', '#3498db', '#2ecc71']),
                textinfo='label+percent',
                textposition='auto',
                hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
            )])
            
            fig_pie.update_layout(
                height=400,
                showlegend=True,
                legend=dict(orientation="v", yanchor="middle", y=0.5)
            )
            
            st.plotly_chart(fig_pie, width='stretch')
        
        st.markdown("---")
        
        # Top and Bottom Performers
        st.markdown("### 🏆 Review Performance Leaders")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### ⭐ Top 10 Best Rated Products")
            
            top_10 = review_df.head(10).copy()
            
            # Create horizontal bar chart
            fig_top = go.Figure(go.Bar(
                x=top_10['AVG_RATING'],
                y=top_10['PRODUCT_TITLE'].str[:40] + '...',
                orientation='h',
                marker=dict(
                    color=top_10['AVG_RATING'],
                    colorscale='Greens',
                    showscale=False
                ),
                text=top_10['AVG_RATING'].round(2),
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>Rating: %{x:.2f}⭐<br>Reviews: %{customdata}<extra></extra>',
                customdata=top_10['TOTAL_REVIEWS']
            ))
            
            fig_top.update_layout(
                height=400,
                xaxis_range=[0, 5.5],
                xaxis_title="Rating",
                yaxis_title="",
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig_top, width='stretch')
        
        with col2:
            st.markdown("#### ⚠️ Bottom 10 Products (Need Improvement)")
            
            bottom_10 = review_df.tail(10).copy()
            
            # Create horizontal bar chart
            fig_bottom = go.Figure(go.Bar(
                x=bottom_10['AVG_RATING'],
                y=bottom_10['PRODUCT_TITLE'].str[:40] + '...',
                orientation='h',
                marker=dict(
                    color=bottom_10['AVG_RATING'],
                    colorscale='Reds',
                    showscale=False
                ),
                text=bottom_10['AVG_RATING'].round(2),
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>Rating: %{x:.2f}⭐<br>Reviews: %{customdata}<extra></extra>',
                customdata=bottom_10['TOTAL_REVIEWS']
            ))
            
            fig_bottom.update_layout(
                height=400,
                xaxis_range=[0, 5.5],
                xaxis_title="Rating",
                yaxis_title="",
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig_bottom, width='stretch')
        
        st.markdown("---")
        
        # Interactive search and filter
        st.markdown("### 🔍 Search Product Reviews")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_product = st.text_input(
                "Search by product or brand",
                placeholder="e.g., Samsung, iPhone, Laptop...",
                key="review_search"
            )
        
        with col2:
            min_rating = st.slider(
                "Minimum Rating",
                min_value=0.0,
                max_value=5.0,
                value=0.0,
                step=0.1,
                key="min_rating_filter"
            )
        
        with col3:
            min_reviews = st.number_input(
                "Minimum Review Count",
                min_value=0,
                value=0,
                step=10,
                key="min_reviews_filter"
            )
        
        # Apply filters
        filtered_reviews = review_df.copy()
        
        if search_product:
            filtered_reviews = filtered_reviews[
                (filtered_reviews['PRODUCT_TITLE'].str.contains(search_product, case=False, na=False)) |
                (filtered_reviews['BRAND'].str.contains(search_product, case=False, na=False))
            ]
        
        filtered_reviews = filtered_reviews[
            (filtered_reviews['AVG_RATING'] >= min_rating) &
            (filtered_reviews['TOTAL_REVIEWS'] >= min_reviews)
        ]
        
        if not filtered_reviews.empty:
            st.success(f"✅ Found {len(filtered_reviews)} products matching criteria")
            
            # Display table
            display_cols = filtered_reviews[['PRODUCT_TITLE', 'BRAND', 'AVG_RATING', 'TOTAL_REVIEWS', 'AVG_PRICE']].copy()
            display_cols['AVG_RATING'] = display_cols['AVG_RATING'].round(2)
            display_cols['AVG_PRICE'] = display_cols['AVG_PRICE'].apply(lambda x: f"${x:.2f}")
            display_cols.columns = ['Product', 'Brand', 'Avg Rating ⭐', 'Total Reviews', 'Avg Price']
            
            st.dataframe(
                display_cols,
                width='stretch',
                hide_index=True,
                height=400
            )
        else:
            st.warning("⚠️ No products match the selected criteria")
    
    else:
        st.warning("No review data available")
    
    # Footer
    st.markdown("---")
    st.caption(f"💡 Dashboard updated in real-time | Last refreshed: {datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}")
