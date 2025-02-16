import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict
import json
from pathlib import Path

class StockNewsAPI:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('NEWSDATA_API_KEY')
        if not self.api_key:
            raise ValueError("NewsData API key is required. Set it as NEWSDATA_API_KEY environment variable or pass it to the constructor.")
        
        self.base_url = "https://newsdata.io/api/1/news"
        self.stocks = [
            "AAPL",  # Apple
            "MSFT",  # Microsoft
            "GOOGL", # Alphabet
            "AMZN",  # Amazon
            "NVDA",  # NVIDIA
            "META",  # Meta
            "TSLA",  # Tesla
            "JPM",   # JPMorgan Chase
            "BAC",   # Bank of America
            "WMT",   # Walmart
        ]

    def get_past_week_news(self) -> Dict[str, List[Dict]]:
        """
        Fetch news for the past week for all stocks in the list.
        Returns a dictionary with stock symbols as keys and lists of news articles as values.
        """
        all_news = {}
        
        for stock in self.stocks:
            try:
                params = {
                    'apikey': self.api_key,
                    'qInTitle': stock,  # Search in title
                    'category': 'business',  # Focus on business news
                    'language': 'en',
                    'country': 'us'  # Focus on US news
                }
                
                response = requests.get(self.base_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                if data.get('status') == 'success':
                    # Filter results to only include those mentioning the stock
                    filtered_results = [
                        article for article in data.get('results', [])
                        if stock.lower() in article.get('title', '').lower() or
                           stock.lower() in article.get('description', '').lower()
                    ]
                    all_news[stock] = filtered_results
                    print(f"Successfully fetched {len(all_news[stock])} news items for {stock}")
                else:
                    print(f"Failed to fetch news for {stock}: {data.get('message', 'Unknown error')}")
                    all_news[stock] = []
                    
            except Exception as e:
                print(f"Error fetching news for {stock}: {str(e)}")
                all_news[stock] = []
            
            # Add a small delay to avoid rate limiting
            if stock != self.stocks[-1]:  # Don't delay after the last request
                import time
                time.sleep(1)
        
        return all_news

    def save_to_file(self, data: Dict[str, List[Dict]], filename: str = "stock_news.json"):
        """Save the fetched news data to a JSON file"""
        output_path = Path(__file__).parent / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"News data saved to {output_path}")

def main():
    # Initialize the API (make sure to set NEWSDATA_API_KEY environment variable)
    api = StockNewsAPI()
    
    # Fetch news for all stocks
    news_data = api.get_past_week_news()
    
    # Save to file
    api.save_to_file(news_data)

if __name__ == "__main__":
    main() 