import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
from calendar import month_name
from utils import load_data, to_excel

#  Setting the vibe and visuals
st.set_page_config(page_title="Customer Transaction Insights Dashboard", layout="wide")
sns.set(style='whitegrid')

df = load_data()

# Sidebar filters
st.sidebar.header("Filters")

# Date range filter with unique key to avoid duplicate ID error
min_date = df['purchase_date'].min()
max_date = df['purchase_date'].max()
start_date, end_date = st.sidebar.date_input("Select date range", value=[min_date, max_date], min_value=min_date, max_value=max_date, key="date_range")

# Customer type filter
customer_type = st.sidebar.multiselect("Select customer type", options=['New', 'Returning'], default=['New', 'Returning'])

# Payment method filter
payment_methods = df['payment_method'].unique().tolist()
selected_payments = st.sidebar.multiselect("Select payment methods", options=payment_methods, default=payment_methods)

# Churn threshold slider
churn_threshold = st.sidebar.slider("Churn threshold (max previous purchases)", min_value=1, max_value=int(df['previous_purchases'].max()), value=1)

# Chart visibility toggles
st.sidebar.header("Toggle Charts")
show_segmentation = st.sidebar.checkbox("Customer Segmentation", value=True)
show_purchase_count = st.sidebar.checkbox("Previous Purchase Count", value=True)
show_payment_pref = st.sidebar.checkbox("Payment Method Preferences", value=True)
show_purchase_freq = st.sidebar.checkbox("Frequency of Purchases", value=True)
show_churn = st.sidebar.checkbox("Customer Churn", value=True)
show_time_trends = st.sidebar.checkbox("Time-Based Trends", value=True)

# Enhanced styles with improved insight visibility
st.markdown(
    """
    <style>
    .fixed-header {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        background-color: #f5f5f5;
        padding: 10px 20px;
        z-index: 1000;
        border-bottom: 1px solid #ddd;
    }
    .content {
        margin-top: 40px;
    }
    .kpi-capsule {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px 30px;
        border-radius: 50px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        margin: 15px;
        min-width: 200px;
        display: inline-block;
    }
    .kpi-capsule:hover {
        transform: scale(1.03);
        transition: transform 0.2s ease;
    }
    .kpi-value {
        font-size: 2.3em;
        font-weight: 700;
        margin: 0;
        line-height: 1;
    }
    .kpi-label {
        font-size: 0.95em;
        margin-top: 6px;
        margin-bottom: 0;
        font-weight: 500;
        opacity: 0.85;
    }
    .kpi-insight-list {
        margin-top: 12px;
        background-color: rgba(255, 255, 255, 0.1);
        padding: 12px 16px;
        border-radius: 8px;
        border-left: 3px solid #ffd700;
        min-height: 60px;
        display: flex;
        align-items: center;
    }
    
    .kpi-insight-list ul {
        margin: 0;
        padding-left: 1.2rem;
        list-style-type: disc;
    }
    
    .kpi-insight-list li {
        font-size: 1.0em;
        color: #495057;
        font-style: italic;
        font-weight: 500;
        line-height: 1.4;
        margin: 0;
    }
    .download-button {
        font-size: 18px;
        font-weight: bold;
    }
    .download-button > button {
        font-size: 18px !important;
        font-weight: bold !important;
        padding: 10px 16px;
        border-radius: 6px;
        background-color: #4CAF50;
        color: white;
        border: none;
    }
    .download-button > button:hover {
        background-color: #45a049;
    }
    
    /* Alternative insight styling - more prominent */
    .kpi-insight-prominent {
        margin-top: 15px;
        font-size: 1.1em;
        color: #2c3e50;
        font-weight: 600;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 12px 16px;
        border-radius: 25px;
        border-left: 4px solid #007bff;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Section insight styling for chart descriptions */
    .section-insight {
        background-color: #f8f9fa;
        border-left: 4px solid #007bff;
        padding: 12px 16px;
        margin: 10px 0;
        border-radius: 6px;
        font-size: 0.95em;
        color: #495057;
        font-style: italic;
    }
    </style>
    """,
    unsafe_allow_html=True
)

with st.container():
    st.markdown('<div class="fixed-header">', unsafe_allow_html=True)
    st.title("Customer Transaction Insights Dashboard")
    st.markdown("Gain actionable insights from customer transaction patterns — segmentation, churn, and behavior — like a real data analyst would.")
    st.markdown('</div>', unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="content">', unsafe_allow_html=True)

    # Filter data based on selections
    filtered_df = df[
        (df['purchase_date'] >= pd.to_datetime(start_date)) &
        (df['purchase_date'] <= pd.to_datetime(end_date)) &
        (df['payment_method'].isin(selected_payments))
    ]

    # Map customer type selection to binary values
    customer_type_map = {'New': 0, 'Returning': 1}
    selected_customer_type_vals = [customer_type_map[ct] for ct in customer_type]
    filtered_df = filtered_df[filtered_df['is_returning_customer'].isin(selected_customer_type_vals)]

    # Summary KPIs
    st.subheader("Key Performance Indicators")
    total_customer_types = filtered_df['is_returning_customer'].nunique()
    total_transactions = filtered_df.shape[0]
    avg_purchases = filtered_df['previous_purchases'].mean()

    col1, col2, col3 = st.columns(3)

    # KPI cards with enhanced insight visibility
    with col1:
        st.markdown(f'''
        <div class="kpi-capsule">
            <div class="kpi-value">{total_customer_types}</div>
            <div class="kpi-label">Customer Types Present</div>
        </div>
        ''', unsafe_allow_html=True)
        returning_percentage = ((filtered_df['is_returning_customer'] == 1).sum() / len(filtered_df)) * 100 if len(filtered_df) > 0 else 0
        st.markdown(f'''
        <div class="kpi-insight-list">
            <ul>
                <li><strong>Insight:</strong> Returning customers make up {returning_percentage:.1f}% of the data.</li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
        <div class="kpi-capsule">
            <div class="kpi-value">{total_transactions:,}</div>
            <div class="kpi-label">Total Transactions</div>
        </div>
        ''', unsafe_allow_html=True)
        st.markdown(f'''
        <div class="kpi-insight-list">
            <ul>
                <li><strong>Insight:</strong> Average transactions per customer is {avg_purchases:.2f}.</li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'''
        <div class="kpi-capsule">
            <div class="kpi-value">{avg_purchases:.2f}</div>
            <div class="kpi-label">Average Previous Purchases</div>
        </div>
        ''', unsafe_allow_html=True)
        st.markdown('''
        <div class="kpi-insight-list">
            <ul>
                <li><strong>Insight:</strong> Higher average indicates loyal customers.</li>
            </ul>
        </div>
        ''', unsafe_allow_html=True)

    if show_segmentation:
        st.subheader("Customer Segmentation")
        st.caption("Are people coming back, or just testing the waters?")
        
        # Enhanced section insight
        st.markdown('<div class="section-insight"><strong>Customer Segmentation:</strong> This section shows the distribution of new vs returning customers using bar and pie charts, helping identify customer loyalty patterns.</div>', unsafe_allow_html=True)
        
        segment_counts = filtered_df['is_returning_customer'].value_counts().rename({0: 'New', 1: 'Returning'})
        fig, ax = plt.subplots(1, 2, figsize=(12, 5))

        # Bar plot
        sns.barplot(x=segment_counts.index, y=segment_counts.values, hue=segment_counts.index, palette='pastel', legend=True, ax=ax[0])
        ax[0].set_title("Customer Segmentation: New vs Returning (Bar Plot)")
        ax[0].set_ylabel("Number of Customers")
        ax[0].legend(title='Customer Type')

        # Pie chart
        colors = sns.color_palette('pastel')[0:2]
        ax[1].pie(segment_counts.values, labels=segment_counts.index, colors=colors, autopct='%1.1f%%', startangle=140)
        ax[1].set_title("Customer Segmentation: New vs Returning (Pie Chart)")

        st.pyplot(fig)

    if show_purchase_count:
        st.subheader("Previous Purchase Count")
        st.caption("This gives us a quick sense of customer loyalty.")
        st.markdown('<div class="section-insight"><strong>Previous Purchase Count:</strong> This chart shows the distribution of customers based on how many previous purchases they have made, indicating loyalty levels.</div>', unsafe_allow_html=True)
        hist_values = filtered_df['previous_purchases'].value_counts().sort_index()
        st.bar_chart(hist_values)

    if show_payment_pref:
        st.subheader("Payment Method Preferences")
        st.caption("Let's see what people actually use when they pay.")
        st.markdown('<div class="section-insight"><strong>Payment Method Preferences:</strong> This section shows the distribution of payment methods used by customers, highlighting popular transaction modes.</div>', unsafe_allow_html=True)
        
        payment_counts = filtered_df['payment_method'].value_counts()
        fig, ax = plt.subplots(1, 2, figsize=(12, 5))

        # Count plot
        sns.countplot(data=filtered_df, y='payment_method', order=payment_counts.index, hue='payment_method', palette="Set2", legend=False, ax=ax[0])
        ax[0].set_title("Payment Method Usage (Count Plot)")
        ax[0].set_xlabel("Count")
        ax[0].set_ylabel("Payment Method")

        # Pie chart
        colors = sns.color_palette('Set2')[0:len(payment_counts)]
        ax[1].pie(payment_counts.values, labels=payment_counts.index, colors=colors, autopct='%1.1f%%', startangle=140)
        ax[1].set_title("Payment Method Usage (Pie Chart)")

        st.pyplot(fig)

    if show_purchase_freq:
        st.subheader("Frequency of Purchases")
        st.caption("How often do customers shop — according to labels they chose.")
        st.markdown('<div class="section-insight"><strong>Frequency of Purchases:</strong> This chart shows how frequently customers make purchases, based on their selected frequency labels.</div>', unsafe_allow_html=True)
        purchase_freq = filtered_df['frequency_of_purchases'].value_counts()
        st.bar_chart(purchase_freq)

    if show_churn:
        st.subheader("Customer Churn")
        st.caption(f"Assuming churners are customers with only {churn_threshold} or fewer past purchases.")
        st.markdown('<div class="section-insight"><strong>Customer Churn:</strong> This chart identifies customers likely to have churned based on their low number of previous purchases, segmented by new vs returning.</div>', unsafe_allow_html=True)
        churned = filtered_df[filtered_df['previous_purchases'] <= churn_threshold]
        churn_summary = churned['is_returning_customer'].value_counts().rename({0: 'New', 1: 'Returning'})
        st.bar_chart(churn_summary)

    # Extra curiosity: how do payment preferences differ by customer type?
    with st.expander("Payment Method Split by Customer Type"):
        cross_tab = pd.crosstab(filtered_df['payment_method'], filtered_df['is_returning_customer'])
        cross_tab.columns = ['New', 'Returning']
        st.dataframe(cross_tab)

    if show_time_trends:
        # Time-Based Trends
        st.subheader("🕒 Time-Based Transaction Trends")
        st.caption("Monthly and weekday patterns in customer purchases.")
        st.markdown('<div class="section-insight"><strong>Time-Based Transaction Trends:</strong> This section shows how transactions vary over months and days of the week, highlighting temporal patterns.</div>', unsafe_allow_html=True)

        # Monthly trend with proper month names
        st.markdown("**Monthly Transaction Volume**")
        monthly = (
            filtered_df.groupby(['month', 'month_name']).size()
            .reset_index(name='transaction_count')
            .sort_values('month')
        )
        monthly.set_index('month_name', inplace=True)
        st.line_chart(monthly['transaction_count'])

        # Weekly trend
        st.markdown("**Transactions by Day of Week**")
        weekly = filtered_df['day_of_week'].value_counts().reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
        st.bar_chart(weekly)

# Tooltip for churn threshold slider
st.sidebar.markdown("ℹ️ **Churn threshold**: Maximum number of previous purchases to consider a customer as churned.")

# Show selected date range below KPIs
st.markdown(f"### Showing data for **{start_date.strftime('%b %Y')}** to **{end_date.strftime('%b %Y')}**")

# Reset filters button
if st.sidebar.button("Reset All Filters"):
    st.experimental_rerun()

#  Visual separator
st.markdown("---")

#  Export section
st.subheader("📥 Export Data")
st.markdown("Download the filtered dataset as an Excel report.")
st.markdown("Click below to download the filtered Excel report ⬇️")

# Generate Excel data
excel_data = to_excel(filtered_df)

# Styled download button
st.download_button(
    label='📥 Download Excel Report',
    data=excel_data,
    file_name='customer_transaction_report.xlsx',
    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    key='download-excel',
    help='Download the filtered dataset as an Excel report',
)

# Spacing before footer
st.markdown(" ")

# Footer credit
st.markdown(
    """
    <p style='text-align: center; color: #666; font-size: 14px; margin-top: 2rem;'>
        📊 Built by <a href='https://www.linkedin.com/in/siddhi-phatkare-a78552250/' 
        target='_blank' style='color: #0066cc; text-decoration: none;'>Siddhi Phatkare</a> 
        • Open for learning & inspiration, not rehosting.
    </p>
    """,
    unsafe_allow_html=True
)