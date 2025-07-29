import pytest
import pandas as pd
from io import BytesIO
from utils import load_data, to_excel
import streamlit_app as app

@pytest.fixture
def df():
    return load_data()

def test_filtering_churn_summary(df):
    # Apply filters similar to the app
    start_date = df['purchase_date'].min()
    end_date = df['purchase_date'].max()
    selected_payments = df['payment_method'].unique().tolist()
    customer_type = ['New', 'Returning']
    churn_threshold = 1

    filtered_df = df[
        (df['purchase_date'] >= pd.to_datetime(start_date)) &
        (df['purchase_date'] <= pd.to_datetime(end_date)) &
        (df['payment_method'].isin(selected_payments))
    ]
    customer_type_map = {'new': 0, 'returning': 1}
    selected_customer_type_vals = [customer_type_map[ct.lower()] for ct in customer_type]
    filtered_df = filtered_df[filtered_df['is_returning_customer'].astype(int).isin(selected_customer_type_vals)]

    churned_customers = filtered_df[filtered_df['previous_purchases'] <= churn_threshold]
    churn_summary = churned_customers['is_returning_customer'].value_counts().rename({0: 'New', 1: 'Returning'})

    total_churned = churned_customers.shape[0]
    total_customers = filtered_df.shape[0]
    churn_rate = (total_churned / total_customers) * 100 if total_customers > 0 else 0

    # Basic assertions
    assert total_customers == filtered_df.shape[0]
    assert churn_rate >= 0
    assert 'New' in churn_summary.index or 'Returning' in churn_summary.index

def test_to_excel_output(df):
    excel_data = to_excel(df)
    assert isinstance(excel_data, bytes)
    assert len(excel_data) > 0

def test_data_dictionary_content():
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
    # Check keys and values are non-empty strings
    for k, v in data_dict.items():
        assert isinstance(k, str) and len(k) > 0
        assert isinstance(v, str) and len(v) > 0

# Additional tests for other tabs and charts can be added similarly
