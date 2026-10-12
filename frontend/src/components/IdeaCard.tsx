import React from 'react';
import type { CreativeItem, CreativeCard } from '../api/types';

interface IdeaCardProps {
  item: CreativeItem;
  card?: CreativeCard;
  onClick: (id: string) => void;
}

export const IdeaCard: React.FC<IdeaCardProps> = ({ item, card, onClick }) => {
  const categoryColor = {
    visual_design: 'bg-purple-100 text-purple-800',
    video_creative: 'bg-blue-100 text-blue-800',
    product_innovation: 'bg-green-100 text-green-800',
    ai_creative: 'bg-cyan-100 text-cyan-800',
    commercial: 'bg-pink-100 text-pink-800',
    wild_idea: 'bg-amber-100 text-amber-800',
  }[item.category] || 'bg-gray-100 text-gray-800';

  const formatDate = (dateStr: string) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString('zh-CN', { year: 'numeric', month: 'short', day: 'numeric' });
  };

  return (
    <div
      className="bg-white rounded-lg shadow-md overflow-hidden cursor-pointer hover:shadow-lg transition-shadow"
      onClick={() => onClick(item.id)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter') onClick(item.id);
      }}
    >
      {/* 图片区域 */}
      {item.thumbnail ? (
        <div className="relative h-48 overflow-hidden">
          <img
            src={item.thumbnail}
            alt={item.title}
            className="w-full h-full object-cover"
            loading="lazy"
          />
          <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/40 to-transparent p-2">
            <span className="text-white text-xs font-medium">{item.source}</span>
          </div>
        </div>
      ) : (
        <div className="h-48 bg-gray-200 flex items-center justify-center">
          <span className="text-gray-400 text-sm">暂无封面</span>
        </div>
      )}

      {/* 内容区域 */}
      <div className="p-4">
        <div className="flex justify-between items-start gap-2">
          <h3 className="font-semibold text-lg text-gray-900 line-clamp-2">
            {item.title || '无标题'}
          </h3>
          <span className={`text-xs font-medium px-2 py-1 rounded-full ${categoryColor}`}>
            {item.category || '未分类'}
          </span>
        </div>

        <p className="text-sm text-gray-600 mt-2 line-clamp-2">
          {item.description || '暂无描述'}
        </p>

        {/* 卡片详情（如果有 AI 分析） */}
        {card?.recommendation && (
          <div className="mt-3 pt-3 border-t border-gray-200">
            <p className="text-sm text-gray-700 line-clamp-2">{card.recommendation}</p>
          </div>
        )}

        {/* 发布时间 */}
        <div className="mt-2 text-xs text-gray-500">
          {formatDate(item.published_at)}
          {item.author && <span className="mx-1">·</span>}
          {item.author && <span>{item.author}</span>}
        </div>
      </div>
    </div>
  );
};

export default IdeaCard;
