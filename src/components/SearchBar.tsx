
import { Search } from "lucide-react";

export const SearchBar = () => {
  return (
    <div className="relative w-full max-w-md animate-fadeIn">
      <input
        type="text"
        placeholder="Search"
        className="w-full px-4 py-2 pl-10 bg-news-card/50 rounded-lg border border-white/10 text-news-text placeholder:text-news-muted focus:outline-none focus:ring-2 focus:ring-news-accent/50 transition-all"
      />
      <Search className="absolute left-3 top-2.5 w-5 h-5 text-news-muted" />
    </div>
  );
};
