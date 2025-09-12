-- Database setup for stock portfolio management
CREATE DATABASE IF NOT EXISTS stock_portfolio;
USE stock_portfolio;

-- Drop existing tables to recreate with new schema
DROP TABLE IF EXISTS portfolio_stocks;
DROP TABLE IF EXISTS stock_data;
DROP TABLE IF EXISTS portfolios;
DROP TABLE IF EXISTS users;

-- Table for users
CREATE TABLE users (
    id VARCHAR(24) PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for portfolios
CREATE TABLE portfolios (
    id VARCHAR(24) PRIMARY KEY,
    user_id VARCHAR(24) NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_portfolio (user_id, name)
);

-- Table for stocks in portfolios
CREATE TABLE portfolio_stocks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    portfolio_id VARCHAR(24),
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