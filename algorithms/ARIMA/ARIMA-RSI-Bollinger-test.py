import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
from multiprocessing import Pool, cpu_count


def run_backtest():
    """Simple ARIMA backtest"""
    print("Running ARIMA backtest...")
    
    # Load data
    df = pd.read_csv('../../data/processed_tech_stock_data.csv')
    df['date'] = pd.to_datetime(df['date'])
    tickers = df['ticker'].unique()
    print(f"Processing {len(tickers)} tickers...")
    
    # Initialize
    capital = 100000
    positions = {}
    portfolio_values = []
    trade_count = 0  # Track actual trades
    
    # Get test period dates only (last 20% of data)
    all_dates = sorted(df['date'].unique())
    train_size = int(len(all_dates) * 0.8)
    dates = all_dates[train_size:]
    total_dates = len(dates)
    print(f"Backtesting over {total_dates} trading days...")
    
    # Pre-load all models for faster access
    models = {}
    for ticker in tickers:
        try:
            with open(f'../../data/arima/models/{ticker}_arima_model.pkl', 'rb') as f:
                models[ticker] = pickle.load(f)
        except:
            models[ticker] = None
    
    # Buy initial positions on first day
    first_date = dates[0]
    first_day_data = df[df['date'] == first_date]
    for ticker in tickers:
        ticker_data = first_day_data[first_day_data['ticker'] == ticker]
        if not ticker_data.empty:
            price = ticker_data['adj_close_price'].iloc[0]
            shares = int(capital * 0.03 / price)  # 3% allocation per stock
            if shares > 0 and capital > shares * price:
                capital -= shares * price
                positions[ticker] = shares
                print(f"Initial BUY {shares} shares of {ticker} at ${price:.2f}")
    
    print(f"Remaining cash after initial purchases: ${capital:,.2f}")
    
    # Process dates in batches for better performance
    batch_size = 10
    for i in range(0, len(dates), batch_size):
        batch_dates = dates[i:i+batch_size]
        
        # Show progress every 100 days
        if i % 100 == 0:
            progress = (i / total_dates) * 100
            print(f"Progress: {progress:.1f}% ({i}/{total_dates} days)")
        
        for date in batch_dates:
            day_data = df[df['date'] == date]
            current_prices = {}
            
            # Process each ticker
            for ticker in tickers:
                ticker_data = day_data[day_data['ticker'] == ticker]
                if not ticker_data.empty:
                    price = ticker_data['adj_close_price'].iloc[0]
                    current_prices[ticker] = price
                    
                    # Get historical data up to training cutoff (models only trained on 80% of data)
                    train_cutoff_date = all_dates[train_size-1]
                    hist_data = df[(df['ticker'] == ticker) & (df['date'] <= train_cutoff_date)]
                    if len(hist_data) > 50 and models.get(ticker):
                        # Combined 3-Indicator Strategy
                        signals = []
                        
                        # 1. ARIMA Signal
                        try:
                            if models.get(ticker):
                                forecast = models[ticker].forecast(steps=1).iloc[0]
                                change_pct = forecast / price
                                if change_pct > 0.0001:
                                    signals.append('BUY')
                                elif change_pct < -0.0001:
                                    signals.append('SELL')
                                else:
                                    signals.append('HOLD')
                            else:
                                signals.append('HOLD')
                        except:
                            signals.append('HOLD')
                        
                        # 2. Bollinger Bands Signal
                        if len(hist_data) >= 20:
                            prices = hist_data['adj_close_price'].tail(20)
                            bb_mean = prices.mean()
                            bb_std = prices.std()
                            bb_upper = bb_mean + (2 * bb_std)
                            bb_lower = bb_mean - (2 * bb_std)
                            
                            if price <= bb_lower:
                                signals.append('BUY')
                            elif price >= bb_upper:
                                signals.append('SELL')
                            else:
                                signals.append('HOLD')
                        
                        # 3. RSI Signal
                        if len(hist_data) >= 14:
                            price_changes = hist_data['adj_close_price'].pct_change().tail(14)
                            gains = price_changes[price_changes > 0]
                            losses = -price_changes[price_changes < 0]
                            
                            avg_gain = gains.mean() if len(gains) > 0 else 0
                            avg_loss = losses.mean() if len(losses) > 0 else 0
                            
                            if avg_loss > 0:
                                rs = avg_gain / avg_loss
                                rsi = 100 - (100 / (1 + rs))
                                
                                if rsi < 30:  # Oversold
                                    signals.append('BUY')
                                elif rsi > 70:  # Overbought
                                    signals.append('SELL')
                                else:
                                    signals.append('HOLD')
                            else:
                                signals.append('HOLD')
                        
                        # More aggressive trading logic
                        buy_votes = signals.count('BUY')
                        sell_votes = signals.count('SELL')
                        
                        # Trade if any indicator gives signal and no opposing signals
                        if buy_votes > 0 and sell_votes == 0:
                            signal = 'BUY'
                        elif sell_votes > 0 and buy_votes == 0:
                            signal = 'SELL'
                        elif buy_votes > sell_votes:
                            signal = 'BUY'
                        elif sell_votes > buy_votes:
                            signal = 'SELL'
                        else:
                            signal = 'HOLD'
                        
                        
                        if signal == 'BUY':
                            # If no cash, sell worst performing stock to buy this one
                            if capital < price * 10:
                                # Find worst performing stock to sell
                                worst_ticker = None
                                worst_return = float('inf')
                                for t in positions:
                                    if positions[t] > 0 and t != ticker:
                                        current_t_price = current_prices.get(t, 0)
                                        if current_t_price > 0:
                                            # Simple return calculation
                                            perf = current_t_price / price  # Rough performance
                                            if perf < worst_return:
                                                worst_return = perf
                                                worst_ticker = t
                                
                                # Sell worst performer
                                if worst_ticker and positions.get(worst_ticker, 0) > 0:
                                    sell_shares = positions[worst_ticker]
                                    sell_price = current_prices.get(worst_ticker, 0)
                                    capital += sell_shares * sell_price
                                    positions[worst_ticker] = 0
                                    print(f"SELL {sell_shares} shares of {worst_ticker} at ${sell_price:.2f} (to buy {ticker})")
                                    trade_count += 1
                            
                            # Now buy the target stock
                            if capital > price * 10:
                                shares = int(capital * 0.1 / price)  # Use 10% of capital
                                if shares > 0:
                                    capital -= shares * price
                                    positions[ticker] = positions.get(ticker, 0) + shares
                                    print(f"BUY {shares} shares of {ticker} at ${price:.2f}")
                                    trade_count += 1
                        
                        elif signal == 'SELL' and positions.get(ticker, 0) > 0:
                            # Sell half the position
                            shares = positions[ticker] // 2
                            if shares > 0:
                                capital += shares * price
                                positions[ticker] -= shares
                                print(f"SELL {shares} shares of {ticker} at ${price:.2f}")
                                trade_count += 1
            
            # Calculate portfolio value
            stock_value = sum(positions.get(t, 0) * current_prices.get(t, 0) for t in tickers)
            portfolio_value = capital + stock_value
            portfolio_values.append(portfolio_value)
    
    # Calculate comprehensive metrics
    initial_value = 100000
    final_value = portfolio_values[-1]
    
    # Convert to DataFrame for calculations
    portfolio_df = pd.DataFrame({'value': portfolio_values, 'date': dates})
    portfolio_df['daily_return'] = portfolio_df['value'].pct_change()
    
    # Calculate metrics
    total_return = (final_value / initial_value - 1) * 100
    days = len(dates)
    annualized_return = ((final_value / initial_value) ** (365/days) - 1) * 100
    
    # Sharpe ratio
    risk_free_rate = 0.02 / 252
    excess_returns = portfolio_df['daily_return'].dropna() - risk_free_rate
    sharpe_ratio = excess_returns.mean() / excess_returns.std() * np.sqrt(252)
    
    # Max drawdown
    portfolio_df['cummax'] = portfolio_df['value'].cummax()
    portfolio_df['drawdown'] = (portfolio_df['value'] - portfolio_df['cummax']) / portfolio_df['cummax']
    max_drawdown = portfolio_df['drawdown'].min() * 100
    
    # Volatility
    volatility = portfolio_df['daily_return'].std() * np.sqrt(252) * 100
    
    # Actual trade count
    total_trades = trade_count + len([t for t in tickers if positions.get(t, 0) > 0])  # +initial buys
    
    print(f"\n{'='*50}")
    print("COMBINED 3-INDICATOR STRATEGY RESULTS")
    print("Indicators: ARIMA + Bollinger Bands + RSI")
    print(f"{'='*50}")
    print(f"Initial Capital: ${initial_value:,.2f}")
    print(f"Final Portfolio Value: ${final_value:,.2f}")
    print(f"Total Return: {total_return:.2f}%")
    print(f"Annualized Return: {annualized_return:.2f}%")
    print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
    print(f"Max Drawdown: {max_drawdown:.2f}%")
    print(f"Volatility: {volatility:.2f}%")
    print(f"Estimated Trades: {total_trades}")
    print(f"Trading Days: {days}")
    
    # Create plots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Portfolio value over time
    ax1.plot(portfolio_df['date'], portfolio_df['value'], 'b-', linewidth=2)
    ax1.axhline(y=initial_value, color='r', linestyle='--', alpha=0.7, label='Initial Value')
    ax1.set_title('Portfolio Value Over Time')
    ax1.set_ylabel('Portfolio Value ($)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Drawdown chart
    ax2.fill_between(portfolio_df['date'], portfolio_df['drawdown'] * 100, 0, 
                     color='red', alpha=0.3, label='Drawdown')
    ax2.set_title('Portfolio Drawdown')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Drawdown (%)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('../../data/plots/arima_portfolio_performance.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"\nPlot saved: data/plots/arima_portfolio_performance.png")
    
    return final_value, total_return

if __name__ == "__main__":
    run_backtest()