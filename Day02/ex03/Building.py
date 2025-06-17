import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv("/home/plam/sgoinfre/test.env")

def fetch_order_data():
    """
    Connect to the PostgreSQL database and fetch order data.
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

        # Query to fetch order data
        query = """
        SELECT user_id, COUNT(*) AS order_count, SUM(price) AS total_spent
        FROM customers
        WHERE event_type = 'purchase'
        GROUP BY user_id;
        """
        cursor.execute(query)
        results = cursor.fetchall()

        # Convert results to a DataFrame
        df = pd.DataFrame(results, columns=["user_id", "order_count", "total_spent"])
        return df

    except Exception as e:
        print("Error connecting to the database:", e)
        return pd.DataFrame()

    finally:
        if connection:
            cursor.close()
            connection.close()

def create_bar_charts(df):
    """
    Create bar charts for the number of orders and Altairian Dollars spent.
    """
    # Bar chart: Number of orders by frequency
    plt.figure(figsize=(10, 6))
    df["order_count"].value_counts().sort_index().plot(kind="bar", color="skyblue")
    plt.title("Number of Orders by Frequency")
    plt.xlabel("Number of Orders")
    plt.ylabel("Frequency")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.show()

    # Bar chart: Altairian Dollars spent by customers
    plt.figure(figsize=(10, 6))
    df["total_spent"].plot(kind="bar", color="lightgreen")
    plt.title("Altairian Dollars Spent by Customers")
    plt.xlabel("Customer Index")
    plt.ylabel("Total Spent (Altairian Dollars)")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Fetch order data
    order_data = fetch_order_data()

    # Check if data is available
    if not order_data.empty:
        # Create the bar charts
        create_bar_charts(order_data)
    else:
        print("No order data available.")
