import psycopg as pc
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from dotenv import load_dotenv
import os

# Load environment variables from test.env
load_dotenv("/home/plam/sgoinfre/test.env")


def fetch_customer_data():
    """
    Connect to the PostgreSQL database and fetch customer data.
    """
    try:
        # Connect to the database using environment variables
        connection = pc.connect(
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
        df = pd.DataFrame(
            results, columns=["user_id", "order_count", "total_spent"]
            )
        return df

    except Exception as e:
        print("Error connecting to the database:", e)
        return pd.DataFrame()

    finally:
        if connection:
            cursor.close()
            connection.close()


def perform_clustering(data, n_clusters=4):
    """
    Perform clustering on the customer data.
    """
    # Standardize the data
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(data)

    # Apply KMeans clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(scaled_data)

    # Add cluster labels to the original data
    data["cluster"] = clusters
    return data, kmeans


def visualize_clusters(data):
    """
    Create visualizations for the customer clusters.
    """
    # Scatter plot: Total spent vs. Order count, colored by cluster
    plt.figure(figsize=(10, 6))
    for cluster in data["cluster"].unique():
        cluster_data = data[data["cluster"] == cluster]
        plt.scatter(
            cluster_data["order_count"],
            cluster_data["total_spent"],
            label=f"Cluster {cluster}"
            )
    plt.title("Customer Clusters: Total Spent vs. Order Count")
    plt.xlabel("Order Count")
    plt.ylabel("Total Spent (Altairian Dollars)")
    plt.legend()
    plt.grid()
    plt.show()

    # Bar plot: Average total spent per cluster
    avg_spent_per_cluster = data.groupby("cluster")["total_spent"].mean()
    avg_spent_per_cluster.plot(kind="bar", color="skyblue", figsize=(10, 6))
    plt.title("Average Total Spent per Cluster")
    plt.xlabel("Cluster")
    plt.ylabel("Average Total Spent (Altairian Dollars)")
    plt.xticks(rotation=0)
    plt.grid()
    plt.show()


if __name__ == "__main__":
    # Fetch customer data
    customer_data = fetch_customer_data()

    # Check if data is available
    if not customer_data.empty:
        # Use only numerical columns for clustering
        numerical_data = customer_data[["order_count", "total_spent"]]

        # Perform clustering
        clustered_data, kmeans_model = perform_clustering(
            numerical_data, n_clusters=4
            )

        # Visualize the clusters
        visualize_clusters(clustered_data)
    else:
        print("No customer data available.")
