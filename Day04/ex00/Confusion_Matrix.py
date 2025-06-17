import matplotlib.pyplot as plt
import numpy as np


if __name__ == "__main__":
    y_true = [1, 0, 1, 1, 0, 1, 0, 0, 1, 0]
    y_pred = [1, 0, 1, 0, 0, 1, 1, 0, 1, 0]

    # Create confusion matrix
    confusion_matrix = np.zeros((2, 2), dtype=int)
    for true_label, pred_label in zip(y_true, y_pred):
        confusion_matrix[true_label][pred_label] += 1

    # Plot confusion matrix
    plt.imshow(confusion_matrix, cmap='Blues', interpolation='nearest')
    plt.colorbar()
    plt.xticks(ticks=[0, 1], labels=['Predicted: No', 'Predicted: Yes'])
    plt.yticks(ticks=[0, 1], labels=['Actual: No', 'Actual: Yes'])
    plt.title('Confusion Matrix')
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')
    plt.show()
    print("Confusion Matrix:")
    print(confusion_matrix)
    print("True Positives:", confusion_matrix[1][1])
    print("True Negatives:", confusion_matrix[0][0])
    print("False Positives:", confusion_matrix[0][1])
    print("False Negatives:", confusion_matrix[1][0])
    print("Accuracy:", (confusion_matrix[0][0] + confusion_matrix[1][1]) / np.sum(confusion_matrix))
    print("Precision:", confusion_matrix[1][1] / (confusion_matrix[1][1] + confusion_matrix[0][1]))
    print("Recall:", confusion_matrix[1][1] / (confusion_matrix[1][1] + confusion_matrix[1][0]))