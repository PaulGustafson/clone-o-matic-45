
interface StockTickerProps {
  symbol: string;
  name: string;
  price: number;
  change: number;
  chartData?: number[];
}

export const StockTicker = ({ symbol, name, price, change, chartData = [] }: StockTickerProps) => {
  const isNegative = change < 0;
  
  // Calculate chart path based on real data
  const getChartPath = () => {
    if (!chartData.length) {
      return "M0,15 L10,18 L20,12 L30,20 L40,15 L50,10 L60,18 L70,5 L80,15 L90,12 L100,15";
    }

    const height = 30;
    const width = 100;
    const max = Math.max(...chartData);
    const min = Math.min(...chartData);
    const range = max - min;
    
    return chartData.map((point, i) => {
      const x = (i / (chartData.length - 1)) * width;
      const y = height - ((point - min) / range) * height;
      return `${i === 0 ? 'M' : 'L'}${x},${y}`;
    }).join(' ');
  };

  return (
    <div className="glass-card p-3 rounded-lg transition-all hover:scale-[1.02] cursor-pointer animate-slideIn">
      <div className="flex justify-between items-start gap-4">
        <div className="min-w-0 flex-1">
          <h3 className="font-semibold truncate">{symbol}</h3>
          <p className="text-news-muted text-sm truncate">{name}</p>
        </div>
        <div className="text-right flex-shrink-0">
          <p className="font-semibold">${price?.toFixed(2) || '0.00'}</p>
          <p className={`text-sm ${isNegative ? 'text-news-negative' : 'text-green-500'}`}>
            {change > 0 ? '+' : ''}{change?.toFixed(2) || '0.00'}%
          </p>
        </div>
      </div>
      <svg className="w-full h-8 mt-1" viewBox="0 0 100 30">
        <path
          d={getChartPath()}
          className={`chart-line ${isNegative ? 'chart-line-negative' : ''}`}
        />
      </svg>
    </div>
  );
};
