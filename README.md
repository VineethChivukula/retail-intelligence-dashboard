# Retail Intelligence Hub 📊

A professional, enterprise-grade retail analytics platform built with Streamlit and Snowflake. Features real-time business intelligence, competitive benchmarking, customer insights, and AI-powered natural language queries—all with a modern dark-themed interface.

---

## ✨ Features

### 📈 **Sales Performance Dashboard**

- **Key Performance Indicators (KPIs)**
  - Total Revenue with period-over-period growth
  - Average Order Value (AOV) tracking
  - Conversion Rate analysis
  - Customer metrics and discount analytics
- **Advanced Analytics**
  - Daily sales trends with 7-day moving averages
  - Sales by day of week analysis
  - Category and brand performance comparison
  - Merchant performance breakdown with profitability metrics
- **Interactive Visualizations**
  - Dual-axis charts (Revenue + Orders)
  - Dynamic pie charts for revenue distribution
  - Top performing products with review ratings
  - Customizable date range filtering

### 📦 **Product Performance & Inventory Analytics**

- **Inventory Health Dashboard**
  - Real-time stock status monitoring (In-Stock, Limited, Out-of-Stock)
  - Average daily sales velocity
  - 30-day revenue tracking
  - Quick stock lookup with search
- **Product Profitability Matrix**
  - Revenue vs. Volume bubble charts
  - Quadrant analysis (Stars, Premium, Volume, Question Marks)
  - Strategic insights for inventory optimization
- **Pricing Analysis**
  - Price distribution with min-max ranges
  - Price segmentation (Budget, Mid-range, Premium, Luxury)
  - Average sale price trends with error bars
- **Customer Review Intelligence**
  - Rating vs. Review volume analysis
  - Top/Bottom performer identification
  - Sentiment distribution (Poor, Fair, Good, Excellent)
  - Advanced filtering by rating and review count

### 💰 **Benchmarking & Customer Insights**

- **Competitive Price Intelligence**
  - Real-time price comparison vs. competitors
  - Price positioning scatter plots
  - Gap analysis with percentage differences
  - Multi-store and brand filtering
- **Competitor Trend Analysis**
  - Historical pricing trends across stores
  - Category-level price distribution
  - Market share visualization with sunburst charts
- **Customer Behavior Analytics**
  - Payment method preferences with revenue breakdown
  - RFM (Recency, Frequency, Monetary) segmentation
  - Customer Lifetime Value (CLV) analysis
  - Customer quadrant analysis (VIP, Frequent Buyers, High Spenders, Occasional)
  - Top customer identification and filtering

### 🤖 **AI Data Assistant (Cortex Analyst)**

- **Natural Language Queries**
  - Ask questions in plain English
  - AI-powered SQL generation
  - Automatic data visualization
- **Smart Features**
  - Row limiting for performance (max 1,000 display, 10,000 query limit)
  - CSV export for large datasets
  - Interactive tabs (Data Table, Line Chart, Bar Chart)
  - SQL query inspection
- **Dark-Themed Chat Interface**
  - Gradient user messages
  - Dark data tables with amber accents
  - Responsive design

---

## 🎨 Design & User Experience

### **Modern Dark Theme**

- Dynamic color schemes per dashboard:
  - 🟢 **Sales Performance**: Green (#10b981) - Growth & Revenue
  - 🔵 **Product Analytics**: Blue (#3b82f6) - Data Analysis
  - 🟣 **Benchmarking**: Purple (#8b5cf6) - Premium Intelligence
  - 🟠 **AI Assistant**: Amber (#f59e0b) - Intelligent Insights

### **Professional UI Elements**

- Smooth transitions and hover effects
- Gradient accents and glowing selected states
- Dark sidebar with custom scrollbar
- Live status indicator with pulse animation
- Responsive layout optimized for wide screens

---

## 🛠️ Tech Stack

| Component              | Technology                                                                                                          |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------- |
| **Frontend Framework** | [Streamlit](https://streamlit.io/)                                                                          |
| **Data Warehouse**     | [Snowflake](https://www.snowflake.com/)                                                                             |
| **Data Processing**    | [Pandas](https://pandas.pydata.org/)                                                                          |
| **Visualizations**     | [Plotly Express & Graph Objects](https://plotly.com/)                                                    |
| **Database Connector** | [snowflake-connector-python](https://docs.snowflake.com/en/developer-guide/python-connector/python-connector) |
| **Navigation**         | [streamlit-option-menu](https://github.com/victoryhb/streamlit-option-menu)                                |
| **Environment Config** | [python-dotenv](https://python-dotenv.readthedocs.io/)                                                     |
| **AI Integration**     | Snowflake Cortex Analyst API                                                                                        |

---

## 🚀 Installation

### **Prerequisites**

- Python 3.8 or higher
- Snowflake account with appropriate credentials
- Active Snowflake warehouse
- Cortex Analyst semantic model (for AI features)

### **Quick Start**

1. **Clone the repository**

```bash
git clone <repository-url>
cd retail-intelligence-hub
```

2. **Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Create a `.env` file in the project root:

```
# Snowflake Connection
USER=your_snowflake_username
PASSWORD=your_snowflake_password
ACCOUNT=your_account_identifier
WAREHOUSE=your_warehouse_name
DATABASE=your_database_name
SCHEMA=your_schema_name

# Cortex Analyst Configuration
HOST=your_account.snowflakecomputing.com
SEMANTIC_VIEW=your_semantic_model_name
```

5. **Launch the dashboard**

```bash
streamlit run dashboard.py
```

The dashboard will open at `http://localhost:8501`

---

## 📁 Project Structure

```
retail-intelligence-hub/
├── dashboard.py                              # Main navigation with dynamic theming
├── db_connection.py                          # Centralized database connection (NEW)
├── sales_performance_metrics.py              # Sales analytics with KPIs
├── product_performance_metrics.py            # Product & inventory intelligence
├── benchmarking_and_customer_insights.py     # Competitive & customer analytics
├── cortex_analyst.py                         # AI chat interface with row limiting
├── requirements.txt                          # Python dependencies
├── .env                                      # Environment variables (not in git)
├── .env.example                              # Environment template
├── .gitignore                                # Git ignore rules
└── README.md                                 # This file
```

---

## 🔧 Key Components

### **db_connection.py** ⭐ NEW

Centralized database management for optimized performance:

- Singleton connection with `@st.cache_resource`
- Query caching with 1-hour TTL via `@st.cache_data`
- Error handling and graceful degradation
- Helper functions for filter options

### **dashboard.py**

Main navigation hub with advanced features:

- Dynamic theme switching per dashboard
- Dark-themed sidebar with gradient accents
- Real-time status indicator
- Collapsible help section
- Professional footer with branding

### **sales_performance_metrics.py**

Comprehensive sales intelligence:

- Period-over-period comparison engine
- Multi-dimensional filtering (Brand, Category, Merchant, Date)
- Dual-axis trend charts
- Top product identification
- Merchant profitability analysis

### **product_performance_metrics.py**

Product and inventory optimization:

- Inventory health scoring
- Profitability matrix with quadrant analysis
- Pricing analysis with statistical insights
- Review sentiment analysis
- Search and advanced filtering

### **benchmarking_and_customer_insights.py**

Competitive intelligence and customer analytics:

- Price positioning vs. competitors
- Competitor trend tracking
- Payment method analysis
- RFM customer segmentation
- CLV calculation and insights

### **cortex_analyst.py**

AI-powered natural language interface:

- Natural language to SQL conversion
- Automatic row limiting (1,000 display / 10,000 query)
- CSV export for large datasets
- Dark-themed data tables and charts
- Interactive suggestion prompts

---

## 🗄️ Database Schema

The platform connects to the following Snowflake tables:

### **Core Tables**

```sql
-- Products catalog
CREATE TABLE Products (
    ITEM_ID INT AUTOINCREMENT PRIMARY KEY,
    ITEM_NAME VARCHAR(255),
    PRODUCT_TITLE VARCHAR(255),
    MODEL VARCHAR(100),
    SKU VARCHAR(100),
    TAXONOMY VARCHAR(255),
    WEIGHTS_AND_DIMENSIONS VARCHAR(100),
    BRAND VARCHAR(100),
    COMPANY_NAME VARCHAR(255)
);

-- Product availability status
CREATE TABLE Availability (
    ITEM_ID INT,
    AVAILABILITY_INDICATOR VARCHAR(50),
    PRIMARY KEY (ITEM_ID),
    FOREIGN KEY (ITEM_ID) REFERENCES Products(ITEM_ID)
);

-- Competitive benchmark data
CREATE TABLE Benchmark (
    BENCHMARK_ID INT AUTOINCREMENT PRIMARY KEY,
    BENCHMARK_BRAND_NAME VARCHAR(255),
    BENCHMARK_CATG VARCHAR(100),
    BENCHMARK_CATG_ID VARCHAR(50),
    BENCHMARK_COLOR_DESC VARCHAR(50),
    BENCHMARK_DEPT VARCHAR(255),
    BENCHMARK_ITEM_ATTRIBS VARCHAR(500),
    BENCHMARK_ITEM_MDL_NUM VARCHAR(100),
    BENCHMARK_ITEM_SUB_DESC VARCHAR(255),
    BENCHMARK_STORE VARCHAR(255),
    BENCHMARK_SUBCATG VARCHAR(100),
    BENCHMARK_UPC_NUM VARCHAR(100)
);

-- Pricing and benchmarks
CREATE TABLE Pricing (
    ITEM_ID INT,
    PRODUCT_PRICE FLOAT,
    PRICE_SCRAPE_DATE DATE,
    BENCHMARK_ID INT,
    BENCHMARK_BASE_PRICE FLOAT,
    BENCHMARK_SITE_PRICE FLOAT,
    PRIMARY KEY (ITEM_ID, BENCHMARK_ID),
    FOREIGN KEY (ITEM_ID) REFERENCES Products(ITEM_ID),
    FOREIGN KEY (BENCHMARK_ID) REFERENCES Benchmark(BENCHMARK_ID)
);

-- Customer reviews
CREATE TABLE Reviews (
    ITEM_ID INT,
    ITEM_REVIEW_COUNT INT,
    ITEM_REVIEW_RATING FLOAT,
    PRIMARY KEY (ITEM_ID),
    FOREIGN KEY (ITEM_ID) REFERENCES Products(ITEM_ID)
);

-- Third-party merchants
CREATE TABLE Third_Party_Merchants (
    MERCHANT_ID INT AUTOINCREMENT PRIMARY KEY,
    THIRD_PARTY_MERCHANT_NAME VARCHAR(255)
);

-- Product-Merchant mapping
CREATE TABLE Product_Merchant_Mapping (
    ITEM_ID INT,
    MERCHANT_ID INT,
    PRIMARY KEY (ITEM_ID, MERCHANT_ID),
    FOREIGN KEY (ITEM_ID) REFERENCES Products(ITEM_ID),
    FOREIGN KEY (MERCHANT_ID) REFERENCES Third_Party_Merchants(MERCHANT_ID)
);

-- Sales transactions
CREATE TABLE Sales (
    SALE_ID INT AUTOINCREMENT PRIMARY KEY,
    ITEM_ID INT,
    MERCHANT_ID INT,
    SALE_DATE DATE,
    QUANTITY_SOLD INT,
    SALE_PRICE FLOAT,
    TOTAL_SALE_AMOUNT FLOAT,
    DISCOUNT_APPLIED FLOAT,
    CUSTOMER_ID INT,
    PAYMENT_METHOD VARCHAR(50),
    FOREIGN KEY (ITEM_ID) REFERENCES Products(ITEM_ID),
    FOREIGN KEY (MERCHANT_ID) REFERENCES Third_Party_Merchants(MERCHANT_ID)
);
```

---

## 🎯 Key Capabilities

### **Performance Optimization**

- ✅ Centralized database connection pooling
- ✅ Query result caching (1-hour TTL)
- ✅ Lazy loading with conditional rendering
- ✅ Row limiting for large datasets (max 1,000 rows display)
- ✅ Automatic SQL LIMIT injection for safety
- ✅ CSV export for offline analysis

### **Advanced Analytics**

- ✅ Period-over-period growth calculations
- ✅ Moving averages for trend smoothing
- ✅ Quadrant analysis for strategic insights
- ✅ RFM customer segmentation
- ✅ Customer Lifetime Value (CLV) modeling
- ✅ Price positioning analysis

### **User Experience**

- ✅ Responsive dark theme with dynamic colors
- ✅ Interactive filters with multi-select
- ✅ Real-time data updates
- ✅ Comprehensive error handling
- ✅ Pagination for large datasets
- ✅ Export capabilities (CSV download)

### **Data Visualization**

- ✅ Plotly interactive charts
- ✅ Dual-axis trend analysis
- ✅ Bubble charts for multi-dimensional data
- ✅ Sunburst charts for hierarchical data
- ✅ Custom color schemes per dashboard
- ✅ Hover tooltips with detailed info

---

## 🔒 Security Best Practices

⚠️ **Important Security Notes:**

1. **Never commit `.env` file** - Contains sensitive credentials
2. **Use environment variables** - All sensitive data in `.env`
3. **Role-based access** - Implement Snowflake RBAC
4. **Warehouse management** - Auto-suspend unused warehouses
5. **Query limits** - Automatic row limiting prevents excessive data pulls

### **.gitignore Configuration**

```
.env
__pycache__/
*.pyc
.streamlit/
venv/
```

---

## 🐛 Troubleshooting

### **Connection Issues**

```bash
# Verify Snowflake credentials
cat .env | grep USER

# Test connection
python -c "from db_connection import init_connection; init_connection()"

# Check network/firewall
ping your_account.snowflakecomputing.com
```

### **Performance Issues**

- **Clear cache**: Remove `.streamlit/cache/` directory
- **Increase warehouse size**: Upgrade to MEDIUM or LARGE
- **Optimize queries**: Review SQL execution plans
- **Reduce date ranges**: Filter to smaller time periods

### **Data Not Loading**

- Verify table names match schema exactly
- Check user permissions: `SHOW GRANTS TO USER your_user;`
- Ensure warehouse is running: `SHOW WAREHOUSES;`
- Review query logs in Snowflake UI

### **AI Assistant Issues**

- Verify `SEMANTIC_VIEW` is created and accessible
- Check Cortex Analyst is enabled for your account
- Ensure token permissions are correct
- Review API timeout settings (default: 30s)

---

## 📊 Dashboard Metrics Reference

### **Sales Performance KPIs**

| Metric                | Calculation                               | Purpose                   |
| --------------------- | ----------------------------------------- | ------------------------- |
| Total Revenue         | `SUM(TOTAL_SALE_AMOUNT)`                  | Overall sales performance |
| Revenue Growth %      | `((Current - Previous) / Previous) * 100` | Period comparison         |
| Avg Order Value (AOV) | `AVG(TOTAL_SALE_AMOUNT)`                  | Transaction value         |
| Conversion Rate       | `(Orders / Customers) * 100`              | Purchase efficiency       |
| Avg Discount          | `AVG(DISCOUNT_APPLIED)`                   | Promotional impact        |

### **Product Performance KPIs**

| Metric               | Purpose                    |
| -------------------- | -------------------------- |
| In-Stock Rate        | Inventory health indicator |
| Stock-to-Sales Ratio | Inventory efficiency       |
| Avg Daily Sales      | Velocity tracking          |
| Review Rating        | Customer satisfaction      |
| Price Volatility     | Pricing stability          |

---

## 🚀 Advanced Configuration

### **Custom Row Limits**

Edit `cortex_analyst.py`:

```python
MAX_DISPLAY_ROWS = 1000  # Adjust display limit
MAX_CHART_ROWS = 100     # Adjust chart limit
```

### **Cache Configuration**

Edit `db_connection.py`:

```python
@st.cache_data(ttl=3600)  # Change TTL (seconds)
def run_query(query, params=None):
        # ...
```

### **Theme Customization**

Edit `dashboard.py` `DASHBOARD_THEMES` dictionary:

```python
DASHBOARD_THEMES = {
        "Sales Performance": {
                "primary": "#your_color",
                "secondary": "#your_color",
                # ...
        }
}
```

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

**Last Updated**: January 2026  
**Maintained by**: IceQuery Crew

---

<div align="center">

**Built with ❤️ using Streamlit & Snowflake**

</div>
