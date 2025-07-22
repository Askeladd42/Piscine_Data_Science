import psycopg as pc
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
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
            SELECT event_time, price, user_id
            FROM customers
            WHERE event_type = 'purchase'
            AND event_time BETWEEN '2022-10-01' AND '2023-02-28';
        """
        cursor.execute(query)
        results = cursor.fetchall()

        # Convert results to a DataFrame, including month extraction
        df = pd.DataFrame(results, columns=["event_time", "price", "user_id"])
        df["event_time"] = pd.to_datetime(df["event_time"])
        df["day"] = df["event_time"].dt.date.astype(str)
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
    # Chart 1: number of unique customers per day (line chart)
    daily_customers = df.groupby("day")["user_id"].nunique().reset_index()
    daily_customers["day"] = pd.to_datetime(daily_customers["day"])
    daily_customers = daily_customers.sort_values("day")

    plt.figure(figsize=(12, 6))
    plt.plot(
        daily_customers["day"],
        daily_customers["user_id"],
    )
    plt.xlabel("Month")
    plt.ylabel("Number of customers")
    plt.title("Number of customers per month")
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))  # Month format
    plt.xticks(rotation=45)
    plt.xlim(daily_customers["day"].min(), daily_customers["day"].max())
    plt.tight_layout()
    plt.show()

    # Chart 2: Total sales by month (bar chart)
    df["month"] = pd.to_datetime(df["day"]).dt.to_period("M")
    monthly_sales = df.groupby("month")["price"].sum().reset_index()
    # Convert 'month' to datetime for plotting
    monthly_sales["month_start"] = monthly_sales["month"].dt.to_timestamp()
    plt.figure(figsize=(10, 6))
    plt.bar(
        monthly_sales["month_start"],
        monthly_sales["price"],
        color="#35618f",
        width=20
    )
    plt.xlabel("Month")
    plt.ylabel("Total sales")
    plt.title("Total Sales per Month")
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # Chart 3: Average spending per customer per day (area chart)
    average_spending = df.groupby("day").agg(
        price=("price", "mean"),
        user_id=("user_id", "nunique")
    ).reset_index()
    average_spending["day"] = pd.to_datetime(average_spending["day"])
    plt.figure(figsize=(10, 6))
    plt.fill_between(
        average_spending["day"],
        average_spending["price"],
        color="#6baed6",
        alpha=0.7
    )
    plt.plot(
        average_spending["day"],
        average_spending["price"],
        color="#35618f",
    )
    plt.xlabel("Month")
    plt.ylabel("Average spend/customers in A")
    plt.title("Area Chart: Average Spend/Customer per Month")
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    plt.xticks(rotation=45)
    plt.xlim(average_spending["day"].min(), average_spending["day"].max())
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
