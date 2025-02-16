
interface NewsCardProps {
  source: string;
  title: string;
  summary: string;
  time: string;
  questions: string[];
}

export const NewsCard = ({ source, title, summary, time, questions }: NewsCardProps) => {
  return (
    <div className="glass-card rounded-lg overflow-hidden transition-all hover:scale-[1.01] cursor-pointer animate-fadeIn p-4">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-sm font-medium text-news-accent">{source}</span>
        <span className="text-xs text-news-muted">{time}</span>
      </div>
      <h2 className="text-xl font-semibold mb-3 line-clamp-2">{title}</h2>
      <p className="text-sm text-news-text mb-4 line-clamp-3">{summary}</p>
      <div className="space-y-2">
        {questions.map((question, index) => (
          <p key={index} className="text-sm text-news-accent italic">
            {question}
          </p>
        ))}
      </div>
    </div>
  );
};
