import React, { useState, useEffect } from 'react';
import { api, type CreativeItem, type CreativeCard } from '../api/client';

export const Detail: React.FC = () => {
  const [item, setItem] = useState<CreativeItem | null>(null);
  const [card, setCard] = useState<CreativeCard | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const itemId = params.get('id');
    if (itemId) {
      loadItem(itemId);
    } else {
      setLoading(false);
    }
  }, []);

  const loadItem = async (itemId: string) => {
    try {
      const [itemData, cardData] = await Promise.all([
        api.getItem(itemId),
        api.getCard(itemId),
      ]);
      setItem(itemData);
      setCard(cardData);
    } catch (error) {
      console.error('加载详情失败:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-8 text-gray-500">加载中...</div>;
  }

  if (!item) {
    return <div className="text-center py-8 text-gray-500">未找到该内容</div>;
  }

  return (
    <div>
      {/* 标题 */}
      <header className="text-center py-8">
        <h1 className="text-3xl font-bold text-gray-900">{item.title || '无标题'}</h1>
        <p className="text-gray-600 mt-2">
          来自 {item.source} · {item.category}
        </p>
        <p className="text-gray-500 text-sm">
          发布于 {new Date(item.published_at || '').toLocaleDateString('zh-CN', { year: 'numeric', month: 'short', day: 'numeric' })}
        </p>
      </header>

      {/* 图片 */}
      {item.thumbnail && (
        <div className="mt-4">
          <img
            src={item.thumbnail}
            alt={item.title}
            className="max-w-4xl mx-auto rounded-lg shadow-lg"
            loading="lazy"
          />
        </div>
      )}

      {/* 推荐理由 */}
      {card?.recommendation && (
        <section className="mt-6 max-w-4xl mx-auto">
          <h2 className="text-xl font-bold text-gray-900 mb-2">⭐ 推荐理由</h2>
          <p className="text-gray-700 leading-relaxed">{card.recommendation}</p>
        </section>
      )}

      {/* 创意核心 */}
      {card?.creative_core && (
        <section className="mt-6 max-w-4xl mx-auto">
          <h2 className="text-xl font-bold text-gray-900 mb-2">💡 创意核心</h2>
          <p className="text-gray-700 leading-relaxed">{card.creative_core}</p>
        </section>
      )}

      {/* 视觉拆解 */}
      {card?.visual_analysis && (
        <section className="mt-6 max-w-4xl mx-auto">
          <h2 className="text-xl font-bold text-gray-900 mb-2">👀 视觉拆解</h2>
          <p className="text-gray-700 leading-relaxed">{card.visual_analysis}</p>
        </section>
      )}

      {/* 创意套路 */}
      {card?.creative_tricks && (
        <section className="mt-6 max-w-4xl mx-auto">
          <h2 className="text-xl font-bold text-gray-900 mb-2">🎯 创意套路</h2>
          <p className="text-gray-700 leading-relaxed">{card.creative_tricks}</p>
        </section>
      )}

      {/* 模仿方法 */}
      {card?.imitation_method && (
        <section className="mt-6 max-w-4xl mx-auto">
          <h2 className="text-xl font-bold text-gray-900 mb-2">🧠 可直接模仿</h2>
          <ol className="list-decimal list-inside space-y-2 text-gray-700">
            {card.imitation_method.split('\n').filter(Boolean).map((step: string, idx: number) => (
              <li key={idx}>{step}</li>
            ))}
          </ol>
        </section>
      )}

      {/* 应用场景 */}
      {card?.application && (
        <section className="mt-6 max-w-4xl mx-auto">
          <h2 className="text-xl font-bold text-gray-900 mb-2">📋 如何应用到自己的项目</h2>
          <p className="text-gray-700 leading-relaxed">{card.application}</p>
        </section>
      )}

      {/* AI 创作提示 */}
      {card?.ai_prompt && (
        <section className="mt-6 max-w-4xl mx-auto">
          <h2 className="text-xl font-bold text-gray-900 mb-2">🤖 AI 继续创作提示</h2>
          <pre className="bg-gray-900 text-green-400 p-4 rounded-lg text-sm overflow-x-auto">
            {card.ai_prompt}
          </pre>
        </section>
      )}

      {/* 原始链接 */}
      {item.source_url && (
        <section className="mt-6 text-center">
          <a
            href={item.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
          >
            <span className="text-sm">查看原作品</span>
            <svg
              className="w-4 h-4 ml-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
              />
            </svg>
          </a>
        </section>
      )}

      {/* 收藏按钮 */}
      <section className="mt-6 text-center">
        <button
          className="px-4 py-2 bg-favorite-500 text-white rounded-lg hover:bg-favorite-600 transition"
          onClick={() => {
            if (item) {
              api.toggleFavorite(item.id, true);
            }
          }}
        >
          收藏
        </button>
      </section>

      {/* 底部 */}
      <footer className="mt-12 pt-6 border-t border-gray-200 text-center text-gray-500 text-sm">
        <button
          className="underline hover:text-primary-600"
          onClick={() => window.history.back()}
        >
          返回
        </button>
      </footer>
    </div>
  );
};

export default Detail;
