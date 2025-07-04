import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO

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

# Excel report generation feature
from datetime import datetime

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    workbook = writer.book

    # Summary Sheet
    summary_ws = workbook.add_worksheet('Summary')
    writer.sheets['Summary'] = summary_ws

    # Formats
    bold = workbook.add_format({'bold': True})
    center_bold = workbook.add_format({'bold': True, 'align': 'center'})
    header_fmt = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC', 'align': 'center'})
    timestamp_fmt = workbook.add_format({'italic': True, 'font_color': '#888888'})

    # Column widths
    summary_ws.set_column('A:A', 25)
    summary_ws.set_column('B:B', 20)

    # Timestamp at top-right (row 0, column E)
    summary_ws.write(0, 4, datetime.now().strftime("Last Updated: %Y-%m-%d %H:%M"), timestamp_fmt)

    # Start KPIs at row 2 to avoid timestamp overlap
    row = 2
    summary_ws.write(row, 0, "Key Performance Indicators", bold)
    row += 1

    kpis = {
        'Total Customer Types': df['is_returning_customer'].nunique(),
        'Total Transactions': df.shape[0],
        'Average Previous Purchases': round(df['previous_purchases'].mean(), 2)
    }
    for k, v in kpis.items():
        summary_ws.write(row, 0, k)
        summary_ws.write(row, 1, v)
        row += 1

    # Customer Segmentation
    row += 1
    summary_ws.write(row, 0, "Customer Segmentation Summary", bold)
    row += 1
    summary_ws.write(row, 0, "Segment", header_fmt)
    summary_ws.write(row, 1, "Count", header_fmt)
    row += 1
    seg_counts = df['is_returning_customer'].value_counts().reindex([0, 1], fill_value=0).rename({0: 'New', 1: 'Returning'})
    seg_start_row = row
    for seg, count in seg_counts.items():
        summary_ws.write(row, 0, seg)
        summary_ws.write(row, 1, count)
        row += 1
    seg_end_row = row - 1

    # Pie Chart
    pie_chart = workbook.add_chart({'type': 'pie'})
    pie_chart.add_series({
        'name': 'Customer Segmentation',
        'categories': ['Summary', seg_start_row, 0, seg_end_row, 0],
        'values':     ['Summary', seg_start_row, 1, seg_end_row, 1],
        'data_labels': {'percentage': True},
        'points': [
            {'fill': {'color': '#ED7D31'}},  # New
            {'fill': {'color': '#5B9BD5'}}   # Returning
        ]
    })
    pie_chart.set_title({'name': 'Customer Segmentation'})
    summary_ws.insert_chart('E5', pie_chart)

    # Monthly Trend
    monthly = df['month'].value_counts().sort_index()
    row += 2
    summary_ws.write(row, 0, "Monthly Transaction Volume", bold)
    row += 1
    monthly_start = row
    summary_ws.write(row, 0, "Month", header_fmt)
    summary_ws.write(row, 1, "Transactions", header_fmt)
    row += 1
    for month, count in monthly.items():
        summary_ws.write(row, 0, month)
        summary_ws.write(row, 1, count)
        row += 1
    monthly_end = row - 1

    line_chart = workbook.add_chart({'type': 'line'})
    line_chart.add_series({
        'name': 'Monthly Transactions',
        'categories': ['Summary', monthly_start + 1, 0, monthly_end, 0],
        'values':     ['Summary', monthly_start + 1, 1, monthly_end, 1],
        'data_labels': {'value': True}
    })
    line_chart.set_title({'name': 'Monthly Transaction Trend'})
    line_chart.set_x_axis({'name': 'Month'})
    line_chart.set_y_axis({'name': 'Transactions'})
    line_chart.set_legend({'position': 'bottom'})
    line_chart.set_style(10)
    summary_ws.insert_chart('E22', line_chart)

    # Payment Method Preferences
    payment_counts = df['payment_method'].value_counts()
    row += 2
    summary_ws.write(row, 0, "Payment Method Preferences", bold)
    row += 1
    pay_start = row
    summary_ws.write(row, 0, "Payment Method", header_fmt)
    summary_ws.write(row, 1, "Count", header_fmt)
    row += 1
    for method, count in payment_counts.items():
        summary_ws.write(row, 0, method)
        summary_ws.write(row, 1, count)
        row += 1
    pay_end = row - 1

    bar_chart = workbook.add_chart({'type': 'column'})
    bar_chart.add_series({
        'name': 'Payment Methods',
        'categories': ['Summary', pay_start + 1, 0, pay_end, 0],
        'values':     ['Summary', pay_start + 1, 1, pay_end, 1],
        'data_labels': {'value': True}
    })
    bar_chart.set_title({'name': 'Payment Method Usage'})
    bar_chart.set_x_axis({'name': 'Method'})
    bar_chart.set_y_axis({'name': 'Count'})
    bar_chart.set_legend({'none': True})
    bar_chart.set_style(11)
    summary_ws.insert_chart('E42', bar_chart)

    # Freeze header rows under timestamp + KPI header
    summary_ws.freeze_panes(3, 0)

    # Report Sheet 
    df.to_excel(writer, index=False, sheet_name='Report', startrow=1, header=False)
    report_ws = writer.sheets['Report']

    for col_num, col_name in enumerate(df.columns):
        report_ws.write(0, col_num, col_name, header_fmt)
        report_ws.set_column(col_num, col_num, 15)

    report_ws.freeze_panes(1, 0)

    writer.close()
    return output.getvalue()

# ⬇️ Adding visual separation from above
st.markdown("---")

# 📥 Export section
st.subheader("📥 Export Data")
st.markdown("Download the filtered dataset as an Excel report.")

excel_data = to_excel(filtered_df)
st.download_button(
    label='📥 Download Excel Report',
    data=excel_data,
    file_name='customer_transaction_report.xlsx',
    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
)

# Extra line spacing before footer
st.markdown(" ")

# 👤 Credit footer
st.markdown(
    "📊 Built by [Siddhi Phatkare](https://www.linkedin.com/in/siddhi-phatkare-a78552250/) • Open for learning & inspiration, not rehosting.",
    unsafe_allow_html=True
)
