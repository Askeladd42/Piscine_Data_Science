import pandas as pd
import matplotlib.pyplot as plt

def plot_test_knight_histogram(file_path):
    """
    Create a histogram to visualize the data in Test_knight.csv.
    """
    # Load the CSV file
    data = pd.read_csv(file_path)

    # Plot histograms for all numerical columns
    data.hist(bins=20, figsize=(10, 8), color="skyblue", edgecolor="black")
    plt.suptitle("Histogram of Test_knight.csv Features", fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()

def plot_train_knight_histogram(file_path):
    """
    Create a histogram to understand the interaction between knight's skills (features)
    and the "knight" column (target) in Train_knight.csv.
    """
    # Load the CSV file
    data = pd.read_csv(file_path)

    # Separate features and target
    features = data.drop(columns=["knight"])  # All columns except "knight"
    target = data["knight"]

    # Plot histograms for each feature grouped by the "knight" column
    for column in features.columns:
        plt.figure(figsize=(8, 6))
        for knight_type in target.unique():
            subset = data[data["knight"] == knight_type]
            plt.hist(subset[column], bins=20, alpha=0.5, label=f"Knight {knight_type}", edgecolor="black")
        plt.title(f"Histogram of {column} by Knight Type", fontsize=14)
        plt.xlabel(column)
        plt.ylabel("Frequency")
        plt.legend()
        plt.grid()
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    # File paths
    test_file = "Test_knight.csv"
    train_file = "Train_knight.csv"

    # Plot histograms for Test_knight.csv
    print("Visualizing Test_knight.csv...")
    plot_test_knight_histogram(test_file)

    # Plot histograms for Train_knight.csv
    print("Visualizing Train_knight.csv...")
    plot_train_knight_histogram(train_file)
