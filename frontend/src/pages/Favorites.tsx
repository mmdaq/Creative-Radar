import React, { useState, useEffect } from 'react';
import { api, type Favorite, type CreativeItem } from '../api/client';

export const Favorites: React.FC = () => {
  const [favorites, setFavorites] = useState<Favorite[]>([]);
  const [items, setItems] = useState<{ [key: string]: CreativeItem }>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadFavorites();
  }, []);

  const loadFavorites = async () => {
    try {
      const favList = await api.getFavorites();
      setFavorites(favList);

      // 并行加载收藏内容
      const itemPromises = favList.map(async (fav) => {
        try {
          const item = await api.getItem(fav.item_id);
          return { [fav.item_id]: item };
        } catch {
          return {};
        }
      });

      const itemResults = await Promise.all(itemPromises);
      const mergedItems: { [key: string]: CreativeItem } = {};
      itemResults.forEach((itemsMap) => {
        Object.assign(mergedItems, itemsMap);
      });
      setItems(mergedItems);
    } catch (error) {
      console.error('加载收藏失败:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-8 text-gray-500">加载中...</div>;
  }

  if (favorites.length === 0) {
    return (
      <div>
        <header className="text-center py-8">
          <h1 className="text-3xl font-bold text-gray-900">我的收藏</h1>
          <p className="text-gray-600 mt-2">暂无收藏，去看看创意内容吧</p>
        </header>
        <div className="mt-8 text-center">
          <span className="text-gray-500">收藏后会显示在这里</span>
        </div>
      </div>
    );
  }

  return (
    <div>
      <header className="text-center py-8">
        <h1 className="text-3xl font-bold text-gray-900">我的收藏</h1>
        <p className="text-gray-600 mt-2">{favorites.length} 个收藏</p>
      </header>

      <section className="mt-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {favorites.map((fav) => {
            const item = items[fav.item_id];
            if (!item) return null;
            return (
              <div key={fav.id} className="bg-white rounded-lg shadow-md overflow-hidden">
                {item.thumbnail && (
                  <img
                    src={item.thumbnail}
                    alt={item.title}
                    className="w-full h-32 object-cover"
                    loading="lazy"
                  />
                )}
                <div className="p-4">
                  <h3 className="font-semibold text-lg text-gray-900">{item.title}</h3>
                  <p className="text-sm text-gray-600 mt-1">
                    {item.source} · {item.category}
                  </p>
                  <p className="text-xs text-gray-500 mt-2">
                    收藏于 {new Date(fav.created_at).toLocaleString('zh-CN')}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
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

export default Favorites;
