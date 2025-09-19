import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
import pickle
import os
import warnings
warnings.filterwarnings('ignore')

def train_and_save_arima_models():
    """Train ARIMA models for all tickers and save them"""
    print("Training ARIMA models for all tickers...")
    
    # Load data
    df = pd.read_csv('../../data/processed_tech_stock_data.csv')
    tickers = df['ticker'].unique()
    
    # Create models directory
    os.makedirs('../../data/arima/models', exist_ok=True)
    model_info = []
    
    for ticker in tickers:
        print(f"Training ARIMA model for {ticker}...")
        try:
            # Get ticker data
            ticker_data = df[df['ticker'] == ticker].copy()
            ticker_data['date'] = pd.to_datetime(ticker_data['date'])
            ticker_data = ticker_data.sort_values('date')
            
            # Set datetime index with business day frequency
            ticker_data = ticker_data.set_index('date')
            ticker_data.index.freq = 'B'  # Business day frequency
            train_size = int(len(ticker_data) * 0.8)
            
            # Use log transformation for better stationarity
            log_prices = np.log(ticker_data['adj_close_price'])
            train_data = log_prices[:train_size]
            
            # Check stationarity
            adf_result = adfuller(train_data.dropna())
            is_stationary = adf_result[1] < 0.05
            print(f"{ticker}: Stationary = {is_stationary} (p-value: {adf_result[1]:.4f})")
            
            # If not stationary, difference the data
            if not is_stationary:
                train_data = train_data.diff().dropna()
            
            best_order = find_best_arima_order(train_data)
            model = ARIMA(train_data, order=best_order)
            fitted_model = model.fit()
            
            model_path = f'../../data/arima/models/{ticker}_arima_model.pkl'
            with open(model_path, 'wb') as f:
                pickle.dump(fitted_model, f)
            
            # Save model info
            model_info.append({
                'ticker': ticker,
                'order': best_order,
                'aic': fitted_model.aic,
                'train_size': len(train_data),
                'model_path': model_path
            })
            print(f"✓ {ticker}: ARIMA{best_order}, AIC: {fitted_model.aic:.2f}")
            
        except Exception as e:
            print(f"✗ {ticker}: Error - {e}")
            model_info.append({
                'ticker': ticker,
                'order': None,
                'aic': None,
                'train_size': 0,
                'model_path': None
            })
    
    # Save model info
    model_df = pd.DataFrame(model_info)
    model_df.to_csv('../../data/arima/trained_models_info.csv', index=False)
    print(f"\n✓ Trained {len([m for m in model_info if m['order'] is not None])} ARIMA models")
    print("Models saved in data/arima/models/")
    return model_df

def find_best_arima_order(data):
    """Find best ARIMA order using manual search with log-transformed data"""
    best_aic = float('inf')
    best_order = (1, 1, 1)
    
    # Test common ARIMA configurations
    orders_to_test = [(1,1,1), (1,1,0), (0,1,1), (2,1,1), (1,1,2), (2,1,2), (1,0,1), (2,0,1)]
    
    for order in orders_to_test:
        try:
            model = ARIMA(data, order=order)
            fitted = model.fit(method_kwargs={'warn_convergence': False})
            if fitted.aic < best_aic:
                best_aic = fitted.aic
                best_order = order
        except:
            continue
    
    return best_order

def load_trained_model(ticker):
    """Load pre-trained ARIMA model"""
    model_path = f'../../data/arima/models/{ticker}_arima_model.pkl'
    try:
        with open(model_path, 'rb') as f:
            return pickle.load(f)
    except:
        return None

if __name__ == "__main__":
    train_and_save_arima_models()