import psycopg2
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os

# Load environment variables from test.env
load_dotenv("../../test.env")

def pie_chart(data, labels):
    """
    Function to create a pie chart.

    Parameters:
    data (list): A list of values to plot.
    labels (list): A list of labels for each slice of the pie.
    """
    # Create a pie chart
    plt.figure(figsize=(8, 8))
    plt.pie(data, labels=labels, autopct='%1.1f%%', startangle=140)

    # Equal aspect ratio ensures that pie is drawn as a circle
    plt.axis('equal')
    plt.title('User Actions on the Site')

    # Show the plot
    plt.show()


def fetch_data():
    """
    Connect to the PostgreSQL database and fetch data for the pie chart.
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

        # Query to count user actions
        query = """
        SELECT event_type, COUNT(*) 
        FROM customers 
        WHERE event_type IN ('view', 'cart', 'remove_from_cart', 'purchase')
        GROUP BY event_type;
        """
        cursor.execute(query)
        results = cursor.fetchall()

        # Process the results
        labels = [row[0] for row in results]
        data = [row[1] for row in results]

        return data, labels

    except Exception as e:
        print("Error connecting to the database:", e)
        return [], []

    finally:
        if connection:
            cursor.close()
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
