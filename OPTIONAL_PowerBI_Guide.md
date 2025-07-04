# Power BI Dashboard Guide for Customer Transaction Insights

This guide provides instructions to create a Power BI dashboard using the `shopping_trends.csv` dataset from the Customer Transaction Insights project.

## Dataset

- The dataset `shopping_trends.csv` contains transaction data including:
  - Customer subscription status
  - Purchase dates
  - Payment methods
  - Purchase frequency
  - Transaction amounts
  - Other relevant customer and transaction details

## Steps to Create the Dashboard

1. **Load Data**
   - Open Power BI Desktop.
   - Click on "Get Data" and select "Text/CSV".
   - Load the `shopping_trends.csv` file.

2. **Data Preparation**
   - Use Power Query Editor to clean and transform data as needed.
   - Create calculated columns for:
     - `Is Returning Customer` (map subscription status to binary)
     - Extract `Month` and `Day of Week` from purchase date.
   - Handle missing or erroneous data.

3. **Create Visuals**
   - **Customer Segmentation**
     - Bar chart and pie chart showing counts of new vs returning customers.
   - **Transaction Frequency**
     - Histogram or bar chart of previous purchases.
   - **Payment Method Preferences**
     - Bar chart and pie chart of payment method usage.
   - **Customer Churn**
     - Bar chart showing churned customers by segment.
   - **Time-Based Trends**
     - Line chart for monthly transaction volume.
     - Bar chart for transactions by day of week.

4. **Add Filters and Slicers**
   - Date range slicer for purchase date.
   - Customer type slicer (New, Returning).
   - Payment method slicer.

5. **Dashboard Layout**
   - Arrange visuals logically for easy interpretation.
   - Add titles, labels, and tooltips for clarity.

6. **Publish and Share**
   - Publish the report to Power BI Service.
   - Share with stakeholders or embed in other platforms.

## Additional Tips

- Use DAX measures for advanced calculations.
- Customize colors to match branding.
- Schedule data refresh if connected to live data sources.

---

For any questions or contributions, please refer to the project GitHub repository.
