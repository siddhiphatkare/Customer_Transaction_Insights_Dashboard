# Customer Transaction Insights Dashboard

This project analyzes a simulated e-commerce dataset to generate actionable business insights, including customer segmentation, payment behavior, transaction frequency, and churn analysis. It showcases skills in data cleaning, visualization, and interactive dashboard development using Streamlit.

## 🚀 Features

- Clean and prepare transactional data for analysis.
- Segment customers into new and returning types.
- Analyze payment method preferences and purchase frequency.
- Perform churn analysis with an adjustable threshold.
- Explore time-based transaction trends by month and weekday.
- Use interactive filters (date range, customer type, payment methods, chart toggles).

## 🛠️ Getting Started

### Prerequisites

- Python 3.7 or higher
- Required libraries:

```bash
pip install -r requirements.txt
```

### Running the Streamlit App Locally

To launch the interactive dashboard locally, run:

```bash
streamlit run streamlit_app.py
```

Then open the URL provided in the terminal (usually http://localhost:8501 or http://localhost:8502).

### Deploying to Streamlit Cloud

1. Push your project repository to GitHub.
2. Go to [Streamlit Cloud](https://streamlit.io/cloud) and sign in.
3. Click "New app" and select your GitHub repository and branch.
4. Configure the app settings if needed and deploy.
5. Your application will be deployed with a public URL that can be shared.


## 🌐Live Demo

You can access the live deployed dashboard here: 
[Customer Transaction Insights Dashboard](https://customer-insights-dashboard.streamlit.app/)

##📊 Using the Dashboard

- Use the sidebar filters to select date ranges, customer types (New, Returning), and payment methods.
- Adjust the churn threshold slider to define what counts as churned customers.
- Toggle visibility of different charts to customize your view.
- Explore the "Payment Method Split by Customer Type" expander for detailed cross-tabulation.

## 📁 Project Structure

- `Customer_Transaction_Insights_Dashboard.ipynb`: Jupyter notebook with enhanced exploratory data analysis including summary KPIs, interactive filters, and improved storytelling.
- `streamlit_app.py`: Streamlit app code providing an interactive dashboard.
- `shopping_trends.csv`: Dataset used for analysis.
- `README.md`: Project overview and documentation.
- `requirements.txt`: Python package dependencies.

## 💼 Business Impact

This project helps businesses understand customer behavior, identify churn risks, and optimize marketing and retention strategies through data-driven insights.

## 🔮 Future Enhancements

- Add predictive modeling for customer churn.
- Incorporate more granular time-series forecasting.
- Add user-level tracking (via customer ID). 
- Enhance visualizations with drill-down and annotations.


