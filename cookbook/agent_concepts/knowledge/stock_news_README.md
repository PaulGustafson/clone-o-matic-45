# Stock News Agent

This example demonstrates how to create an Agno agent that can index and search stock market news articles.

## Features

- Indexes news articles with their metadata (stock symbol, title, link, etc.)
- Supports semantic search across news content
- Includes associated questions for each article
- Provides market analysis and insights

## Setup

1. Make sure you have PgVector running:
```shell
./cookbook/scripts/run_pgvector.sh
```

2. Install required packages:
```shell
pip install -U pgvector "psycopg[binary]" sqlalchemy openai agno
```

3. Run the stock news agent:
```shell
python cookbook/agent_concepts/knowledge/stock_news_agent.py
```

## Example Queries

- "What's the latest news about AAPL?"
- "Find news about AI companies"
- "What are the market implications of recent NVIDIA news?"
- "Show me news about tech companies and their financial performance"

The agent will search through the indexed news articles and provide relevant information along with analysis and insights. 