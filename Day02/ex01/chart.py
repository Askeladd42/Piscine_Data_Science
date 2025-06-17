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
    # Chart 1: Number of customers per month with a line chart
    monthly_customers = df.groupby("month")["purchase"].sum().reset_index()
    plt.figure(figsize=(10, 6))
    plt.plot(monthly_customers["month"], monthly_customers["purchase"], marker="o")
    plt.xlabel("Month")
    plt.ylabel("Number of customers")
    plt.title("Number of Customers per Month")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # Chart 2: Number of purchases per month with an histogram chart
    monthly_purchases = df.groupby("month")["price"].count().reset_index()
    plt.figure(figsize=(10, 6))
    plt.bar(monthly_purchases["month"], monthly_purchases["price"])
    plt.xlabel("Month")
    plt.ylabel("Total sales in milliom of A")
    plt.title("Number of Purchases per Month")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # Chart 3: Distribution of purchase prices with a stacked area chart
    df["price"] = df["price"].round(2)
    price_bins = pd.cut(df["price"], bins=10)
    stacked = df.groupby(["month", price_bins]).size().unstack(fill_value=0)
    stacked = stacked.sort_index()
    plt.figure(figsize=(10, 6))
    stacked.plot(kind="area", stacked=True, colormap="tab20", alpha=0.7)
    plt.xlabel("Month")
    plt.ylabel("Average spend/customers in A")
    plt.title("Stacked Area Chart: Distribution of Purchase Prices by Month")
    plt.xticks(rotation=45)
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