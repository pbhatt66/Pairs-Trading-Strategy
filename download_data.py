import yfinance as yf
import os
import pandas as pd

# List of symbols to download
# symbols = [
#     '^GSPC', 'BRK-B', 'MSFT', 'CMS', 'DTE', 'NEE', 'SRE', 'CPAY', 'PKG',
#     'GILD', 'PPG', 'SNA', 'MMC', 'WAB', 'ECL', 'TYL', 'ACGL', 'CB',
#     'XLV', 'SCHD', 'BZ=F', 'HO=F', 'CL=F', 'ZC=F', 'ZW=F', 'ZS=F', 'POOL', 'V'
# ]
symbols = [
    'BZ=F', 'HO=F',
]

# Date range for historical data
start_date = '2014-01-01'
end_date = '2024-11-01'

# Directory to save the CSV files
output_dir = 'historical_data'
os.makedirs(output_dir, exist_ok=True)  # Create directory if it doesn't exist

# Fetch and save data
for symbol in symbols:
    try:
        print(f"Downloading data for {symbol}...")
        # Download data
        data = yf.download(symbol, start=start_date, end=end_date)

        if not data.empty:
            # Ensure the 'Adj Close' column is present
            if 'Adj Close' in data.columns:
                data = data[['Adj Close']]  # Keep only the 'Adj Close' column
            else:
                print(f"'Adj Close' not found for {symbol}, skipping.")
                continue

            # Clean up the index to ensure proper date format
            data.index.name = 'Date'

            # Save to CSV
            csv_path = os.path.join(output_dir, f"{symbol}.csv")
            data.to_csv(csv_path)
            print(f"Data for {symbol} saved to {csv_path}")
        else:
            print(f"No data found for {symbol}.")
    except Exception as e:
        print(f"Error downloading data for {symbol}: {e}")

print("\nDownload complete!")

