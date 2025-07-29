import pandas as pd
from io import BytesIO
from datetime import datetime
from calendar import month_name


def load_data():
    df = pd.read_csv("shopping_trends.csv")
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    if 'customer_type' in df.columns:
        df['is_returning_customer'] = df['customer_type'].map({'new': 0, 'returning': 1})
    elif 'subscription_status' in df.columns:
        df['is_returning_customer'] = df['subscription_status'].map({'Yes': 1, 'No': 0})
    if 'purchase_date' in df.columns:
        df['purchase_date'] = pd.to_datetime(df['purchase_date'], errors='coerce')
        df['month'] = df['purchase_date'].dt.month
        df['month_name'] = df['purchase_date'].dt.strftime('%B')
        df['day_of_week'] = df['purchase_date'].dt.day_name()
    if 'customer_id' in df.columns:
        df['customer_id'] = df['customer_id'].astype(str)

    return df


def compute_cohort_table(df):
    df['cohort_month'] = df.groupby('customer_id')['purchase_date'].transform('min').dt.to_period('M')
    df['order_month'] = df['purchase_date'].dt.to_period('M')
    df['cohort_index'] = (df['order_month'] - df['cohort_month']).apply(lambda x: x.n)

    cohort_data = df.groupby(['cohort_month', 'cohort_index'])['customer_id'].nunique().reset_index()
    cohort_pivot = cohort_data.pivot(index='cohort_month', columns='cohort_index', values='customer_id')
    return cohort_pivot


def compute_monthly_revenue(df):
    if 'price' in df.columns:
        monthly_revenue = (
            df.groupby([df['purchase_date'].dt.to_period('M')])['price']
            .sum().reset_index().rename(columns={'price': 'revenue'})
        )
        monthly_revenue['purchase_date'] = monthly_revenue['purchase_date'].dt.to_timestamp()
        return monthly_revenue
    return pd.DataFrame()


def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    workbook = writer.book
    summary_ws = workbook.add_worksheet('Summary')
    writer.sheets['Summary'] = summary_ws

    bold = workbook.add_format({'bold': True})
    center_bold = workbook.add_format({'bold': True, 'align': 'center'})
    header_fmt = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC', 'align': 'center'})
    timestamp_fmt = workbook.add_format({'italic': True, 'font_color': '#888888'})

    summary_ws.set_column('A:A', 25)
    summary_ws.set_column('B:B', 20)
    summary_ws.write(0, 4, datetime.now().strftime("Last Updated: %Y-%m-%d %H:%M"), timestamp_fmt)

    row = 2
    summary_ws.write(row, 0, "Key Performance Indicators", bold)
    row += 1

    kpis = {
        'Total Customer Types': df['is_returning_customer'].nunique(),
        'Total Transactions': df.shape[0],
        'Average Previous Purchases': round(df['previous_purchases'].mean(), 2)
    }
    if 'price' in df.columns:
        kpis['Total Revenue'] = round(df['price'].sum(), 2)
        kpis['Average Revenue per Transaction'] = round(df['price'].mean(), 2)

    for k, v in kpis.items():
        summary_ws.write(row, 0, k)
        summary_ws.write(row, 1, v)
        row += 1

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

    pie_chart = workbook.add_chart({'type': 'pie'})
    pie_chart.add_series({
        'name': 'Customer Segmentation',
        'categories': ['Summary', seg_start_row, 0, seg_end_row, 0],
        'values':     ['Summary', seg_start_row, 1, seg_end_row, 1],
        'data_labels': {'percentage': True},
        'points': [
            {'fill': {'color': '#ED7D31'}},
            {'fill': {'color': '#5B9BD5'}}
        ]
    })
    pie_chart.set_title({'name': 'Customer Segmentation'})
    summary_ws.insert_chart('E5', pie_chart)

    monthly = df['month'].value_counts().reindex(range(1, 13), fill_value=0)
    monthly.index = [month_name[m] for m in monthly.index]

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

    summary_ws.freeze_panes(3, 0)

    df.to_excel(writer, index=False, sheet_name='Report', startrow=1, header=False)
    report_ws = writer.sheets['Report']
    for col_num, col_name in enumerate(df.columns):
        report_ws.write(0, col_num, col_name, header_fmt)
        report_ws.set_column(col_num, col_num, 15)
    report_ws.freeze_panes(1, 0)

    writer.close()
    return output.getvalue()
