import json
import os
from pathlib import Path
from typing import Dict, List

from agno.agent import Agent
from agno.knowledge.base import KnowledgeBase
from agno.models.together import TogetherChat
from agno.embedder.together import TogetherEmbedder
from agno.vectordb.pgvector import PgVector
from rich.prompt import Prompt

# Set Together API key

class StockNewsKnowledge(KnowledgeBase):
    def __init__(self, vector_db: PgVector, news_file: str):
        super().__init__(vector_db)
        self.news_file = news_file

    def load_documents(self) -> List[Dict]:
        """Load stock news articles from JSON file"""
        with open(self.news_file, 'r', encoding='utf-8') as f:
            news_data = json.load(f)

        documents = []
        # Process each stock's news articles
        for stock, articles in news_data.items():
            for article in articles:
                # Create a document for each article with metadata
                doc = {
                    "content": f"Title: {article['title']}\n\nDescription: {article.get('description', '')}\n\nStock: {stock}",
                    "metadata": {
                        "stock": stock,
                        "title": article["title"],
                        "link": article.get("link", ""),
                        "questions": article.get("questions", []),
                        "published_date": article.get("pubDate", "")
                    }
                }
                documents.append(doc)
        
        return documents

def main():
    # Initialize vector database with TogetherEmbedder
    vector_db = PgVector(
        table_name="stock_news",
        db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
        embedder=TogetherEmbedder()  # Use TogetherAI embedder
    )

    # Initialize knowledge base
    news_file = Path(__file__).parent.parent.parent.parent / "api" / "stock_news.json"
    knowledge_base = StockNewsKnowledge(
        vector_db=vector_db,
        news_file=str(news_file)
    )

    # Check if data needs to be loaded
    if not vector_db.exists() or Prompt.ask(
        "[bold yellow]Do you want to reload the news data?[/bold yellow]", 
        choices=["y", "n"], 
        default="n"
    ) == "y":
        print("[bold blue]Loading news data into vector database...[/bold blue]")
        knowledge_base.load(recreate=True)
        print("[bold green]Data loaded successfully![/bold green]")

    # Create the agent with TogetherChat
    agent = Agent(
        model=TogetherChat(id="mistralai/Mixtral-8x7B-Instruct-v0.1"),  # Use Mixtral model
        knowledge=knowledge_base,
        search_knowledge=True,
        description="You are a stock market news analyst. You help users find and analyze relevant stock market news.",
        instructions=[
            "Always cite the source of news articles when discussing them",
            "When analyzing news, consider potential market implications",
            "Include relevant questions from the articles in your analysis"
        ],
        show_tool_calls=True,
        markdown=True
    )

    print("\n[bold green]Stock News Agent is ready! Ask questions about stock news or type 'exit' to quit.[/bold green]\n")

    # Interactive chat loop
    while True:
        message = Prompt.ask("[bold]Ask about stock news[/bold]")
        if message.lower() in ("exit", "quit", "bye"):
            break
        agent.print_response(message, stream=True)

if __name__ == "__main__":
    main() 