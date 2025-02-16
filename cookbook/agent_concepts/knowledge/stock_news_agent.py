import json
import os
from pathlib import Path
from typing import Dict, List, Union, Optional

from agno.agent import Agent
from agno.knowledge.base import KnowledgeBase
from agno.models.together import TogetherChat
from agno.embedder.together import TogetherEmbedder
from agno.vectordb.pgvector import PgVector
from rich.prompt import Prompt
from rich.console import Console
from rich import print

console = Console()

class StockNewsKnowledge(KnowledgeBase):
    def __init__(self, vector_dbs: List[PgVector], news_files: List[str]):
        """
        Initialize with multiple vector databases and news files.
        
        Args:
            vector_dbs: List of PgVector instances, one for each news file
            news_files: List of paths to news JSON files
        """
        # Initialize with the first vector db, but keep track of all
        super().__init__(vector_dbs[0])
        self.vector_dbs = vector_dbs
        self.news_files = news_files
        
        if len(vector_dbs) != len(news_files):
            raise ValueError("Number of vector databases must match number of news files")

    def load_documents(self, file_index: int = 0) -> List[Dict]:
        """
        Load stock news articles from a specific JSON file
        
        Args:
            file_index: Index of the news file to load
        """
        with open(self.news_files[file_index], 'r', encoding='utf-8') as f:
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
                        "published_date": article.get("pubDate", ""),
                        "source_file": Path(self.news_files[file_index]).stem  # Add source file info
                    }
                }
                documents.append(doc)
        
        return documents

    def load_all(self, recreate: bool = False) -> None:
        """Load all news files into their respective vector databases"""
        for i, vector_db in enumerate(self.vector_dbs):
            console.print(f"[bold blue]Loading news data from {self.news_files[i]} into {vector_db.table_name}...[/bold blue]")
            # Set current vector db for parent class methods
            self._vector_db = vector_db
            documents = self.load_documents(i)
            if recreate:
                vector_db.recreate()
            vector_db.add_documents(documents)
            console.print(f"[bold green]Loaded {len(documents)} documents into {vector_db.table_name}[/bold green]")

    def search(self, query: str, **kwargs) -> List[Dict]:
        """Search across all vector databases and combine results"""
        all_results = []
        for vector_db in self.vector_dbs:
            # Set current vector db for search
            self._vector_db = vector_db
            results = super().search(query, **kwargs)
            all_results.extend(results)
        
        # Sort combined results by relevance score
        all_results.sort(key=lambda x: x.get('score', 0), reverse=True)
        return all_results[:kwargs.get('limit', 5)]  # Return top N results

def get_table_name(file_path: str) -> str:
    """Generate a valid table name from a file path"""
    return f"stock_news_{Path(file_path).stem.lower().replace('-', '_')}"

def main():
    # List of news files to process
    base_path = Path(__file__).parent.parent.parent.parent
    news_files = [
        str(base_path / "download_data" / "data" / file)
        for file in os.listdir(base_path / "download_data" / "data")
        if file.endswith('.json')
    ]
    print(news_files)

    # Initialize vector databases with TogetherEmbedder
    embedder = TogetherEmbedder()
    vector_dbs = [
        PgVector(
            table_name=get_table_name(file),
            db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
            embedder=embedder
        )
        for file in news_files
    ]

    # Initialize knowledge base
    knowledge_base = StockNewsKnowledge(
        vector_dbs=vector_dbs,
        news_files=news_files
    )

    # Check if data needs to be loaded
    should_reload = False
    for vector_db in vector_dbs:
        if not vector_db.exists():
            should_reload = True
            break
    
    if should_reload or Prompt.ask(
        "[bold yellow]Do you want to reload the news data?[/bold yellow]", 
        choices=["y", "n"], 
        default="n"
    ) == "y":
        console.print("[bold blue]Loading news data into vector databases...[/bold blue]")
        knowledge_base.load_all(recreate=True)
        console.print("[bold green]All data loaded successfully![/bold green]")

    # Create the agent with TogetherChat
    agent = Agent(
        model=TogetherChat(id="mistralai/Mixtral-8x7B-Instruct-v0.1"),
        knowledge=knowledge_base,
        search_knowledge=True,
        description="You are a stock market news analyst. You help users find and analyze relevant stock market news.",
        instructions=[
            "Always cite the source of news articles when discussing them",
            "When analyzing news, consider potential market implications",
            "Include relevant questions from the articles in your analysis",
            "Mention which news source/file the information comes from"
        ],
        show_tool_calls=True,
        markdown=True
    )

    console.print("\n[bold green]Stock News Agent is ready! Ask questions about stock news or type 'exit' to quit.[/bold green]\n")

    # Interactive chat loop
    while True:
        message = Prompt.ask("[bold]Ask about stock news[/bold]")
        if message.lower() in ("exit", "quit", "bye"):
            break
        agent.print_response(message, stream=True)

if __name__ == "__main__":
    main() 