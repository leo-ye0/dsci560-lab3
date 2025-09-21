import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def ma_50(train):
    price = np.mean(train.adj_close_price)
    return price

def buy(capital, price):
    return capital - price

def sell(capital, price):
    return capital + price

def train_moving_avg(path):
    df = pd.read_csv(path)
    print('Moving Average Algorithm\n')
    
    tickers = df.ticker.unique()
    capital = initial_capital / len(tickers)
    stock_dict = {ticker:[] for ticker in tickers}

    for ticker in tickers:
        print(f'Simulate stock trading for {ticker}')
        stock_count = 0
        current_capital, prev_capital = capital, capital
        ticker_df = df[df['ticker'] == ticker].reset_index(drop=True)
        train = ticker_df.iloc[:len(ticker_df) - 50].reset_index(drop=True)
        test = ticker_df.iloc[50:].reset_index(drop=True)
        prev_buy = 0

        for i in train.index:
            date = ticker_df.iloc[i].date
            sma = ma_50(train[i:i + 49])
            current_price = test.iloc[i].adj_close_price
            if i == train.index[-1]:
                sold = current_price * stock_count
                stock_count = 0
                current_capital += sold
            else:

                if (current_price <= sma) and (current_capital >= 0.95 * capital):
                    stock_count += 1
                    prev_buy = current_price
                    current_capital = buy(current_capital, sma)
                elif prev_buy < current_price:
                    if stock_count >= 1:
                        stock_count -= 1
                        current_capital = sell(current_capital, sma)
                
                draw_down = min(0, (current_capital - prev_capital) / current_capital * 100)        
                stock_dict[ticker].append([date, float(round(current_capital, 2)), float(round(draw_down, 2))])
                prev_capital = current_capital
            
        print(f'Starting capital: {capital}')
        print(f'Capital after simulation: {current_capital}')
        print(f'Amount of stock hold: {stock_count}')

        if current_capital > capital:
            print(f'Net profit: {current_capital - capital}\n')
        else: 
            print(f'Net loss: {current_capital - capital}\n')
    return stock_dict

def plot_graph(df):
    print('Start plotting...')
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    ax1.plot(df['Date'], df['Capital'], 'b-', linewidth=2)
    ax1.axhline(y=initial_capital, color='r', linestyle='--', alpha=0.7, label='Initial Value')
    ax1.set_title('Portfolio Value Over Time')
    ax1.set_ylabel('Portfolio Value ($)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_major_locator(mdates.YearLocator())  
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    ax2.fill_between(df['Date'], df['Drawdown'] * 100, 0, 
                     color='red', alpha=0.3, label='Drawdown')
    ax2.set_title('Portfolio Drawdown')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Drawdown (%)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.xaxis.set_major_locator(mdates.YearLocator())
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    
    plt.tight_layout()
    plt.savefig('../../data/plots/ma_portfolio_performance.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f'Plot saved: data/plots/ma_portfolio_performance.png')

if __name__ == '__main__':
    path = '../../data/processed_tech_stock_data.csv'
    initial_capital = 100000
    stock_dict = train_moving_avg(path)
    dfs = [pd.DataFrame(stock_dict[ticker], columns=['Date', 'Capital', 'Drawdown']) for ticker in stock_dict.keys()]

    combined = pd.concat(dfs, ignore_index=True)
    df = combined.groupby('Date', as_index=False).sum()
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    plot_graph(df)