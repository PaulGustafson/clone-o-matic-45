
import { useState, useEffect } from "react";
import { SearchBar } from "@/components/SearchBar";
import { StockTicker } from "@/components/StockTicker";
import { NewsCard } from "@/components/NewsCard";
import { ArrowLeft, Plus, X } from "lucide-react";
import {
  Sidebar,
  SidebarContent,
  SidebarProvider,
} from "@/components/ui/sidebar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import stockNewsData from "../../api/stock_news.json";

// Define the type for our news article
interface NewsArticle {
  source_name: string;
  title: string;
  description: string;
  pubDate: string;
  questions: string[];  // Add questions field to interface
}

const initialSymbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA", "META"];

// Convert API timestamp to relative time
const getRelativeTime = (timestamp: string) => {
  const now = new Date();
  const articleDate = new Date(timestamp);
  const diff = now.getTime() - articleDate.getTime();
  const hours = Math.floor(diff / (1000 * 60 * 60));
  
  return `${hours}h ago`;
};

const Index = () => {
  const [stocks, setStocks] = useState<Array<{
    symbol: string;
    name: string;
    price: number;
    change: number;
    chartData?: number[];
  }>>([]);
  const [newSymbol, setNewSymbol] = useState("");
  const [showAddForm, setShowAddForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [newsData, setNewsData] = useState<Record<string, Array<{
    source: string;
    title: string;
    summary: string;
    time: string;
    questions: string[];
  }>>>({});

  const fetchStockData = async (symbols: string[]) => {
    try {
      const response = await fetch(`http://localhost:8000/api/stocks?symbols=${symbols.join(',')}`);
      const data = await response.json();
      if (Array.isArray(data)) {
        setStocks(data);
      } else {
        console.error('Invalid data format received:', data);
        setStocks([]);
      }
      setLoading(false);
    } catch (error) {
      console.error('Error fetching stock data:', error);
      setStocks([]);
      setLoading(false);
    }
  };

  const fetchNewsData = () => {
    try {
      // Process news data by stock symbol
      const processedNewsBySymbol: Record<string, any[]> = {};
      
      // Process each stock's news articles
      Object.entries(stockNewsData).forEach(([symbol, articles]) => {
        if (Array.isArray(articles)) {
          processedNewsBySymbol[symbol] = articles
            .filter(article => article.title && article.source_name)
            .map(article => ({
              source: article.source_name,
              title: article.title,
              summary: article.description || "No summary available",
              time: getRelativeTime(article.pubDate),
              questions: article.questions || [] // Use questions from JSON data
            }))
            .slice(0, 3); // Limit to top 3 articles per symbol
        }
      });

      setNewsData(processedNewsBySymbol);
    } catch (error) {
      console.error('Error processing news data:', error);
    }
  };

  useEffect(() => {
    fetchStockData(initialSymbols);
    fetchNewsData();
    // Refresh stock data every minute
    const interval = setInterval(() => {
      fetchStockData(initialSymbols);
    }, 60000);

    return () => clearInterval(interval);
  }, []);

  const handleAddSymbol = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSymbol) return;

    try {
      const response = await fetch(`http://localhost:8000/api/stocks/${newSymbol}`);
      const data = await response.json();
      if (!data.error) {
        setStocks(prevStocks => [data, ...prevStocks]);
      }
    } catch (error) {
      console.error('Error adding symbol:', error);
    }

    setNewSymbol("");
    setShowAddForm(false);
  };

  const handleDeleteSymbol = (symbolToDelete: string) => {
    setStocks(prevStocks => prevStocks.filter(stock => stock.symbol !== symbolToDelete));
  };

  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full">
        <Sidebar className="border-r border-white/10">
          <SidebarContent>
            <div className="px-4 py-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold">My Symbols</h2>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setShowAddForm(!showAddForm)}
                  className="hover:bg-news-card/50"
                >
                  <Plus className="h-5 w-5" />
                </Button>
              </div>

              {showAddForm && (
                <form onSubmit={handleAddSymbol} className="mb-4 flex gap-2">
                  <Input
                    value={newSymbol}
                    onChange={(e) => setNewSymbol(e.target.value)}
                    placeholder="Enter symbol"
                    className="bg-news-card/50 border-white/10 text-news-text placeholder:text-news-muted"
                  />
                  <Button type="submit" variant="secondary">Add</Button>
                </form>
              )}

              <div className="space-y-4">
                {loading ? (
                  <div className="text-center text-news-muted">Loading...</div>
                ) : (
                  stocks.map((stock) => (
                    <div key={stock.symbol} className="relative group">
                      <StockTicker {...stock} />
                      <button
                        onClick={() => handleDeleteSymbol(stock.symbol)}
                        className="absolute top-2 right-2 p-1 rounded-full bg-news-card opacity-0 group-hover:opacity-100 hover:bg-red-500/20 transition-all"
                      >
                        <X className="h-4 w-4 text-news-negative" />
                      </button>
                    </div>
                  ))
                )}
              </div>
            </div>
          </SidebarContent>
        </Sidebar>

        <main className="flex-1 p-6">
          <header className="mb-8">
            <div className="flex items-center gap-4 mb-6">
              <button className="p-2 hover:bg-news-card/50 rounded-full transition-colors">
                <ArrowLeft className="w-6 h-6" />
              </button>
              <SearchBar />
            </div>
            <div className="flex items-baseline justify-between mb-2">
              <h1 className="text-4xl font-bold">Stocks</h1>
              <span className="text-xl text-news-muted">
                {new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric' })}
              </span>
            </div>
          </header>

          <section>
            <h2 className="text-3xl font-bold mb-6">Top Stories</h2>
            <div className="space-y-12">
              {stocks.map((stock) => {
                const stockNews = newsData[stock.symbol];
                if (!stockNews || stockNews.length === 0) return null;

                return (
                  <div key={stock.symbol} className="space-y-4">
                    <h3 className="text-2xl font-semibold text-news-accent">{stock.symbol}</h3>
                    <div className="grid gap-6 md:grid-cols-2">
                      {stockNews.map((news, index) => (
                        <NewsCard key={index} {...news} />
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          </section>
        </main>
      </div>
    </SidebarProvider>
  );
};

export default Index;
