import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def run_lstm_backtest():
    df = pd.read_csv('data/processed_tech_stock_data.csv')
    df['date'] = pd.to_datetime(df['date'])
    tickers = df['ticker'].unique()
    print(f"Processing {len(tickers)} tickers...")

    # Initialize
    capital = 100000
    positions = {}
    portfolio_values = []
    trade_count = 0

    # Train/test split
    all_dates = sorted(df['date'].unique())
    train_size = int(len(all_dates) * 0.8)
    dates = all_dates[train_size:]
    total_dates = len(dates)
    print(f"Backtesting over {total_dates} trading days...")

    # Load prediction CSVs
    pred_results = {}
    info = pd.read_csv("../../data/lstm/lstm_trained_models_info.csv")
    for _, row in info.iterrows():
        ticker = row['ticker']
        csv_path = row['csv_path']
        if os.path.exists(csv_path):
            pred_df = pd.read_csv(csv_path)
            pred_df['date'] = pd.to_datetime(pred_df['date'])
            pred_results[ticker] = pred_df
        else:
            pred_results[ticker] = None

    # Backtest loop
    for i, date in enumerate(dates):
        day_data = df[df['date'] == date]
        current_prices = {}
        for ticker in tickers:
            ticker_data = day_data[day_data['ticker'] == ticker]
            if not ticker_data.empty:
                price = ticker_data['adj_close_price'].iloc[0]
                current_prices[ticker] = price
                pred_df = pred_results.get(ticker)
                if pred_df is not None:
                    row = pred_df[pred_df['date'] == date]
                    idx = row.index.min()
                    if idx is not None and idx > 0:
                        pred_yesterday = pred_df.loc[idx-1, "predicted_price"]
                        avg_future_change = (pred_yesterday - price) / price
                    else:
                        avg_future_change = 0
                else:
                    avg_future_change = 0

                # Trend filter
                hist_prices = df[(df['ticker'] == ticker) & (df['date'] <= date)]['adj_close_price']
                if len(hist_prices) >= 6:
                    ma5_now = hist_prices.tail(5).mean()
                    ma5_prev = hist_prices.tail(6).head(5).mean()
                    ma_trend_up = ma5_now > ma5_prev
                else:
                    ma_trend_up = True

                # Buy logic (Dynamic Position Sizing)
                if avg_future_change > 0.01 and ma_trend_up and capital > price * 10:
                    if avg_future_change > 0.03:
                        invest_ratio = 0.2  # strong signal
                    else:
                        invest_ratio = 0.1  # normal signal

                    invest_amount = capital * invest_ratio
                    shares = int(invest_amount // price)

                    if shares > 0:
                        capital -= shares * price
                        if ticker in positions:
                            # Update average entry price
                            old_shares = positions[ticker]["shares"]
                            old_entry = positions[ticker]["entry_price"]
                            new_total_shares = old_shares + shares
                            new_entry_price = (old_shares * old_entry + shares * price) / new_total_shares
                            positions[ticker] = {"shares": new_total_shares, "entry_price": new_entry_price}
                        else:
                            positions[ticker] = {"shares": shares, "entry_price": price}

                        trade_count += 1
                        print(f"{date.date()} BUY {shares} {ticker} at {price:.2f}")

                # Sell logic (Partial Sell)
                if ticker in positions and positions[ticker]["shares"] > 0:
                    entry_price = positions[ticker]["entry_price"]
                    shares = positions[ticker]["shares"]
                    profit_pct = (price - entry_price) / entry_price

                    if avg_future_change < -0.01:
                        # Predicted drop → full sell
                        capital += shares * price
                        positions.pop(ticker)
                        trade_count += 1
                        print(f"{date.date()} FULL SELL {shares} {ticker} at {price:.2f}")
                    elif profit_pct > 0.1 or profit_pct < -0.05:
                        # Stop-loss or Take-profit → sell half
                        sell_shares = shares // 2 if shares // 2 > 0 else shares
                        capital += sell_shares * price
                        positions[ticker]["shares"] -= sell_shares
                        if positions[ticker]["shares"] == 0:
                            positions.pop(ticker)
                        trade_count += 1
                        print(f"{date.date()} PARTIAL SELL {sell_shares} {ticker} at {price:.2f} | Pct: {profit_pct:.2%}")

        # Portfolio value
        stock_value = sum(positions[t]["shares"] * current_prices.get(t, 0) for t in positions)
        portfolio_value = capital + stock_value
        portfolio_values.append(portfolio_value)

    # Metrics
    initial_value = 100000
    final_value = portfolio_values[-1]
    portfolio_df = pd.DataFrame({'date': dates, 'value': portfolio_values})
    portfolio_df['daily_return'] = portfolio_df['value'].pct_change()

    total_return = (final_value / initial_value - 1) * 100
    days = len(dates)
    annualized_return = ((final_value / initial_value) ** (365/days) - 1) * 100
    risk_free_rate = 0.02 / 252
    excess_returns = portfolio_df['daily_return'].dropna() - risk_free_rate
    sharpe_ratio = excess_returns.mean() / excess_returns.std() * np.sqrt(252)
    portfolio_df['cummax'] = portfolio_df['value'].cummax()
    portfolio_df['drawdown'] = (portfolio_df['value'] - portfolio_df['cummax']) / portfolio_df['cummax']
    max_drawdown = portfolio_df['drawdown'].min() * 100
    volatility = portfolio_df['daily_return'].std() * np.sqrt(252) * 100

    print("\n" + "="*50)
    print("COMBINED LSTM STRATEGY RESULTS")
    print("Indicators: LSTM Prediction + Trend Filter (MA5) + Dynamic Position Sizing + Partial Sell")
    print("="*50)
    print(f"Initial Capital: ${initial_value:,.2f}")
    print(f"Final Portfolio Value: ${final_value:,.2f}")
    print(f"Total Return: {total_return:.2f}%")
    print(f"Annualized Return: {annualized_return:.2f}%")
    print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
    print(f"Max Drawdown: {max_drawdown:.2f}%")
    print(f"Volatility: {volatility:.2f}%")
    print(f"Estimated Trades: {trade_count}")
    print(f"Trading Days: {days}")

    # Plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    ax1.plot(portfolio_df['date'], portfolio_df['value'], 'b-', linewidth=2)
    ax1.axhline(y=initial_value, color='r', linestyle='--', alpha=0.7, label='Initial Value')
    ax1.set_title('Portfolio Value Over Time (LSTM Strategy)')
    ax1.set_ylabel('Portfolio Value ($)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    ax2.fill_between(portfolio_df['date'], portfolio_df['drawdown'] * 100, 0,
                     color='red', alpha=0.3, label='Drawdown')
    ax2.set_title('Portfolio Drawdown')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Drawdown (%)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('data/lstm_portfolio_performance.png', dpi=300, bbox_inches='tight')
    plt.show()

    return final_value, total_return

if __name__ == "__main__":
    run_lstm_backtest()
