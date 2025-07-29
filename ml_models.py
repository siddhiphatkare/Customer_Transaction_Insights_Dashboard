import pandas as pd
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression
import numpy as np

class MLModels:
    def __init__(self):
        self.churn_model = None
        self.sales_model = None

    def train_churn_model(self, df):
        # Placeholder: train a churn prediction model
        # For demonstration, train a simple RandomForestClassifier on previous_purchases and is_returning_customer
        features = df[['previous_purchases']].fillna(0)
        target = (df['previous_purchases'] <= 1).astype(int)  # churn if <= 1 previous purchase
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(features, target)
        self.churn_model = model

    def predict_churn(self, df):
        if self.churn_model is None:
            self.train_churn_model(df)
        features = df[['previous_purchases']].fillna(0)
        preds = self.churn_model.predict(features)
        return preds

    def train_sales_forecast_model(self, df):
        # Placeholder: train a simple linear regression on monthly revenue
        if 'purchase_date' not in df or 'price' not in df:
            self.sales_model = None
            return
        monthly_revenue = df.groupby(df['purchase_date'].dt.to_period('M'))['price'].sum().reset_index()
        monthly_revenue['month_num'] = monthly_revenue['purchase_date'].dt.month
        X = monthly_revenue[['month_num']]
        y = monthly_revenue['price']
        model = LinearRegression()
        model.fit(X, y)
        self.sales_model = model

    def forecast_sales(self, months_ahead=3):
        if self.sales_model is None:
            return []
        last_month = 12  # Simplification: assume December is last month
        future_months = np.array(range(last_month + 1, last_month + 1 + months_ahead)).reshape(-1, 1)
        preds = self.sales_model.predict(future_months)
        return preds

def cluster_customers(df, n_clusters=3):
    # Simple clustering based on age and previous_purchases
    features = df[['age', 'previous_purchases']].fillna(0)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(features)
    return clusters
