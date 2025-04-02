import numpy as np
import matplotlib.pyplot as plt
import psycopg2


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
            host="piscineds",  # Replace with your database host
            port="5432",       # Replace with your database port
            database="postgres_db",  # Replace with your database name
            user="plam",       # Replace with your database user
            password="mysecretpassword"  # Replace with your database password
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
