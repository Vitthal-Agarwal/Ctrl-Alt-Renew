# scripts/data_preparation.py

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
import joblib
import os
import psutil
import time
from threading import Thread


def prepare_data():
    # Load the dataset
    df = pd.read_csv("mock_cpu_usage_data.csv")

    # Convert 'Timestamp' to datetime
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])

    # Extract time-based features
    df["Hour"] = df["Timestamp"].dt.hour
    df["Minute"] = df["Timestamp"].dt.minute
    df["DayOfWeek"] = df["Timestamp"].dt.dayofweek  # Monday=0, Sunday=6
    df["IsWeekend"] = df["DayOfWeek"].apply(lambda x: 1 if x >= 5 else 0)
    df["TimeOfDay"] = df["Hour"] * 60 + df["Minute"]

    # Sort by Timestamp
    df = df.sort_values("Timestamp").reset_index(drop=True)

    # **Redefine 'Activity_Status' based on new CPU usage ranges**
    def map_usage_level(cpu_usage):
        if cpu_usage < 10:
            return "Idle"
        elif 10 <= cpu_usage < 50:
            return "Medium Usage"
        elif 50 <= cpu_usage < 75:
            return "High Usage"
        else:
            return "Very High Usage"

    df["Activity_Status"] = df["CPU_Usage"].apply(map_usage_level)

    # Map Activity_Status to numerical labels
    activity_mapping = {
        "Idle": 0,
        "Medium Usage": 1,
        "High Usage": 2,
        "Very High Usage": 3,
    }
    df["Target"] = df["Activity_Status"].map(activity_mapping)

    # Print class distribution
    class_counts = df["Target"].value_counts()
    print("Class distribution:")
    print(class_counts)

    return df


def train_model(df):
    # Define feature columns
    feature_cols = ["Hour", "DayOfWeek", "IsWeekend", "TimeOfDay"]

    X = df[feature_cols]
    y = df["Target"]

    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False  # Do not shuffle for time series data
    )

    # **Compute class weights**
    from sklearn.utils import class_weight

    class_weights_array = class_weight.compute_class_weight(
        class_weight="balanced", classes=np.unique(y_train), y=y_train
    )
    class_weights_dict = dict(zip(np.unique(y_train), class_weights_array))

    # **Create sample weights**
    sample_weights = y_train.apply(lambda x: class_weights_dict[x])

    # Initialize and train the model
    model = XGBClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        objective="multi:softmax",  # Use softmax for multi-class classification
        num_class=4,  # Number of classes updated to 4
        random_state=42,
        use_label_encoder=False,
        eval_metric="mlogloss",
    )
    model.fit(X_train, y_train, sample_weight=sample_weights)

    # **Evaluate the model**
    from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

    y_pred = model.predict(X_test)

    # Calculate accuracy
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {accuracy:.2f}")

    # Classification report
    target_names = ["Idle", "Light Usage", "Heavy Usage", "Very High Usage"]
    print(classification_report(y_test, y_pred, target_names=target_names))

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    print("Confusion Matrix:")
    print(cm)

    # Save the model
    os.makedirs("models", exist_ok=True)
    joblib.dump(model, "models/idle_time_predictor.pkl")
    print("Model saved to 'models/idle_time_predictor.pkl'.")

    return model


def predict_future_usage(model, df):
    # **Simulate future time intervals (next 7 days)**
    future_timestamps = pd.date_range(
        start=df["Timestamp"].iloc[-1] + pd.Timedelta(minutes=15),
        periods=96 * 7,  # Next 7 days at 15-minute intervals
        freq="15T",
    )

    # (existing code)

    # Create a DataFrame for future predictions
    future_df = pd.DataFrame({"Timestamp": future_timestamps})

    # Extract features
    future_df["Hour"] = future_df["Timestamp"].dt.hour
    future_df["Minute"] = future_df["Timestamp"].dt.minute
    future_df["DayOfWeek"] = future_df["Timestamp"].dt.dayofweek
    future_df["IsWeekend"] = future_df["DayOfWeek"].apply(lambda x: 1 if x >= 5 else 0)
    future_df["TimeOfDay"] = future_df["Hour"] * 60 + future_df["Minute"]

    # Define feature columns
    feature_cols = ["Hour", "DayOfWeek", "IsWeekend", "TimeOfDay"]

    future_X = future_df[feature_cols]
    future_predictions = model.predict(future_X)

    # Add predictions to the DataFrame
    future_df["Predicted_Status"] = future_predictions
    activity_mapping_rev = {
        0: "Idle",
        1: "Medium Usage",
        2: "High Usage",
        3: "Very High Usage",
    }
    future_df["Predicted_Status_Label"] = future_df["Predicted_Status"].map(
        activity_mapping_rev
    )

    # Print predicted statuses
    print("Predicted statuses for future timestamps:")
    print(future_df[["Timestamp", "Predicted_Status_Label"]])

    return future_df


if __name__ == "__main__":
    df = prepare_data()
    model = train_model(df)
    future_df = predict_future_usage(model, df)
