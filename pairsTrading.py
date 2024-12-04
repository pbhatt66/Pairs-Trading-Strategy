import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.ticker import MultipleLocator
from scipy.stats import skew
import statsmodels.api as sm

pairs = [
    ('BRK-B', 'MSFT'),
    ('CPAY', 'PKG'),
    ('PPG', 'SNA'),
    ('MMC', 'WAB'),
    ('ECL', 'TYL'),
    ('ACGL', 'CB'),
    ('XLV', 'SCHD'),
    ('BZ=F', 'HO=F'),
    ('POOL', 'V'),
    ('ECL', 'MMC')
]

total_initial_capital = 1000000.00
pairs_capital = total_initial_capital * 0.65
etf_capital = total_initial_capital * 0.35

pair_allocation = pairs_capital / len(pairs)
portfolio = pd.DataFrame()

def backtest_pair(ticker1, ticker2, start_date, end_date, allocated_capital, window=20):
    data = yf.download([ticker1, ticker2], start=start_date, end=end_date)['Adj Close'].dropna()
    data['Price_Ratio'] = data[ticker1] / data[ticker2]

    data['Ratio_MA'] = data['Price_Ratio'].rolling(window=window).mean()
    data['Ratio_SD'] = data['Price_Ratio'].rolling(window=window).std()
    data['Upper_Band'] = data['Ratio_MA'] + 2 * data['Ratio_SD']
    data['Lower_Band'] = data['Ratio_MA'] - 2 * data['Ratio_SD']

    data['Position'] = 0
    for i in range(window, len(data)):
        if data['Price_Ratio'].iloc[i] > data['Upper_Band'].iloc[i]:
            data.at[data.index[i], 'Position'] = -1  # Short ticker1, Long ticker2
        elif data['Price_Ratio'].iloc[i] < data['Lower_Band'].iloc[i]:
            data.at[data.index[i], 'Position'] = 1  # Long ticker1, Short ticker2
        elif abs(data['Price_Ratio'].iloc[i] - data['Ratio_MA'].iloc[i]) < .01:
            data.at[data.index[i], 'Position'] = 0
        else:
            data.at[data.index[i], 'Position'] = data['Position'].iloc[i - 1]

    data['Ticker1_Return'] = data[ticker1].pct_change()
    data['Ticker2_Return'] = data[ticker2].pct_change()
    data['Strategy_Return'] = data['Position'].shift(1) * (data['Ticker1_Return'] - data['Ticker2_Return'])

    data['Portfolio_Value'] = allocated_capital * (1 + data['Strategy_Return']).cumprod()

    return data['Portfolio_Value']

start_date = '2014-01-01'
end_date = '2024-11-01'

for ticker1, ticker2 in pairs:
    portfolio[f'{ticker1}-{ticker2}'] = backtest_pair(ticker1, ticker2, start_date, end_date, pair_allocation)

etf_ticker = 'SCHD'
etf_data = yf.download(etf_ticker, start=start_date, end=end_date)['Adj Close']
etf_returns = etf_data.pct_change().dropna()
etf_cumulative_returns = (1 + etf_returns).cumprod()
etf_portfolio_value = etf_capital * etf_cumulative_returns
etf_portfolio_value = etf_portfolio_value.squeeze()

portfolio['Total_Portfolio_Value'] = portfolio.sum(axis=1) + etf_portfolio_value

portfolio['Daily_Return'] = portfolio['Total_Portfolio_Value'].pct_change()
portfolio['Daily_Return'].replace([np.inf, -np.inf], np.nan, inplace=True)
portfolio.dropna(subset=['Daily_Return'], inplace=True)

monthly_returns = portfolio['Daily_Return'].resample('M').apply(lambda x: (1 + x).prod() - 1)
monthly_returns.to_csv('monthly_returns_1.csv', header=['Monthly_Return'])

def calculate_cagr(portfolio_value, start_date, end_date):
    years = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days / 365.25
    return (portfolio_value.iloc[-1] / portfolio_value.iloc[0]) ** (1 / years) - 1

def calculate_sortino_ratio(returns, risk_free_rate=0.02):
    downside_returns = returns[returns < 0]  # Only negative returns
    downside_deviation = np.std(downside_returns) * np.sqrt(252)
    return (returns.mean() * 252 - risk_free_rate) / downside_deviation

def calculate_sharpe_ratio(returns, risk_free_rate=0.02):
    return (returns.mean() * 252 - risk_free_rate) / (returns.std() * np.sqrt(252))

# portfolio_cagr = calculate_cagr(portfolio['Total_Portfolio_Value'], start_date, end_date)
# portfolio_annualized_volatility = portfolio['Daily_Return'].std() * np.sqrt(252)
# portfolio_sharpe_ratio = calculate_sharpe_ratio(portfolio['Daily_Return'])
# portfolio_sortino_ratio = calculate_sortino_ratio(portfolio['Daily_Return'])
# portfolio_skew = skew(portfolio['Daily_Return'])


# sp500_data = yf.download('^GSPC', start=start_date, end=end_date)['Adj Close']
# sp500_returns = sp500_data.pct_change().dropna()
# sp500_cumulative_returns = (1 + sp500_returns).cumprod()
# sp500_portfolio_value = total_initial_capital * sp500_cumulative_returns


# portfolio_cumulative_returns = (1 + portfolio['Daily_Return']).cumprod()
# rolling_max = portfolio_cumulative_returns.cummax()
# drawdown = (portfolio_cumulative_returns - rolling_max) / rolling_max
# max_drawdown = drawdown.min()

# print("Portfolio Performance:")
# print(f"  Annualized Return: {portfolio['Daily_Return'].mean() * 252:.2%}")
# print(f"  CAGR: {portfolio_cagr:.2%}")
# print(f"  Standard Deviation: {portfolio_annualized_volatility:.2%}")
# print(f"  Sharpe Ratio: {portfolio_sharpe_ratio:.2f}")
# print(f"  Sortino Ratio: {portfolio_sortino_ratio:.2f}")
# print(f"  Skew: {portfolio_skew:.2f}")
# print(f"  Max Drawdown: {max_drawdown.min():.2%}")



# plt.figure(figsize=(14, 7))
# plt.plot(portfolio.index, portfolio['Total_Portfolio_Value'], label='Portfolio Value from Pairs Trades', color='#6495ED', linewidth=2)
# plt.plot(sp500_portfolio_value.index, sp500_portfolio_value, label='S&P 500 Portfolio', color='#848884', linewidth=2)
# plt.title('Pairs Trading Strategy vs. S&P 500')
# plt.xlabel('Year')
# plt.ylabel('Portfolio Value ($)')
# plt.legend(loc='upper left')
# plt.grid()
#
# plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
# plt.show()