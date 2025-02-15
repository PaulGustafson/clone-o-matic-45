
import { useState } from "react";
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

const initialStockData = [
  { symbol: "IONQ", name: "IonQ, Inc.", price: 37.46, change: -3.08 },
  { symbol: "DRTS", name: "D-Wave Quantum Inc.", price: 6.37, change: -2.00 },
  { symbol: "TLT", name: "iShares 20+ Year Treas...", price: 89.15, change: 0.53 },
  { symbol: "TSLA", name: "Tesla, Inc.", price: 355.84, change: -0.03 },
  { symbol: "NVDA", name: "NVIDIA Corporation", price: 138.85, change: 2.63 },
  { symbol: "SPY", name: "SPDR S&P 500 ETF Trust", price: 609.70, change: -0.00 },
  { symbol: "^VIX", name: "CBOE Volatility Index", price: 14.77, change: -2.19 },
];

const newsData = [
  {
    source: "cheddar",
    title: "The biggest business stories of the week",
    imageUrl: "/lovable-uploads/5a40a2f1-0262-44c9-b69c-577df111c31c.png",
    time: "4h ago",
  },
  {
    source: "POLITICO",
    title: "\"Like a tornado hit\": Stunned federal workers take stock of mass layoffs — and brace for repercussions",
    imageUrl: "/lovable-uploads/5a40a2f1-0262-44c9-b69c-577df111c31c.png",
    time: "4h ago",
    authors: "Liz Crampton, Marcia Brown, Danny Ngu...",
  },
];

const Index = () => {
  const [stocks, setStocks] = useState(initialStockData);
  const [newSymbol, setNewSymbol] = useState("");
  const [showAddForm, setShowAddForm] = useState(false);

  const handleAddSymbol = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSymbol) return;

    // In a real app, you would fetch the company details from an API
    const mockNewStock = {
      symbol: newSymbol.toUpperCase(),
      name: `${newSymbol.toUpperCase()} Company`,
      price: Math.random() * 1000,
      change: (Math.random() * 10) * (Math.random() > 0.5 ? 1 : -1),
    };

    setStocks([mockNewStock, ...stocks]);
    setNewSymbol("");
    setShowAddForm(false);
  };

  const handleDeleteSymbol = (symbolToDelete: string) => {
    setStocks(stocks.filter(stock => stock.symbol !== symbolToDelete));
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
                {stocks.map((stock) => (
                  <div key={stock.symbol} className="relative group">
                    <StockTicker {...stock} />
                    <button
                      onClick={() => handleDeleteSymbol(stock.symbol)}
                      className="absolute top-2 right-2 p-1 rounded-full bg-news-card opacity-0 group-hover:opacity-100 hover:bg-red-500/20 transition-all"
                    >
                      <X className="h-4 w-4 text-news-negative" />
                    </button>
                  </div>
                ))}
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
              <span className="text-xl text-news-muted">February 15</span>
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
