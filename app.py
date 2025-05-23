import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Set page config
st.set_page_config(
    page_title="Sales Trend Explorer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_sample_data():
    """Load or create sample Superstore-like data"""
    np.random.seed(42)
    
    # Create sample data similar to Superstore dataset
    dates = pd.date_range('2021-01-01', '2023-12-31', freq='D')
    categories = ['Technology', 'Furniture', 'Office Supplies']
    subcategories = {
        'Technology': ['Phones', 'Computers', 'Accessories'],
        'Furniture': ['Chairs', 'Tables', 'Storage'],
        'Office Supplies': ['Paper', 'Binders', 'Art']
    }
    regions = ['Central', 'East', 'South', 'West']
    
    data = []
    for _ in range(5000):
        date = np.random.choice(dates)
        category = np.random.choice(categories)
        subcategory = np.random.choice(subcategories[category])
        region = np.random.choice(regions)
        
        # Generate realistic sales data
        base_sales = {'Technology': 1000, 'Furniture': 800, 'Office Supplies': 300}[category]
        sales = np.random.normal(base_sales, base_sales * 0.3)
        profit = sales * np.random.uniform(0.1, 0.3)
        quantity = np.random.randint(1, 10)
        
        data.append({
            'Order Date': date,
            'Category': category,
            'Sub-Category': subcategory,
            'Region': region,
            'Sales': max(sales, 50),
            'Profit': profit,
            'Quantity': quantity
        })
    
    df = pd.DataFrame(data)
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Year'] = df['Order Date'].dt.year
    df['Month'] = df['Order Date'].dt.month
    df['Year-Month'] = df['Order Date'].dt.to_period('M')
    
    return df

def create_line_plot(df):
    """Create monthly sales trend line plot"""
    monthly_sales = df.groupby(['Year-Month', 'Category'])['Sales'].sum().reset_index()
    monthly_sales['Year-Month'] = monthly_sales['Year-Month'].astype(str)
    
    fig = px.line(monthly_sales, x='Year-Month', y='Sales', color='Category',
                  title='Monthly Sales Trend by Category',
                  labels={'Sales': 'Sales ($)', 'Year-Month': 'Month'})
    fig.update_layout(height=500, xaxis_tickangle=45)
    return fig

def create_bar_chart(df):
    """Create category-wise sales bar chart"""
    category_sales = df.groupby('Category')['Sales'].sum().reset_index()
    
    fig = px.bar(category_sales, x='Category', y='Sales',
                 title='Total Sales by Category',
                 color='Sales',
                 color_continuous_scale='viridis')
    fig.update_layout(height=500)
    return fig

def create_heatmap(df):
    """Create sales heatmap by region and category"""
    heatmap_data = df.groupby(['Region', 'Category'])['Sales'].sum().unstack(fill_value=0)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(heatmap_data, annot=True, fmt='.0f', cmap='YlOrRd', ax=ax)
    ax.set_title('Sales Heatmap: Region vs Category')
    plt.tight_layout()
    return fig

def main():
    # Header
    st.markdown('<h1 class="main-header">📊 Sales Trend Explorer</h1>', unsafe_allow_html=True)
    st.markdown("**E-Commerce Sales Analytics Dashboard**")
    
    # Load data
    with st.spinner('Loading data...'):
        df = load_sample_data()
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Year filter
    years = sorted(df['Year'].unique())
    selected_years = st.sidebar.multiselect('Select Years', years, default=years)
    
    # Category filter
    categories = df['Category'].unique()
    selected_categories = st.sidebar.multiselect('Select Categories', categories, default=categories)
    
    # Region filter
    regions = df['Region'].unique()
    selected_regions = st.sidebar.multiselect('Select Regions', regions, default=regions)
    
    # Filter data
    filtered_df = df[
        (df['Year'].isin(selected_years)) &
        (df['Category'].isin(selected_categories)) &
        (df['Region'].isin(selected_regions))
    ]
    
    # Key Metrics
    st.header("📈 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_sales = filtered_df['Sales'].sum()
        st.metric("Total Sales", f"${total_sales:,.0f}")
    
    with col2:
        total_profit = filtered_df['Profit'].sum()
        st.metric("Total Profit", f"${total_profit:,.0f}")
    
    with col3:
        avg_order_value = filtered_df['Sales'].mean()
        st.metric("Avg Order Value", f"${avg_order_value:.2f}")
    
    with col4:
        total_orders = len(filtered_df)
        st.metric("Total Orders", f"{total_orders:,}")
    
    st.divider()
    
    # Visualizations
    st.header("📊 Sales Analysis")
    
    # Line Plot
    st.subheader("1. Monthly Sales Trend")
    if len(filtered_df) > 0:
        line_fig = create_line_plot(filtered_df)
        st.plotly_chart(line_fig, use_container_width=True)
    else:
        st.warning("No data available for selected filters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Bar Chart
        st.subheader("2. Sales by Category")
        if len(filtered_df) > 0:
            bar_fig = create_bar_chart(filtered_df)
            st.plotly_chart(bar_fig, use_container_width=True)
    
    with col2:
        # Additional insights
        st.subheader("3. Top Performing Sub-Categories")
        if len(filtered_df) > 0:
            top_subcats = filtered_df.groupby('Sub-Category')['Sales'].sum().sort_values(ascending=False).head(5)
            st.bar_chart(top_subcats)
    
    # Heatmap
    st.subheader("4. Sales Heatmap (Region vs Category)")
    if len(filtered_df) > 0:
        heatmap_fig = create_heatmap(filtered_df)
        st.pyplot(heatmap_fig)
    
    # Data Table
    st.header("📋 Data Overview")
    if st.checkbox("Show Raw Data"):
        st.dataframe(filtered_df.head(100), use_container_width=True)
    
    # Download option
    st.header("💾 Download Data")
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="Download filtered data as CSV",
        data=csv,
        file_name=f'sales_data_{datetime.now().strftime("%Y%m%d")}.csv',
        mime='text/csv'
    )
    
    # Footer
    st.divider()
    st.markdown("**Built with Streamlit** | Sales Trend Explorer v1.0")

if __name__ == "__main__":
    main()