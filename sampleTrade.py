#
# import pandas as pd
# import matplotlib.pyplot as plt
#
# heating_oil_data = pd.read_csv('historical_data/HO=F.csv', skiprows=3, names=["Date", "Price"])
# brent_oil_data = pd.read_csv('historical_data/BZ=F.csv', skiprows=3, names=["Date", "Price"])
#
# print(heating_oil_data["Date"])
# print(brent_oil_data["Date"])
#
# for df in [heating_oil_data, brent_oil_data]:
#     df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
#     df["Price"] = pd.to_numeric(df["Price"], errors='coerce')
#     df.dropna(inplace=True)
#
# # Merge the data on Date
# merged_data = pd.merge(heating_oil_data, brent_oil_data, on="Date", suffixes=('_HO', '_Brent'))
#
# # Filter data for the 2014-2024 range
# filtered_data = merged_data[(merged_data["Date"].dt.year >= 2014) & (merged_data["Date"].dt.year <= 2024)]
#
# # Remove rows with zero or negative prices
# filtered_data = filtered_data[(filtered_data["Price_HO"] > 0) & (filtered_data["Price_Brent"] > 0)]
#
# # Calculate the price ratio
# filtered_data["Price_Ratio"] = filtered_data["Price_Brent"] / filtered_data["Price_HO"]
#
# # Calculate statistics
# mean_ratio = filtered_data["Price_Ratio"].mean()
# std_ratio = filtered_data["Price_Ratio"].std()
#
# # Debugging output
# print(f"Mean Ratio: {mean_ratio}")
# print(f"Standard Deviation: {std_ratio}")
# print(filtered_data.head())
#
# # Plot the data
# plt.figure(figsize=(12, 6))
# plt.plot(filtered_data["Date"], filtered_data["Price_Ratio"], label="Price Ratio", color='blue')
# plt.axhline(mean_ratio, color='green', linestyle='--', label="Mean")
# plt.axhline(mean_ratio + std_ratio, color='orange', linestyle='--', label="Mean + 1 STD")
# plt.axhline(mean_ratio - std_ratio, color='orange', linestyle='--', label="Mean - 1 STD")
# plt.axhline(mean_ratio + 2 * std_ratio, color='red', linestyle='--', label="Mean + 2 STD")
# plt.axhline(mean_ratio - 2 * std_ratio, color='red', linestyle='--', label="Mean - 2 STD")
#
# # Customize the plot
# plt.title("Price Ratio Between Heating Oil Futures and Brent Oil Futures (2014-2024)")
# plt.xlabel("Date")
# plt.ylabel("Price Ratio")
# plt.legend()
# plt.grid(True)
# plt.tight_layout()
#
# # Show the plot
# plt.show()

import pandas as pd
import matplotlib.pyplot as plt

heating_oil_data = pd.read_csv('historical_data/HO=F.csv', skiprows=3, names=["Date", "Price"])
brent_oil_data = pd.read_csv('historical_data/BZ=F.csv', skiprows=3, names=["Date", "Price"])

for df in [heating_oil_data, brent_oil_data]:
    df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
    df["Price"] = pd.to_numeric(df["Price"], errors='coerce')
    df.dropna(inplace=True)

# Merge the data on Date
merged_data = pd.merge(heating_oil_data, brent_oil_data, on="Date", suffixes=('_HO', '_Brent'))

# Filter data for the 2014-2015 range
filtered_data = merged_data[(merged_data["Date"].dt.year >= 2014) & (merged_data["Date"].dt.year <= 2014)]

# Remove rows with zero or negative prices
filtered_data = filtered_data[(filtered_data["Price_HO"] > 0) & (filtered_data["Price_Brent"] > 0)]

# Calculate the price ratio
filtered_data["Price_Ratio"] = filtered_data["Price_Brent"] / filtered_data["Price_HO"]

# Calculate the 20-day moving average and standard deviation
filtered_data["Ratio_MA"] = filtered_data["Price_Ratio"].rolling(window=20).mean()
filtered_data["Ratio_SD"] = filtered_data["Price_Ratio"].rolling(window=20).std()

# Calculate the Bollinger Bands
filtered_data["Upper_Band"] = filtered_data["Ratio_MA"] + 2 * filtered_data["Ratio_SD"]
filtered_data["Lower_Band"] = filtered_data["Ratio_MA"] - 2 * filtered_data["Ratio_SD"]

# Debugging output
print(filtered_data[["Date", "Price_Ratio", "Ratio_MA", "Upper_Band", "Lower_Band"]].head())

# Plot the data
plt.figure(figsize=(12, 6))
plt.plot(filtered_data["Date"], filtered_data["Price_Ratio"], label="Price Ratio", color='blue')
plt.plot(filtered_data["Date"], filtered_data["Ratio_MA"], label="20-Day MA", color='green')
plt.plot(filtered_data["Date"], filtered_data["Upper_Band"], label="Upper Band", color='red')
plt.plot(filtered_data["Date"], filtered_data["Lower_Band"], label="Lower Band", color='red')

# Customize the plot
plt.title("Price Ratio Between Heating Oil Futures and Brent Oil Futures (2014)")
plt.xlabel("Date")
plt.ylabel("Price Ratio")
plt.legend()
plt.grid(True)
plt.tight_layout()

# Show the plot
plt.show()