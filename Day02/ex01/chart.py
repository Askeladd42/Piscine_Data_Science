import psycopg as pc
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv("/home/plam/sgoinfre/test.env")


def fetch_purchase_data():
    """
    Connect to the PostgreSQL database and fetch purchase data for the
    specified time range.
    """
    try:
        # Connect to the database
        connection = pc.connect(
            host="localhost",
            port="5432",
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD")
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

        # Convert results to a DataFrame, including month extraction
        df = pd.DataFrame(results, columns=["event_time", "price"])
        df["event_time"] = pd.to_datetime(df["event_time"])
        df["month"] = df["event_time"].dt.to_period("M").astype(str)
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
    # Chart 1: Nombre d'achats par mois (line chart)
    monthly_purchases = df.groupby("month")["price"].count().reset_index()
    plt.figure(figsize=(10, 6))
    plt.plot(
        monthly_purchases["month"], monthly_purchases["price"], marker="o"
    )
    plt.xlabel("Month")
    plt.ylabel("Number of purchases")
    plt.title("Number of Purchases per Month")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # Chart 2: Total des ventes par mois (bar chart)
    monthly_sales = df.groupby("month")["price"].sum().reset_index()
    plt.figure(figsize=(10, 6))
    plt.bar(monthly_sales["month"], monthly_sales["price"])
    plt.xlabel("Month")
    plt.ylabel("Total sales")
    plt.title("Total Sales per Month")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # Chart 3: Distribution des prix d'achat par mois (stacked area)
    df["price"] = df["price"].round(2)
    price_bins = pd.cut(df["price"], bins=10)
    stacked = df.groupby(["month", price_bins]).size().unstack(fill_value=0)
    stacked = stacked.sort_index()
    plt.figure(figsize=(10, 6))
    stacked.plot(kind="area", stacked=True, colormap="tab20", alpha=0.7)
    plt.xlabel("Month")
    plt.ylabel("Number of purchases")
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
