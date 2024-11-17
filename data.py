import pandas as pd
import numpy as np
import datetime
import random

# Parameters
start_date = datetime.datetime(2023, 7, 1)
end_date = datetime.datetime(2023, 9, 30)
time_interval = datetime.timedelta(minutes=15)  # Data every 15 minutes

# Generate date range
date_range = pd.date_range(start=start_date, end=end_date, freq="15T")

# Initialize list to store data
data = []

for timestamp in date_range:
    day_of_week = timestamp.weekday()  # Monday=0, Sunday=6
    hour = timestamp.hour
    minute = timestamp.minute

    # Initialize CPU usage
    cpu_usage = 0

    # Weekday patterns
    if day_of_week < 5:
        if 9 <= hour < 17:
            # Work hours
            cpu_usage = np.random.normal(70, 10)  # Mean 70%, SD 10%
        elif 17 <= hour < 22:
            # Evening leisure hours
            cpu_usage = np.random.normal(40, 10)  # Mean 40%, SD 10%
        elif 8 <= hour < 9 or 22 <= hour < 23:
            # Morning prep and late evening
            cpu_usage = np.random.normal(20, 5)  # Mean 20%, SD 5%
        else:
            # Night time
            cpu_usage = np.random.normal(5, 2)  # Mean 5%, SD 2%
    else:
        # Weekend patterns
        if 10 <= hour < 24:
            # Daytime and evening
            cpu_usage = np.random.normal(30, 15)  # Mean 30%, SD 15%
        else:
            # Early morning
            cpu_usage = np.random.normal(10, 5)  # Mean 10%, SD 5%

    # Clamp CPU usage between 0% and 100%
    cpu_usage = max(0, min(100, cpu_usage))

    # Determine activity status
    if cpu_usage < 10:
        activity_status = "Idle"
    elif cpu_usage < 50:
        activity_status = "Light Usage"
    elif cpu_usage < 75:
        activity_status = "High Usage"
    else:
        activity_status = "Very High Usage"

    # Append data point
    data.append(
        {
            "Timestamp": timestamp,
            "CPU_Usage": cpu_usage,
            "Activity_Status": activity_status,
        }
    )

# Create DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv("mock_cpu_usage_data.csv", index=False)

print("Mock data generated and saved to 'mock_cpu_usage_data.csv'.")
