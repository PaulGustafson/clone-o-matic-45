import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict
import json
from pathlib import Path
import google.generativeai as genai
import time

class StockNewsAPI:
    def __init__(self, api_key: str = None, gemini_key: str = None):
        self.api_key = api_key or os.getenv('NEWSDATA_API_KEY')
        if not self.api_key:
            raise ValueError("NewsData API key is required. Set it as NEWSDATA_API_KEY environment variable or pass it to the constructor.")
        
        # Initialize Gemini
        genai.configure(api_key=gemini_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
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

    def generate_questions(self, article: Dict) -> List[str]:
        """Generate insightful questions about a news article using Gemini."""
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                prompt = f"""
                Based on this news article:
                Title: {article['title']}
                Description: {article.get('description', '')}
                
                Generate 3 insightful, analytical questions that an investor might ask about the implications of this news.
                Return only a Python list of strings, with each question being a complete sentence ending with a question mark.
                Focus on market impact, business strategy, and future implications.
                Example format: ["Question 1?", "Question 2?", "Question 3?"]
                """
                
                response = self.model.generate_content(prompt)
                response_text = response.text.strip()
                # Remove any markdown code block indicators
                response_text = response_text.replace('```python', '').replace('```', '')
                # Safely evaluate the string as a Python list
                try:
                    questions = eval(response_text)
                    if isinstance(questions, list) and len(questions) >= 3:
                        return questions[:3]
                except:
                    # If eval fails, try to extract questions using string manipulation
                    questions = [q.strip() for q in response_text.split('?') if q.strip()]
                    questions = [f"{q}?" for q in questions]
                    if questions:
                        return questions[:3]
                
                # If we get here, use default questions
                raise ValueError("Could not parse questions from response")
                
            except Exception as e:
                print(f"Error generating questions (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if "429" in str(e):  # Rate limit error
                    time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                    continue
                
                if attempt == max_retries - 1:  # Last attempt
                    return [
                        "What are the potential market implications of this news?",
                        "How might this affect the company's competitive position?",
                        "What could be the long-term impact on the industry?"
                    ]
            
            time.sleep(1)  # Small delay between successful calls

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
                    
                    # Generate questions for each article
                    for article in filtered_results:
                        article['questions'] = self.generate_questions(article)
                        time.sleep(1)  # Add delay between article processing
                    
                    all_news[stock] = filtered_results
                    print(f"Successfully fetched and analyzed {len(all_news[stock])} news items for {stock}")
                else:
                    print(f"Failed to fetch news for {stock}: {data.get('message', 'Unknown error')}")
                    all_news[stock] = []
                    
            except Exception as e:
                print(f"Error fetching news for {stock}: {str(e)}")
                all_news[stock] = []
            
            # Add a small delay to avoid rate limiting
            if stock != self.stocks[-1]:  # Don't delay after the last request
                time.sleep(2)
        
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