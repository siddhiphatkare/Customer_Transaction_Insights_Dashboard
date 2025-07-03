# Customer Transaction Insights Dashboard

This project analyzes a simulated e-commerce dataset to generate business insights, including customer segmentation, payment behavior, transaction frequency, and churn. It demonstrates practical skills in data cleaning, visualization, and interactive dashboard creation using Streamlit.

## Features

- Data cleaning and preparation of transaction data.
- Customer segmentation into new and returning customers.
- Analysis of transaction frequency and payment method preferences.
- Customer churn analysis with adjustable churn threshold.
- Time-based trend analysis of transactions by month and day of week.
- Interactive Streamlit dashboard with filters for date range, customer type, payment methods, and chart visibility toggles.

## Getting Started

### Prerequisites

- Python 3.7 or higher
- Install dependencies:

```bash
pip install -r requirements.txt
```

### Running the Streamlit App

To launch the interactive dashboard, run:

```bash
streamlit run streamlit_app.py
```

Then open the URL provided in the terminal (usually http://localhost:8501 or http://localhost:8502).

### Using the Dashboard

- Use the sidebar filters to select date ranges, customer types (New, Returning), and payment methods.
- Adjust the churn threshold slider to define what counts as churned customers.
- Toggle visibility of different charts to customize your view.
- Explore the "Payment Method Split by Customer Type" expander for detailed cross-tabulation.

## Project Structure

- `Customer_Transaction_Insights_Dashboard.ipynb`: Jupyter notebook with enhanced exploratory data analysis including summary KPIs, interactive filters, and improved storytelling.
- `streamlit_app.py`: Streamlit app providing an interactive dashboard.
- `shopping_trends.csv`: Dataset used for analysis.
- `README.md`: Project documentation.
- `requirements.txt`: Python dependencies.

## Business Impact

This project helps businesses understand customer behavior, identify churn risks, and optimize marketing and retention strategies through data-driven insights.

## Future Enhancements

- Add predictive modeling for customer churn.
- Incorporate more granular time-series forecasting.
- Enhance dashboard with additional interactive visualizations.
- Deploy the app to a cloud platform for wider accessibility.
