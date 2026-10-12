import React, { useState, useEffect } from 'react';
import { api, type CreativeItem, type CreativeCard } from '../api/client';
import { IdeaCard } from '../components/IdeaCard';

const CATEGORY_MAP = {
  visual_design: '视觉设计',
  video_creative: '视频创意',
  product_innovation: '产品创意',
  ai_creative: 'AI 创意',
  commercial: '商业创意',
  wild_idea: '脑洞创意',
} as const;

export const Home: React.FC = () => {
  const [items, setItems] = useState<CreativeItem[]>([]);
  const [cards, setCards] = useState<{ [key: string]: CreativeCard }>({});
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedTag, setSelectedTag] = useState<string>('all');

  useEffect(() => {
    loadToday();
  }, []);

  const loadToday = async () => {
    try {
      const todayItems = await api.getToday();
      setItems(todayItems);

      // 并行加载卡片
      const cardPromises = todayItems.map(async (item) => {
        try {
          const card = await api.getCard(item.id);
          return { [item.id]: card };
        } catch {
          return {};
        }
      });

      const cardResults = await Promise.all(cardPromises);
      const mergedCards: { [key: string]: CreativeCard } = {};
      cardResults.forEach((cardsMap) => {
        Object.assign(mergedCards, cardsMap);
      });
      setCards(mergedCards);
    } catch (error) {
      console.error('加载今日精选失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const tags = Array.from(new Set(items.flatMap((item) => item.tags))).filter(Boolean);

  const filteredItems = selectedCategory === 'all'
    ? items
    : items.filter((item) => item.category === selectedCategory);

  const filteredByTag = selectedTag === 'all'
    ? filteredItems
    : filteredItems.filter((item) => item.tags.includes(selectedTag));

  return (
    <div>
      {/* 标题 */}
      <header className="text-center py-8">
        <h1 className="text-3xl font-bold text-gray-900">Creative Radar</h1>
        <p className="text-gray-600 mt-2">每日发现值得模仿的创意</p>
        <p className="text-gray-500 text-sm">
          {new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })}
        </p>
      </header>

      {/* 今日精选 */}
      <section className="mt-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">🔥 今日精选</h2>

        {loading ? (
          <div className="text-center py-8 text-gray-500">加载中...</div>
        ) : filteredByTag.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            暂无内容，点击下方按钮刷新
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredByTag.map((item) => (
              <IdeaCard
                key={item.id}
                item={item}
                card={cards[item.id]}
                onClick={loadToday}
              />
            ))}
          </div>
        )}
      </section>

      {/* 分类筛选 */}
      <section className="mt-8">
        <h2 className="text-xl font-bold text-gray-900 mb-4">分类</h2>
        <div className="flex flex-wrap gap-2">
          <button
            className="px-3 py-1 rounded-full text-sm bg-gray-200 text-gray-700 hover:bg-gray-300 transition"
            onClick={() => setSelectedCategory('all')}
          >
            全部
          </button>
          {(Object.keys(CATEGORY_MAP) as Array<keyof typeof CATEGORY_MAP>).map((category) => (
            <button
              key={category}
              className={`px-3 py-1 rounded-full text-sm font-medium transition ${
                selectedCategory === category
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
              onClick={() => setSelectedCategory(category)}
            >
              {CATEGORY_MAP[category]}
            </button>
          ))}
        </div>
      </section>

      {/* 标签筛选 */}
      {tags.length > 0 && (
        <section className="mt-4">
          <h2 className="text-xl font-bold text-gray-900 mb-4">标签</h2>
          <div className="flex flex-wrap gap-2">
            <button
              className="px-3 py-1 rounded-full text-sm bg-gray-200 text-gray-700 hover:bg-gray-300 transition"
              onClick={() => setSelectedTag('all')}
            >
              全部
            </button>
            {tags.map((tag) => (
              <button
                key={tag}
                className={`px-3 py-1 rounded-full text-sm font-medium transition ${
                  selectedTag === tag
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
                onClick={() => setSelectedTag(tag)}
              >
                #{tag}
              </button>
            ))}
          </div>
        </section>
      )}

      {/* 底部 */}
      <footer className="mt-12 pt-6 border-t border-gray-200 text-center text-gray-500 text-sm">
        Creative Radar · 每日创意灵感 + 灵感学习卡片 + 邮件推送
      </footer>
    </div>
  );
};

export default Home;
