import yfinance as yf
import pandas as pd
from statsmodels.tsa.stattools import adfuller, coint

def fetch_sp500_data(start_date, end_date):
    sp500_tickers = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]['Symbol'].tolist()
    data = yf.download(sp500_tickers, start=start_date, end=end_date)['Adj Close'].dropna(axis=1)
    return data

def calculate_correlations(data):
    correlation_matrix = data.corr()
    return correlation_matrix

def get_top_pairs(correlation_matrix, top_n=20):
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
    return p_value >= 0.05

def perform_cointegration_test(pair, data):
    ticker1, ticker2 = pair
    score, p_value, _ = coint(data[ticker1], data[ticker2])
    return p_value < 0.05

def find_best_pairs(data, top_pairs):
    best_pairs = []
    for ticker1, ticker2, corr in top_pairs:
        if is_non_stationary(data[ticker1]) and is_non_stationary(data[ticker2]):
            if perform_cointegration_test((ticker1, ticker2), data):
                best_pairs.append((ticker1, ticker2, corr))
        if len(best_pairs) >= 20:
            break
    return best_pairs

if __name__ == "__main__":
    start_date = '2011-01-01'
    end_date = '2014-01-01'

    sp500_data = fetch_sp500_data(start_date, end_date)
    correlation_matrix = calculate_correlations(sp500_data)

    top_correlated_pairs = get_top_pairs(correlation_matrix, top_n=20)
    best_pairs = find_best_pairs(sp500_data, top_correlated_pairs)

    print("\nTop 10 Pairs for Pairs Trading:")
    for ticker1, ticker2, corr in best_pairs:
        print(f"Pair: {ticker1}-{ticker2}, Correlation: {corr:.2f}")
