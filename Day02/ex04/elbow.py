import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans # maybe replaced later by a homemade method
from sklearn.preprocessing import StandardScaler # maybe replaced later by a homemade method
from dotenv import load_dotenv
import os

# Load environment variables from test.env
load_dotenv("../../test.env")

def fetch_customer_data():
    """
    Connect to the PostgreSQL database and fetch customer data.
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

        # Query to fetch relevant customer data
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

def elbow_method(data):
    """
    Perform the Elbow Method to determine the optimal number of clusters.
    """
    # Standardize the data
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(data)

    # Calculate the Within-Cluster-Sum-of-Squares (WCSS) for different cluster counts
    wcss = []
    for k in range(1, 11):  # Test cluster counts from 1 to 10
        kmeans = KMeans(n_clusters=k, random_state=42)
        kmeans.fit(scaled_data)
        wcss.append(kmeans.inertia_)

    # Plot the Elbow Method graph
    plt.figure(figsize=(8, 6))
    plt.plot(range(1, 11), wcss, marker='o', linestyle='--')
    plt.title('Elbow Method for Optimal Clusters')
    plt.xlabel('Number of Clusters')
    plt.ylabel('WCSS (Within-Cluster-Sum-of-Squares)')
    plt.xticks(range(1, 11))
    plt.grid()
    plt.show()

if __name__ == "__main__":
    # Fetch customer data
    customer_data = fetch_customer_data()

    # Check if data is available
    if not customer_data.empty:
        # Use only numerical columns for clustering
        numerical_data = customer_data[["order_count", "total_spent"]]

        # Perform the Elbow Method
        elbow_method(numerical_data)
    else:
        print("No customer data available.")