
interface StockTickerProps {
  symbol: string;
  name: string;
  price: number;
  change: number;
}

export const StockTicker = ({ symbol, name, price, change }: StockTickerProps) => {
  const isNegative = change < 0;
  
  return (
    <div className="glass-card p-4 rounded-lg transition-all hover:scale-[1.02] cursor-pointer animate-slideIn">
      <div className="flex justify-between items-start mb-2">
        <div>
          <h3 className="font-semibold text-lg">{symbol}</h3>
          <p className="text-news-muted text-sm">{name}</p>
        </div>
        <div className="text-right">
          <p className="font-semibold">${price.toFixed(2)}</p>
          <p className={`text-sm ${isNegative ? 'text-news-negative' : 'text-green-500'}`}>
            {change > 0 ? '+' : ''}{change.toFixed(2)}%
          </p>
        </div>
      </div>
      <svg className="w-full h-12" viewBox="0 0 100 30">
        <path
          d="M0,15 L10,18 L20,12 L30,20 L40,15 L50,10 L60,18 L70,5 L80,15 L90,12 L100,15"
          className={`chart-line ${isNegative ? 'chart-line-negative' : ''}`}
        />
      </svg>
    </div>
  );
};
