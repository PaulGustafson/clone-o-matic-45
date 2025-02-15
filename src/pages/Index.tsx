
import { SearchBar } from "@/components/SearchBar";
import { StockTicker } from "@/components/StockTicker";
import { NewsCard } from "@/components/NewsCard";
import { ArrowLeft } from "lucide-react";

const stockData = [
  { symbol: "IONQ", name: "IonQ, Inc.", price: 37.46, change: -3.08 },
  { symbol: "DRTS", name: "D-Wave Quantum Inc.", price: 6.37, change: -2.00 },
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
  return (
    <div className="min-h-screen bg-news-bg text-news-text p-6">
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

      <section className="mb-12">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">My Symbols</h2>
          <button className="text-news-accent hover:underline">See All</button>
        </div>
        <div className="grid gap-4 md:grid-cols-2">
          {stockData.map((stock) => (
            <StockTicker key={stock.symbol} {...stock} />
          ))}
        </div>
      </section>

      <section>
        <h2 className="text-3xl font-bold mb-6">Top Stories</h2>
        <div className="grid gap-6 md:grid-cols-2">
          {newsData.map((news, index) => (
            <NewsCard key={index} {...news} />
          ))}
        </div>
      </section>
    </div>
  );
};

export default Index;
