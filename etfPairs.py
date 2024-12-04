import yfinance as yf
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller, coint


def fetch_etf_data(start_date, end_date):
    etfs = {
        'SPY': 'SPY',  # S&P 500 ETF
        'QQQ': 'QQQ',  # Nasdaq-100 ETF
        'DIA': 'DIA',  # Dow Jones Industrial Average ETF
        'IWM': 'IWM',  # Russell 2000 ETF
        'EFA': 'EFA',  # MSCI EAFE ETF
        'EEM': 'EEM',  # MSCI Emerging Markets ETF
        'TLT': 'TLT',  # 20+ Year Treasury Bond ETF
        'HYG': 'HYG',  # High Yield Corporate Bond ETF
        'LQD': 'LQD',  # Investment Grade Corporate Bond ETF
        'GLD': 'GLD',  # Gold ETF
        'SLV': 'SLV',  # Silver ETF
        'USO': 'USO',  # Crude Oil ETF
        'UNG': 'UNG',  # Natural Gas ETF
        'XLE': 'XLE',  # Energy Select Sector SPDR Fund
        'XLK': 'XLK',  # Technology Select Sector SPDR Fund
        'XLF': 'XLF',  # Financial Select Sector SPDR Fund
        'XLU': 'XLU',  # Utilities Select Sector SPDR Fund
        'XLY': 'XLY',  # Consumer Discretionary Select Sector SPDR Fund
        'XLP': 'XLP',  # Consumer Staples Select Sector SPDR Fund
        'VNQ': 'VNQ',  # Real Estate ETF
        'ARKK': 'ARKK',  # ARK Innovation ETF
        'XLV': 'XLV',  # Health Care Select Sector SPDR Fund
        'XBI': 'XBI',  # S&P Biotech ETF
        'SMH': 'SMH',  # VanEck Semiconductor ETF
        'IBB': 'IBB',  # Nasdaq Biotechnology ETF
        'KRE': 'KRE',  # Regional Bank ETF
        'GDX': 'GDX',  # Gold Miners ETF
        'SOXX': 'SOXX',  # iShares Semiconductor ETF
        'SCHD': 'SCHD',  # Schwab Dividend Equity ETF
        'VTI': 'VTI',  # Vanguard Total Stock Market ETF
        'VEU': 'VEU',  # Vanguard FTSE All-World ex-US ETF
        'VOO': 'VOO',  # Vanguard S&P 500 ETF
        'BND': 'BND',  # Vanguard Total Bond Market ETF
        'VGK': 'VGK',  # Vanguard FTSE Europe ETF
        'VT': 'VT',  # Vanguard Total World Stock ETF
        'SHY': 'SHY',  # iShares 1-3 Year Treasury Bond ETF
        'IEF': 'IEF',  # iShares 7-10 Year Treasury Bond ETF
        'TIP': 'TIP',  # iShares TIPS Bond ETF
        'FXI': 'FXI',  # China Large-Cap ETF
        'EWZ': 'EWZ',  # iShares MSCI Brazil ETF
        'EWT': 'EWT',  # iShares MSCI Taiwan ETF
        'EWH': 'EWH',  # iShares MSCI Hong Kong ETF
        'VWO': 'VWO',  # Vanguard FTSE Emerging Markets ETF
    }

    valid_etfs = {}
    for name, ticker in etfs.items():
        try:
            data = yf.download(ticker, start=start_date, end=end_date)['Adj Close']
            if not data.empty:
                valid_etfs[name] = data
        except Exception as e:
            print(f"Failed to fetch data for {name} ({ticker}): {e}")

    if valid_etfs:
        combined_data = pd.concat(valid_etfs.values(), axis=1)
        combined_data.columns = valid_etfs.keys()
        combined_data.dropna(inplace=True)
        return combined_data
    else:
        raise ValueError("No valid ETF data found.")


def calculate_correlations(data):
    correlation_matrix = data.corr()
    return correlation_matrix


def get_top_pairs(correlation_matrix, top_n=10):
    pairs = []
    for i in range(len(correlation_matrix.columns)):
        for j in range(i + 1, len(correlation_matrix.columns)):
            corr_value = correlation_matrix.iloc[i, j]
            pairs.append((correlation_matrix.columns[i], correlation_matrix.columns[j], corr_value))

    sorted_pairs = sorted(pairs, key=lambda x: abs(x[2]), reverse=True)
    return sorted_pairs[:top_n]


def is_non_stationary(series):
    adf_result = adfuller(series)
    p_value = adf_result[1]
    return p_value >= 0.05  # Non-stationary if p-value >= 0.05


def perform_cointegration_test(pair, data):
    ticker1, ticker2 = pair
    score, p_value, _ = coint(data[ticker1], data[ticker2])
    return p_value < 0.07  # Cointegrated if p-value < 0.05


def find_best_pairs(data, top_pairs):
    best_pairs = []
    for ticker1, ticker2, corr in top_pairs:
        # Ensure both series are non-stationary
        if is_non_stationary(data[ticker1]) and is_non_stationary(data[ticker2]):
            # Perform cointegration test
            if perform_cointegration_test((ticker1, ticker2), data):
                best_pairs.append((ticker1, ticker2, corr))
        if len(best_pairs) >= 10:  # Stop when we have 5 pairs
            break
    return best_pairs


if __name__ == "__main__":

    start_date = '2014-01-01'
    end_date = '2024-01-01'

    print("Fetching ETF data...")
    etf_data = fetch_etf_data(start_date, end_date)

    print("Calculating correlations for ETFs...")
    correlation_matrix = calculate_correlations(etf_data)

    plt.figure(figsize=(12, 8))
    sns.heatmap(correlation_matrix, cmap="coolwarm", annot=True, fmt=".2f")
    plt.title("Correlation Heatmap of Major ETFs")
    plt.show()

    print("Selecting top correlated ETF pairs...")
    top_correlated_pairs = get_top_pairs(correlation_matrix, top_n=10)

    print("Finding best ETF pairs based on stationarity and cointegration...")
    best_pairs = find_best_pairs(etf_data, top_correlated_pairs)

    print("\nTop 5 Pairs for ETF Pairs Trading:")
    for ticker1, ticker2, corr in best_pairs:
        print(f"Pair: {ticker1}-{ticker2}, Correlation: {corr:.2f}")
