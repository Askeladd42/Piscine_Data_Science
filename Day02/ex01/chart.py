import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv("/home/plam/sgoinfre/test.env")

def fetch_purchase_data():
    """
    Connect to the PostgreSQL database and fetch purchase data for the specified time range.
    """
    try:
        # Connect to the database
        connection = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),  # Database host
            port=os.getenv("POSTGRES_PORT"),  # Database port
            database=os.getenv("POSTGRES_DB"),  # Database name
            user=os.getenv("POSTGRES_USER"),  # Database user
            password=os.getenv("POSTGRES_PASSWORD")  # Database password
        )
        cursor = connection.cursor()

        # Query to fetch purchase data from October 2022 to February 2023
        query = """
        SELECT event_time, price
        FROM customers
        WHERE event_type = 'purchase'
        AND event_time BETWEEN '2022-10-01' AND '2023-02-28';
        """
        cursor.execute(query)
        results = cursor.fetchall()

        # Convert results to a DataFrame
        df = pd.DataFrame(results, columns=["event_time", "price"])
        df["event_time"] = pd.to_datetime(df["event_time"])  # Ensure event_time is a datetime object
        return df

    except Exception as e:
        print("Error connecting to the database:", e)
        return pd.DataFrame()

    finally:
        if connection:
            cursor.close()
            connection.close()


def create_charts(df):
    """
    Create 3 charts based on the purchase data.
    """
    # Chart 1: Number of customers per month
    df["purchase"] = 1  # Create a column to count purchases
    df["month"] = df["event_time"].dt.to_period("M")  # Extract month from event_time
    df["month"] = df["month"].astype(str)  # Convert Period to string for plotting
    df = df.groupby("month").agg({"purchase": "sum", "price": "mean"}).reset_index()
    df["month"] = pd.to_datetime(df["month"])  # Convert month back to datetime for plotting
    df["month"] = df["month"].dt.strftime('%Y-%m')  # Format month for better readability
    # df["price"] = df["price"].round(2)  # Round price to 2 decimal places
    df = df.sort_values("month")  # Sort by month for plotting
    plt.xlabel("Month")
    plt.ylabel("Number of customers")
    df.plot(x="month", y="purchase", kind="bar", figsize=(10, 6), title="Number of Customers per Month")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # Chart 2: Number of purchases per month
    monthly_counts = df.groupby("month")["price"].count()
    monthly_counts.plot(kind="line", marker="o", figsize=(10, 6), title="Sales per month")
    plt.xlabel("month")
    plt.ylabel("total sales in million of Altairian Dollars")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # Chart 3: Distribution of purchase prices
    df["price"].plot(kind="hist", bins=20, figsize=(10, 6), title="Distribution of Purchase Prices")
    plt.xlabel("month")
    plt.ylabel("Average spend/customer in Altairian Dollars")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # Fetch purchase data
    purchase_data = fetch_purchase_data()

    # Check if data is available
    if not purchase_data.empty:
        # Create the charts
        create_charts(purchase_data)
    else:
        print("No purchase data available for the specified time range.")