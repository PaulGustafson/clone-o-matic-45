
interface NewsCardProps {
  source: string;
  title: string;
  imageUrl: string;
  time: string;
  authors?: string;
}

export const NewsCard = ({ source, title, imageUrl, time, authors }: NewsCardProps) => {
  return (
    <div className="glass-card rounded-lg overflow-hidden transition-all hover:scale-[1.01] cursor-pointer animate-fadeIn">
      <img
        src={imageUrl}
        alt={title}
        className="w-full h-48 object-cover"
        loading="lazy"
      />
      <div className="p-4">
        <div className="flex items-center gap-2 mb-2">
          <span className="text-sm font-medium text-news-accent">{source}</span>
          <span className="text-xs text-news-muted">{time}</span>
        </div>
        <h2 className="text-xl font-semibold mb-2 line-clamp-2">{title}</h2>
        {authors && (
          <p className="text-sm text-news-muted truncate">{authors}</p>
        )}
      </div>
    </div>
  );
};
