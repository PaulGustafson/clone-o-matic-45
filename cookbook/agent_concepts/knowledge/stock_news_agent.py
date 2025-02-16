import json
import os
from pathlib import Path
from typing import Dict, List, Union, Optional
from hashlib import md5

from agno.agent import Agent
from agno.knowledge.agent import AgentKnowledge as KnowledgeBase
from agno.models.google import Gemini
from agno.embedder.together import TogetherEmbedder
from agno.vectordb.pgvector import PgVector
from agno.document import Document
from rich.prompt import Prompt
from rich.console import Console
from rich import print

console = Console()

class StockNewsKnowledge(KnowledgeBase):
    vector_dbs: List[PgVector]  # Define as class field
    news_files: List[str]  # Define as class field

    def __init__(self, vector_dbs: List[PgVector], news_files: List[str]):
        """
        Initialize with multiple vector databases and news files.
        
        Args:
            vector_dbs: List of PgVector instances, one for each news file
            news_files: List of paths to news JSON files
        """
        if len(vector_dbs) != len(news_files):
            raise ValueError("Number of vector databases must match number of news files")

        # Initialize all fields at once
        super().__init__(
            vector_db=vector_dbs[0],
            vector_dbs=vector_dbs,
            news_files=news_files
        )

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
            if not isinstance(articles, list):
                console.print(f"[yellow]Warning: Invalid format for stock {stock}, skipping...[/yellow]")
                continue
                
            for article in articles:
                if not isinstance(article, dict):
                    console.print(f"[yellow]Warning: Invalid article format for stock {stock}, skipping...[/yellow]")
                    continue
                    
                # Create a document for each article with metadata
                try:
                    doc = {
                        "content": f"Title: {article.get('title', 'No Title')}\n\nDescription: {article.get('description', '')}\n\nStock: {stock}",
                        "metadata": {
                            "stock": stock,
                            "title": article.get("title", "No Title"),
                            "link": article.get("link", ""),
                            "questions": article.get("questions", []),
                            "published_date": article.get("pubDate", ""),
                            "source_file": Path(self.news_files[file_index]).stem  # Add source file info
                        }
                    }
                    documents.append(doc)
                except Exception as e:
                    console.print(f"[red]Error processing article for stock {stock}: {e}[/red]")
                    continue
        
        return documents

    def load_all(self, recreate: bool = False) -> None:
        """Load all news files into their respective vector databases"""
        for i, vector_db in enumerate(self.vector_dbs):
            console.print(f"[bold blue]Loading news data from {self.news_files[i]} into {vector_db.table_name}...[/bold blue]")
            # Set current vector db for parent class methods
            self._vector_db = vector_db
            documents = self.load_documents(i)
            if recreate:
                vector_db.create()
            
            # Convert documents to Document objects with all required fields
            doc_objects = []
            for idx, doc in enumerate(documents):
                try:
                    # Create a unique ID using file index, document index, and content hash
                    content_hash = md5(doc["content"].encode()).hexdigest()
                    doc_id = f"{i}_{idx}_{content_hash[:8]}"
                    # Create a name from the title in metadata or use a fallback
                    doc_name = doc["metadata"].get("title", f"Document_{doc_id}")
                    
                    # Get embedding for the document
                    embedding = vector_db.embedder.get_embedding(doc["content"])
                    
                    # Create document with all required fields
                    doc_obj = Document(
                        id=doc_id,
                        name=doc_name,
                        content=doc["content"],
                        meta_data=doc["metadata"],
                        embedder=vector_db.embedder,
                        embedding=embedding  # Use pre-computed embedding
                    )
                    doc_objects.append(doc_obj)
                except Exception as e:
                    console.print(f"[red]Error creating document {idx}: {str(e)}[/red]")
                    continue
            
            if doc_objects:  # Only attempt insert if we have valid documents
                try:
                    vector_db.insert(doc_objects)
                    console.print(f"[bold green]Loaded {len(doc_objects)} documents into {vector_db.table_name}[/bold green]")
                except Exception as e:
                    console.print(f"[red]Error inserting documents into {vector_db.table_name}: {str(e)}[/red]")
            else:
                console.print(f"[yellow]No valid documents to insert into {vector_db.table_name}[/yellow]")

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

def get_summary_and_follow_up_questions(prompt: str) -> Tuple[str, List[str]]:

def generate_answer(self, article: Dict, prompt: str) -> List[str]:
        """Generate insightful questions about a news article using Gemini."""
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                prompt = f"""
                Based on this news article:
                Title: {article['title']}
                Description: {article.get('description', '')}

                and this
                
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


def main():
    # List of news files to process
    base_path = Path(__file__).parent.parent.parent.parent
    news_files = [
        str(base_path / "download_data" / "data" / file)
        for file in os.listdir(base_path / "download_data" / "data")
        if file.endswith('.json')
    ]
    news_files = news_files[:3]  #FIXME

    # Get Together API key
    together_api_key = os.getenv("TOGETHER_API_KEY")
    if not together_api_key:
        together_api_key = Prompt.ask(
            "[bold yellow]Please enter your Together API key[/bold yellow]",
            password=True
        )
        os.environ["TOGETHER_API_KEY"] = together_api_key

    # Get Gemini API key
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        gemini_api_key = Prompt.ask(
            "[bold yellow]Please enter your Google API key[/bold yellow]",
            password=True
        )
        os.environ["GEMINI_API_KEY"] = gemini_api_key

    # Initialize vector databases with TogetherEmbedder
    embedder = TogetherEmbedder(api_key=together_api_key)
    vector_dbs = [
        PgVector(
            table_name=get_table_name(file),
            db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
            embedder=embedder
        )
        for file in news_files
    ]
    
    print('News files:', news_files)

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
    else:
        knowledge_base.load_all(recreate=False)



    # Create the agent with Gemini model
    gemini_model = Gemini(api_key=gemini_api_key)
    gemini_model.id = "gemini-1.5-flash"  # Set model ID after initialization
    agent = Agent(
        model=gemini_model,
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
    #get_new_articles("What is the news about Meta?")
    main() 