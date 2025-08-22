import psycopg as pc
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
        connection = pc.connect(
            host="localhost",
            port="5432",
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD")
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
        df = pd.DataFrame(results, columns=[
            "user_id", "order_count", "total_spent"
            ])
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
    # Bar chart: Number of orders (customers in y)
    # according to the frequency (in x)
    plt.figure(figsize=(10, 6))
    order_frequency = df["order_count"].value_counts().sort_index()
    plt.bar(order_frequency.index, order_frequency.values, color="skyblue")
    plt.title("Number of Orders according to the Frequency")
    plt.xlabel("Frequency")
    plt.ylabel("Customers")
    plt.xticks(range(0, int(order_frequency.index.max()) + 10, 10))
    plt.xlim(0, 40)
    plt.yticks(range(0, int(order_frequency.values.max()) + 10000, 10000))
    plt.tight_layout()
    plt.show()

    # Bar chart: Number of customers by monetary value spent
    plt.figure(figsize=(10, 6))
    monetary_value = df.groupby("total_spent")["user_id"].count().reset_index()
    monetary_value.columns = ["total_spent", "customer_count"]
    plt.bar(
        monetary_value["total_spent"],
        monetary_value["customer_count"],
        color="skyblue"
    )
    plt.title("Number of Customers by Monetary Value Spent")
    plt.xlabel("Monetary Value (Altairian Dollars)")
    plt.ylabel("Number of Customers")
    plt.xticks(range(0, 221, 50))
    plt.xlim(0, 220)
    plt.yticks(range(0, monetary_value["customer_count"].max() + 5000, 5000))
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

