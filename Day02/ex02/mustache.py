import psycopg2
import pandas as pd
import matplotlib.pyplot as plt

def fetch_purchase_data():
    """
    Connect to the PostgreSQL database and fetch purchase data.
    """
    try:
        # Connect to the database
        connection = psycopg2.connect(
            host="piscineds",  # Replace with your database host
            port="5432",       # Replace with your database port
            database="postgres_db",  # Replace with your database name
            user="plam",       # Replace with your database user
            password="mysecretpassword"  # Replace with your database password
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
    mean = df["price"].mean()
    median = df["price"].median()
    min_price = df["price"].min()
    max_price = df["price"].max()
    q1 = df["price"].quantile(0.25)
    q2 = df["price"].quantile(0.50)  # Same as median
    q3 = df["price"].quantile(0.75)

    print("Statistics for item prices:")
    print(f"Mean: {mean}")
    print(f"Median: {median}")
    print(f"Min: {min_price}")
    print(f"Max: {max_price}")
    print(f"First Quartile (Q1): {q1}")
    print(f"Second Quartile (Q2/Median): {q2}")
    print(f"Third Quartile (Q3): {q3}")

def create_box_plot(df):
    """
    Create a box plot for the price column.
    """
    plt.figure(figsize=(8, 6))
    plt.boxplot(df["price"], vert=False, patch_artist=True, boxprops=dict(facecolor="lightblue"))
    plt.title("Box Plot of Item Prices")
    plt.xlabel("Price (Altairian Dollars)")
    plt.show()

if __name__ == "__main__":
    # Fetch purchase data
    purchase_data = fetch_purchase_data()

    # Check if data is available
    if not purchase_data.empty:
        # Calculate and print statistics
        calculate_statistics(purchase_data)

        # Create a box plot
        create_box_plot(purchase_data)
    else:
        print("No purchase data available.")