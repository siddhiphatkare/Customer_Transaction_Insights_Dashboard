import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
from calendar import month_name
from utils import load_data, to_excel
from ml_models import MLModels, cluster_customers

import streamlit.components.v1 as components

# Inject Google Analytics tracking script
components.html(
    """
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-YLB6N45Q1Q"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-YLB6N45Q1Q');
    </script>
    """,
    height=0
)

#  Setting the vibe and visuals
st.set_page_config(page_title="Customer Transaction Insights Dashboard", layout="wide")
sns.set(style='whitegrid')

df = load_data()

# Sidebar filters
st.sidebar.header("Filters")

# Date range filters split into two separate inputs for independent control
min_date = df['purchase_date'].min()
max_date = df['purchase_date'].max()

start_date = st.sidebar.date_input("From date", value=min_date, min_value=min_date, max_value=max_date, key="start_date")
end_date = st.sidebar.date_input("To date", value=max_date, min_value=min_date, max_value=max_date, key="end_date")

# Ensure start_date is not after end_date
if start_date > end_date:
    st.sidebar.error("Error: 'From date' must be before or equal to 'To date'.")
    # Optionally, prevent filtering with invalid range by resetting end_date to start_date
    end_date = start_date

# Customer type filter
customer_type = st.sidebar.multiselect("Select customer type", options=['New', 'Returning'], default=['New', 'Returning'])

# Advanced filters: demographics and product categories
age_min = int(df['age'].min()) if 'age' in df.columns else None
age_max = int(df['age'].max()) if 'age' in df.columns else None
age_range = (age_min, age_max)
if age_min is not None and age_max is not None:
    age_range = st.sidebar.slider("Select Age Range", min_value=age_min, max_value=age_max, value=(age_min, age_max))

gender_options = df['gender'].dropna().unique().tolist() if 'gender' in df.columns else []
selected_genders = st.sidebar.multiselect("Select Gender", options=gender_options, default=gender_options)

product_categories = df['category'].dropna().unique().tolist() if 'category' in df.columns else []
selected_categories = st.sidebar.multiselect("Select Product Categories", options=product_categories, default=product_categories)

# Price range filter (new)
price_min = float(df['price'].min()) if 'price' in df.columns else None
price_max = float(df['price'].max()) if 'price' in df.columns else None
price_range = (price_min, price_max)
if price_min is not None and price_max is not None:
    price_range = st.sidebar.slider("Select Price Range (USD)", min_value=price_min, max_value=price_max, value=(price_min, price_max), step=0.01)

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
    st.markdown("Extract actionable insights on churn, behavior, and segments — powered by real-time analytics and data storytelling.")
    st.markdown('</div>', unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="content">', unsafe_allow_html=True)

    tabs = st.tabs(["Overview", "Analytics", "Cohort Analysis", "Churn Summary", "Raw Data", "Data Dictionary"])

    with tabs[0]:
        # Overview tab content
        # Filter data based on selections
        filtered_df = df[
            (df['purchase_date'] >= pd.to_datetime(start_date)) &
            (df['purchase_date'] <= pd.to_datetime(end_date)) &
            (df['payment_method'].isin(selected_payments))
        ]

        if age_min is not None and age_max is not None:
            filtered_df = filtered_df[(filtered_df['age'] >= age_range[0]) & (filtered_df['age'] <= age_range[1])]

        if len(gender_options) > 0:
            filtered_df = filtered_df[filtered_df['gender'].isin(selected_genders)]

        if len(product_categories) > 0:
            filtered_df = filtered_df[filtered_df['category'].isin(selected_categories)]

        # Price range filter (new)
        if price_min is not None and price_max is not None:
            filtered_df = filtered_df[(filtered_df['price'] >= price_range[0]) & (filtered_df['price'] <= price_range[1])]

        # Map customer type selection to binary values
        customer_type_map = {'new': 0, 'returning': 1}
        selected_customer_type_vals = [customer_type_map[ct.lower()] for ct in customer_type]
        filtered_df = filtered_df[filtered_df['is_returning_customer'].astype(int).isin(selected_customer_type_vals)]

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

        if show_purchase_count:
            st.subheader("Previous Purchase Count")
            st.caption("This section provides an overview of customer loyalty by showing the distribution of customers based on their number of previous purchases.")
            st.markdown('<div class="section-insight"><strong>Previous Purchase Count:</strong> This chart shows the distribution of customers based on how many previous purchases they have made, indicating loyalty levels.</div>', unsafe_allow_html=True)
            hist_values = filtered_df['previous_purchases'].value_counts().sort_index()
            st.bar_chart(hist_values)

        if show_payment_pref:
            st.subheader("Payment Method Preferences")
            st.caption("This section highlights the payment methods preferred by customers, providing insights into popular transaction modes.")
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
            st.caption("This section analyzes how frequently customers make purchases, categorized by their selected frequency labels.")
            st.markdown('<div class="section-insight"><strong>Frequency of Purchases:</strong> This chart shows how frequently customers make purchases, based on their selected frequency labels.</div>', unsafe_allow_html=True)
            purchase_freq = filtered_df['frequency_of_purchases'].value_counts()
            st.bar_chart(purchase_freq)

        if show_churn:
            st.subheader("Customer Churn")
            st.caption(f"This section identifies customers likely to have churned, defined as those with {churn_threshold} or fewer previous purchases, segmented by new vs returning customers.")
            st.markdown('<div class="section-insight"><strong>Customer Churn:</strong> This chart identifies customers likely to have churned based on their low number of previous purchases, segmented by new vs returning.</div>', unsafe_allow_html=True)
            churned = filtered_df[filtered_df['previous_purchases'] <= churn_threshold]
            churn_summary = churned['is_returning_customer'].value_counts()

            # Ensure both 'New' and 'Returning' labels are present in the churn_summary
            for label in [0, 1]:
                if label not in churn_summary.index:
                    churn_summary.loc[label] = 0
            churn_summary = churn_summary.sort_index()
            churn_summary.index = churn_summary.index.map({0: 'New', 1: 'Returning'})

            st.bar_chart(churn_summary)

        # Extra curiosity: how do payment preferences differ by customer type?
        with st.expander("Payment Method Split by Customer Type"):
            cross_tab = pd.crosstab(filtered_df['payment_method'], filtered_df['is_returning_customer'])
            # Fix: Only rename columns if both 0 and 1 are present to avoid length mismatch error
            if set(cross_tab.columns) == {0, 1}:
                cross_tab.columns = ['New', 'Returning']
            elif set(cross_tab.columns) == {0}:
                cross_tab.columns = ['New']
            elif set(cross_tab.columns) == {1}:
                cross_tab.columns = ['Returning']
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

    with tabs[1]:
        # Analytics tab content
        filtered_df = df[
            (df['purchase_date'] >= pd.to_datetime(start_date)) &
            (df['purchase_date'] <= pd.to_datetime(end_date)) &
            (df['payment_method'].isin(selected_payments))
        ]

        if age_min is not None and age_max is not None:
            filtered_df = filtered_df[(filtered_df['age'] >= age_range[0]) & (filtered_df['age'] <= age_range[1])]

        if len(gender_options) > 0:
            filtered_df = filtered_df[filtered_df['gender'].isin(selected_genders)]

        if len(product_categories) > 0:
            filtered_df = filtered_df[filtered_df['category'].isin(selected_categories)]

        # Price range filter (new)
        if price_min is not None and price_max is not None:
            filtered_df = filtered_df[(filtered_df['price'] >= price_range[0]) & (filtered_df['price'] <= price_range[1])]

        # Map customer type selection to binary values
        customer_type_map = {'new': 0, 'returning': 1}
        selected_customer_type_vals = [customer_type_map[ct.lower()] for ct in customer_type]
        filtered_df = filtered_df[filtered_df['is_returning_customer'].astype(int).isin(selected_customer_type_vals)]

        if show_segmentation:
            st.subheader("Customer Segmentation")
            st.caption("Are people coming back, or just testing the waters?")
            
            st.markdown('<div class="section-insight"><strong>Customer Segmentation:</strong> This section shows the distribution of new vs returning customers using bar and pie charts, helping identify customer loyalty patterns.</div>', unsafe_allow_html=True)
            
            segment_counts = filtered_df['is_returning_customer'].value_counts().rename({0: 'New', 1: 'Returning'})
            fig, ax = plt.subplots(1, 2, figsize=(12, 5))

            sns.barplot(x=segment_counts.index, y=segment_counts.values, hue=segment_counts.index, palette='pastel', legend=True, ax=ax[0])
            ax[0].set_title("Customer Segmentation: New vs Returning (Bar Plot)")
            ax[0].set_ylabel("Number of Customers")
            ax[0].legend(title='Customer Type')

            colors = sns.color_palette('pastel')[0:2]
            ax[1].pie(segment_counts.values, labels=segment_counts.index, colors=colors, autopct='%1.1f%%', startangle=140)
            ax[1].set_title("Customer Segmentation: New vs Returning (Pie Chart)")

            st.pyplot(fig)

        # Add download excel report button here for better visibility
        excel_data = to_excel(filtered_df)
        st.download_button(
            label="Download Excel Report",
            data=excel_data,
            file_name="customer_transaction_insights_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    with tabs[2]:
        # Cohort Analysis tab content
        st.header("Cohort Analysis")
        # Implement cohort analysis visualization here
        st.markdown("This section provides cohort analysis visualizations to track customer lifecycle and behavior over time, helping identify retention and engagement patterns.")
        # Example: cohort analysis by month and customer type
        cohort_data = df.copy()
        cohort_data['purchase_month'] = cohort_data['purchase_date'].dt.to_period('M')
        cohort_counts = cohort_data.groupby(['purchase_month', 'is_returning_customer']).size().unstack(fill_value=0)
        st.line_chart(cohort_counts)

    with tabs[3]:
        # Churn Summary tab content
        st.header("Churn Summary")
        churn_threshold_val = churn_threshold
        churned_customers = filtered_df[filtered_df['previous_purchases'] <= churn_threshold_val]
        churn_summary = churned_customers['is_returning_customer'].value_counts().rename({0: 'New', 1: 'Returning'})

        # Additional KPIs
        total_churned = churned_customers.shape[0]
        total_customers = filtered_df.shape[0]
        churn_rate = (total_churned / total_customers) * 100 if total_customers > 0 else 0

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Churned Customers", total_churned)
        with col2:
            st.metric("Total Customers", total_customers)
        with col3:
            st.metric("Churn Rate (%)", f"{churn_rate:.2f}")

        # Bar chart of churn summary
        st.subheader("Churned Customers by Customer Type")
        if total_churned == 0:
            st.write("No churned customers to display in the bar chart.")
        else:
            st.bar_chart(churn_summary)

        # Pie chart for churn distribution
        st.subheader("Churn Distribution")
        fig, ax = plt.subplots(figsize=(2, 2))  # Adjust figure size to be smaller and square
        colors = sns.color_palette('pastel')[0:2]
        labels = ['New', 'Returning']
        # Fix: Use string labels to get values from churn_summary since index was renamed
        values = [churn_summary.get('New', 0), churn_summary.get('Returning', 0)]
        total = sum(values)
        if total == 0:
            st.write("No churned customers to display in the pie chart.")
        else:
            ax.pie(values, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
            ax.set_title("Churn Distribution: New vs Returning")
            st.pyplot(fig)

        # Textual insights
        st.markdown(
            f"""
            <div class="kpi-insight-prominent">
            <strong>Insights:</strong>
            <ul>
                <li>Churn rate is {churn_rate:.2f}% based on the threshold of {churn_threshold_val} previous purchases.</li>
                <li>Returning customers constitute {(churn_summary.get('Returning', 0) / total_churned * 100) if total_churned > 0 else 0:.1f}% of churned customers.</li>
                <li>New customers constitute {(churn_summary.get('New', 0) / total_churned * 100) if total_churned > 0 else 0:.1f}% of churned customers.</li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

    with tabs[4]:
        # Raw Data tab content
        st.header("Raw Data")
        st.markdown("This section displays the raw transaction data in a tabular format with interactive filters. Users can explore individual records and download the filtered dataset as an Excel file for offline analysis.")
        raw_df = df.copy()
        raw_df['is_returning_customer'] = raw_df['customer_type'].map({'new': 0, 'returning': 1})
        st.dataframe(raw_df)
        towrite = BytesIO()
        raw_df.to_excel(towrite, index=False, header=True)
        towrite.seek(0)
        st.download_button(label="Download data as Excel", data=towrite, file_name="shopping_trends.xlsx", mime="application/vnd.ms-excel")

    with tabs[5]:
        # Data Dictionary tab content
        st.header("Data Dictionary")
        st.write("Data dictionary for dataset columns.")
        data_dict = {
            "customer_id": "Unique identifier for each customer",
            "age": "Age of the customer",
            "gender": "Gender of the customer",
            "item_purchased": "Item purchased by the customer",
            "category": "Category of the purchased item",
            "purchase_amount_(usd)": "Amount spent in USD",
            "location": "Customer location",
            "size": "Size of the item",
            "color": "Color of the item",
            "season": "Season of purchase",
            "review_rating": "Customer review rating",
            "subscription_status": "Subscription status of the customer",
            "payment_method": "Payment method used",
            "shipping_type": "Type of shipping selected",
            "discount_applied": "Whether discount was applied",
            "promo_code_used": "Whether promo code was used",
            "previous_purchases": "Number of previous purchases by the customer",
            "preferred_payment_method": "Customer's preferred payment method",
            "frequency_of_purchases": "Frequency of purchases by the customer",
            "purchase_date": "Date of purchase",
            "customer_type": "Type of customer: New or Returning based on previous purchases"
        }
        dict_df = pd.DataFrame(list(data_dict.items()), columns=["Column", "Description"])
        st.table(dict_df)

