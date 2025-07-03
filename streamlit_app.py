import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

#  Setting the vibe and visuals
st.set_page_config(page_title="Customer Transaction Insights Dashboard", layout="wide")
sns.set(style='whitegrid')

#  Load the dataset once, clean up column names, and tag returning customers
@st.cache_data
def load_data():
    df = pd.read_csv("shopping_trends.csv")
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    df['is_returning_customer'] = df['subscription_status'].map({'Yes': 1, 'No': 0})
    df['purchase_date'] = pd.to_datetime(df['purchase_date'], errors='coerce')
    df['month'] = df['purchase_date'].dt.to_period('M').astype(str)
    df['day_of_week'] = df['purchase_date'].dt.day_name()
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("Filters")

# Date range filter
min_date = df['purchase_date'].min()
max_date = df['purchase_date'].max()
start_date, end_date = st.sidebar.date_input("Select date range", [min_date, max_date], min_value=min_date, max_value=max_date)

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

# Dashboard begins
st.title("Customer Transaction Insights Dashboard")
st.markdown("We're using e-commerce transaction data to generate insights — customer segmentation, payment patterns, and churn analysis.")

# Summary KPIs
st.subheader("Key Performance Indicators")
total_customer_types = filtered_df['is_returning_customer'].nunique()
total_transactions = filtered_df.shape[0]
avg_purchases = filtered_df['previous_purchases'].mean()

col1, col2, col3 = st.columns(3)
col1.metric("Customer Types Present", total_customer_types)
col2.metric("Total Transactions", total_transactions)
col3.metric("Average Previous Purchases", f"{avg_purchases:.2f}")

if show_segmentation:
    st.subheader("Customer Segmentation")
    st.caption("Are people coming back, or just testing the waters?")
    segment_counts = filtered_df['is_returning_customer'].value_counts().rename({0: 'New', 1: 'Returning'})
    fig, ax = plt.subplots(1, 2, figsize=(12, 5))

    # Bar plot
    sns.barplot(x=segment_counts.index, y=segment_counts.values, hue=segment_counts.index, palette='pastel', legend=False, ax=ax[0])
    ax[0].set_title("Customer Segmentation: New vs Returning (Bar Plot)")
    ax[0].set_ylabel("Number of Customers")

    # Pie chart
    colors = sns.color_palette('pastel')[0:2]
    ax[1].pie(segment_counts.values, labels=segment_counts.index, colors=colors, autopct='%1.1f%%', startangle=140)
    ax[1].set_title("Customer Segmentation: New vs Returning (Pie Chart)")

    st.pyplot(fig)

if show_purchase_count:
    st.subheader("Previous Purchase Count")
    st.caption("This gives us a quick sense of customer loyalty.")
    hist_values = filtered_df['previous_purchases'].value_counts().sort_index()
    st.bar_chart(hist_values)

if show_payment_pref:
    st.subheader("Payment Method Preferences")
    st.caption("Let’s see what people actually use when they pay.")
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
    purchase_freq = filtered_df['frequency_of_purchases'].value_counts()
    st.bar_chart(purchase_freq)

if show_churn:
    st.subheader("Customer Churn")
    st.caption(f"Assuming churners are customers with only {churn_threshold} or fewer past purchases.")
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

    # Monthly trend
    st.markdown("**Monthly Transaction Volume**")
    monthly = filtered_df['month'].value_counts().sort_index()
    st.line_chart(monthly)

    # Weekly trend
    st.markdown("**Transactions by Day of Week**")
    weekly = filtered_df['day_of_week'].value_counts().reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    st.bar_chart(weekly)
