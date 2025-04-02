import numpy as np
import matplotlib.pyplot as plt

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
    plt.title('Pie Chart')

    # Show the plot
    plt.show()

# Example usage

if __name__ == "__main__":
    # import the data from the Data Warehouse in module 01
    data = [15, 30, 45, 10]
    labels = ['A', 'B', 'C', 'D']
    pie_chart(data, labels)
