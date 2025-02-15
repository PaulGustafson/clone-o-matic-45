
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd
from typing import List, Dict

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/stocks/{symbol}")
async def get_stock_data(symbol: str):
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        
        # Get historical data for the chart
        hist = stock.history(period="1d", interval="5m")
        
        return {
            "symbol": symbol,
            "name": info.get("longName", "Unknown"),
            "price": info.get("currentPrice", 0),
            "change": info.get("regularMarketChangePercent", 0),
            "chartData": hist["Close"].tolist()[-20:],  # Last 20 points for the chart
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/stocks")
async def get_multiple_stocks(symbols: str):
    symbols_list = symbols.split(",")
    results = []
    
    for symbol in symbols_list:
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            hist = stock.history(period="1d", interval="5m")
            
            results.append({
                "symbol": symbol,
                "name": info.get("longName", "Unknown"),
                "price": info.get("currentPrice", 0),
                "change": info.get("regularMarketChangePercent", 0),
                "chartData": hist["Close"].tolist()[-20:],
            })
        except:
            continue
            
    return results
