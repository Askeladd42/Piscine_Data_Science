import psycopg as pc
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv("/home/plam/sgoinfre/test.env")


def fetch_purchase_data():
    """
    Connect to the PostgreSQL database and fetch purchase data.
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

        # Query to fetch purchase data
        query = """
        SELECT price
        FROM customers
        WHERE event_type = 'purchase';
        """
        cursor.execute(query)
        results = cursor.fetchall()

        # Convert results to a DataFrame
        df = pd.DataFrame(results, columns=["price"])
        return df

    except Exception as e:
        print("Error connecting to the database:", e)
        return pd.DataFrame()

    finally:
        if connection:
            cursor.close()
            connection.close()


def calculate_statistics(df):
    """
    Calculate and print statistics for the price column.
    """
    count = df["price"].count()
    mean = df["price"].mean()
    std = df["price"].std()
    min_price = df["price"].min()
    q1 = df["price"].quantile(0.25)
    q2 = df["price"].quantile(0.50)  # Same as median
    q3 = df["price"].quantile(0.75)
    max_price = df["price"].max()

    print(f"count        {float(count):.6f}")
    print(f"mean         {float(mean):.6f}")
    print(f"std          {float(std):.6f}")
    print(f"min          {float(min_price):.6f}")
    print(f"25%          {float(q1):.6f}")
    print(f"50%          {float(q2):.6f}")
    print(f"75%          {float(q3):.6f}")
    print(f"max          {float(max_price):.6f}")


def create_box_plot(df):
    """
    Create a box plot for the price column, a zoomed-in version and
    a box plot of the average basket price per user.
    """
    plt.figure(figsize=(8, 6))
    plt.boxplot(
        df["price"], vert=False, patch_artist=True, boxprops=dict(
            facecolor="lightblue"
            )
        )
    plt.title("Box plot of the price of the items purchased")
    plt.xlabel("price")
    plt.show()

    # Create a zoomed-in box plot
    plt.figure(
        figsize=(8, 6)  # Adjust height to reduce space above and below
    )
    plt.boxplot(
        df["price"], vert=False, patch_artist=True, boxprops=dict(
            facecolor="lightgreen"
        )
    )
    plt.xlabel("price")
    plt.xlim(-1, 12)
    plt.ylim(0.9, 1.1)
    plt.show()

    # Filter only purchase events
    if "event_type" in df.columns:
        df = df[df["event_type"] == "purchase"]

    # Ensure user_id exists in the DataFrame
    if "user_id" not in df.columns:
        df["user_id"] = 1  # Assign a default user_id if missing

    # Calculate average basket price per user
    avg_basket_price = df.groupby("user_id")["price"].mean().reset_index()

    plt.figure(figsize=(8, 6))
    plt.boxplot(
        avg_basket_price["price"],
        vert=False, patch_artist=True,
        boxprops=dict(
            facecolor="orange"
        )
    )
    plt.title("Box plot of the average basket price per user")
    plt.xlabel("Average basket price")
    plt.ylim(0.9, 1.1)
    plt.show()


if __name__ == "__main__":
    # Fetch purchase data
    purchase_data = fetch_purchase_data()

    # Check if data is available
    if not purchase_data.empty:
        # Calculate and print statistics
        calculate_statistics(purchase_data)

        # Create the box plots
        create_box_plot(purchase_data)
    else:
        print("No purchase data available.")
