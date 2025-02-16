
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
  const [newsData, setNewsData] = useState<Array<{
    source: string;
    title: string;
    imageUrl: string;
    time: string;
    authors?: string;
  }>>([]);

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

  const fetchNewsData = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/stock_news.json');
      const data = await response.json();
      
      // Flatten and process all news articles from all symbols
      const allArticles = Object.values(data).flat();
      
      // Transform articles to match NewsCard props format
      const processedNews = allArticles
        .filter(article => article.title && article.source_name) // Ensure required fields exist
        .map(article => ({
          source: article.source_name,
          title: article.title,
          imageUrl: article.image_url || '/lovable-uploads/5a40a2f1-0262-44c9-b69c-577df111c31c.png',
          time: getRelativeTime(article.pubDate),
          authors: article.creator ? (Array.isArray(article.creator) ? article.creator.join(', ') : article.creator) : undefined
        }))
        .slice(0, 6); // Get top 6 articles

      setNewsData(processedNews);
    } catch (error) {
      console.error('Error fetching news data:', error);
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
            <div className="grid gap-6 md:grid-cols-2">
              {newsData.map((news, index) => (
                <NewsCard key={index} {...news} />
              ))}
            </div>
          </section>
        </main>
      </div>
    </SidebarProvider>
  );
};

export default Index;
