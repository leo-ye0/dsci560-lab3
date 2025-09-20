import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input

def create_dataset(series, time_step=60):
    """Build sliding window dataset"""
    X, y = [], []
    for i in range(len(series) - time_step):
        X.append(series[i:(i + time_step), 0])
        y.append(series[i + time_step, 0])
    return np.array(X), np.array(y)

def build_lstm(time_step=60):
    """Build LSTM model"""
    model = Sequential([
        Input(shape=(time_step, 1)),
        LSTM(50, return_sequences=True),
        Dropout(0.2),
        LSTM(50, return_sequences=False),
        Dropout(0.2),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    return model

def train_lstm(data_path="data/processed_tech_stock_data.csv",
               time_step=60, epochs=20, batch_size=32):
    
    # Load data
    df = pd.read_csv(data_path)
    df['date'] = pd.to_datetime(df['date'])
    tickers = df['ticker'].unique()

    # Create dirs
    os.makedirs("../../data/lstm/models", exist_ok=True)

    model_info = []

    for ticker in tickers:
        try:
            print(f"\n Training LSTM for {ticker}...")
            
            # Get data
            data = df[df['ticker'] == ticker].copy()
            data = data[['date', 'close_price']].sort_values('date').reset_index(drop=True)
            scaler = MinMaxScaler(feature_range=(0, 1))
            scaled = scaler.fit_transform(data[['close_price']])

            X, y = create_dataset(scaled, time_step)
            X = X.reshape(X.shape[0], X.shape[1], 1)

            # Train/test split
            train_size = int(len(X) * 0.8)
            X_train, X_test = X[:train_size], X[train_size:]
            y_train, y_test = y[:train_size], y[train_size:]

            # Build & train model
            model = build_lstm(time_step)
            model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, verbose=0)

            # Save model only
            model_path = f"../../data/lstm/models/lstm_{ticker}.keras"
            model.save(model_path)

            # Save info
            model_info.append({
                "ticker": ticker,
                "train_size": len(X_train),
                "test_size": len(X_test),
                "model_path": model_path
            })

            print(f"✓ {ticker} model saved: {model_path}")

        except Exception as e:
            print(f"✗ {ticker}: Error - {e}")
            model_info.append({
                "ticker": ticker,
                "train_size": 0,
                "test_size": 0,
                "model_path": None
            })

    # Save summary
    info_df = pd.DataFrame(model_info)
    info_df.to_csv("../../data/lstm/lstm_trained_models_info.csv", index=False)

if __name__ == "__main__":
    train_lstm()
