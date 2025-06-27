import psycopg as pc
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os

# Load environment variables from test.env
load_dotenv("/home/plam/sgoinfre/test.env")


def pie_chart(data, labels):
    """
    Function to create a pie chart.

    Parameters:
    data (list): A list of values to plot.
    labels (list): A list of labels for each slice of the pie.
    """
    # Create a pie chart
    plt.figure(figsize=(8, 8))
    plt.axis('equal')
    plt.tight_layout()  # Adjust layout to prevent clipping of pie chart
    pastel_colors = ['#35618f', '#e59427', '#4fa64f', '#c94c4c']
    plt.pie(
        data,
        labels=labels,
        autopct='%1.1f%%',
        startangle=0,
        wedgeprops={'edgecolor': 'white', 'linewidth': 2},
        colors=pastel_colors[:len(labels)]
        )

    # Equal aspect ratio ensures that pie is drawn as a circle
    plt.title('User Actions on the Site')

    # Show the plot
    plt.show()


def fetch_data():
    """
    Connect to the PostgreSQL database and fetch data for the pie chart.
    """
    connection = None
    cursor = None
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

        # Query to count user actions
        query = """
        SELECT event_type, COUNT(*)
        FROM customers
        WHERE event_type IN ('view', 'cart', 'remove_from_cart', 'purchase')
        GROUP BY event_type;
        """
        cursor.execute(query)
        results = cursor.fetchall()

        # Order to display in the pie chart
        desired_order = ['view', 'cart', 'remove_from_cart', 'purchase']
        data_dict = dict(results)
        data = [data_dict.get(label, 0) for label in desired_order]
        labels = desired_order

        return data, labels

    except Exception as e:
        print("Error connecting to the database:", e)
        return [], []

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


if __name__ == "__main__":
    # Fetch data from the database
    data, labels = fetch_data()

    # Check if data is available
    if data and labels:
        # Create the pie chart
        pie_chart(data, labels)
    else:
        print("No data available to plot.")
