import numpy as np
import pandas as pd

file_path = 'S&P 500 Monthly Returns.xlsx'
data = pd.ExcelFile(file_path)
df = data.parse("Sheet1")


df_cleaned = df[['Time Period', 'Return %']].copy()

df_cleaned.columns = ['Date', 'Return']

df_cleaned['Date'] = pd.to_datetime(df_cleaned['Date'], errors='coerce')
df_cleaned['Return'] = pd.to_numeric(df_cleaned['Return'], errors='coerce')


df_cleaned = df_cleaned.dropna()

filtered_data = df_cleaned[(df_cleaned['Date'] >= '2014-01-01') & (df_cleaned['Date'] <= '2024-11-01')]



filtered_data['Return'] = filtered_data['Return'] / 100


total_months = len(filtered_data)
annualized_return = (np.prod(1 + filtered_data['Return']) ** (12 / total_months)) - 1


start_value = 1
end_value = np.prod(1 + filtered_data['Return'])
years = total_months / 12
cagr = (end_value / start_value) ** (1 / years) - 1


std_dev = filtered_data['Return'].std() * np.sqrt(12)


risk_free_rate = 2.457872419 / 100
sharpe_ratio = (annualized_return - risk_free_rate) / std_dev


downside_returns = filtered_data['Return'][filtered_data['Return'] < 0]
downside_std_dev = downside_returns.std() * np.sqrt(12)
sortino_ratio = (annualized_return - risk_free_rate) / downside_std_dev


print({
    "Annualized Return": annualized_return,
    "CAGR": cagr,
    "Standard Deviation": std_dev,
    "Sharpe Ratio": sharpe_ratio,
    "Sortino Ratio": sortino_ratio
})
