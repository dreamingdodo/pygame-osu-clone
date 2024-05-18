import pandas as pd
import matplotlib.pyplot as plt

# Load the data from the file
data = pd.read_csv('performance_log.txt', delimiter=', ')

# Check for missing values
print(data.isnull().sum())

# Drop any rows with missing values
data.dropna(inplace=True)

# Convert columns to appropriate data types if needed
data['FPS'] = data['FPS'].astype(int)
data['CPU Usage (%)'] = data['CPU Usage (%)'].astype(float)
data['Memory Usage (MB)'] = data['Memory Usage (MB)'].astype(float)

# Summary statistics
summary_stats = data.describe()
print(summary_stats)

# Plot FPS over time
plt.figure(figsize=(12, 6))
plt.plot(data['Time'], data['FPS'], label='FPS', marker='.')
plt.xlabel('Time')
plt.ylabel('FPS')
plt.title('FPS over Time')
plt.legend()
plt.xticks(rotation=45)
plt.show()

# Plot CPU usage over time
plt.figure(figsize=(12, 6))
plt.plot(data['Time'], data['CPU Usage (%)'], label='CPU Usage (%)', color='orange', marker='.')
plt.xlabel('Time')
plt.ylabel('CPU Usage (%)')
plt.title('CPU Usage over Time')
plt.legend()
plt.xticks(rotation=45)
plt.show()

# Plot Memory usage over time
plt.figure(figsize=(12, 6))
plt.plot(data['Time'], data['Memory Usage (MB)'], label='Memory Usage (MB)', color='green', marker='.')
plt.xlabel('Time')
plt.ylabel('Memory Usage MB')
plt.title('Memory Usage over Time')
plt.legend()
plt.xticks(rotation=45)
plt.show()