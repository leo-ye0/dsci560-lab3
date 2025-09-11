-- Database setup for stock portfolio management
CREATE DATABASE IF NOT EXISTS stock_portfolio;
USE stock_portfolio;

-- Table for portfolios
CREATE TABLE portfolios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for stocks in portfolios
CREATE TABLE portfolio_stocks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    portfolio_id INT,
    stock_symbol VARCHAR(10) NOT NULL,
    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id) ON DELETE CASCADE,
    UNIQUE KEY unique_portfolio_stock (portfolio_id, stock_symbol)
);

-- Table for stock price data
CREATE TABLE stock_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stock_symbol VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    open_price DECIMAL(10,2),
    high_price DECIMAL(10,2),
    low_price DECIMAL(10,2),
    close_price DECIMAL(10,2),
    volume BIGINT,
    UNIQUE KEY unique_stock_date (stock_symbol, date)
);