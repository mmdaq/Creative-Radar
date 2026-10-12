import React, { useState } from 'react';
import { api, type CreativeItem } from '../api/client';

const CATEGORY_MAP = {
  visual_design: '视觉设计',
  video_creative: '视频创意',
  product_innovation: '产品创意',
  ai_creative: 'AI 创意',
  commercial: '商业创意',
  wild_idea: '脑洞创意',
} as const;

export const Search: React.FC = () => {
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState<string>('all');
  const [source, setSource] = useState<string>('all');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [results, setResults] = useState<CreativeItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async () => {
    if (!query.trim()) {
      setError('请输入搜索关键词');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const params = {
        q: query,
        category: category === 'all' ? undefined : category,
        source: source === 'all' ? undefined : source,
        date_from: dateFrom || undefined,
        date_to: dateTo || undefined,
      };
      const results = await api.search(params);
      setResults(results);
    } catch (err) {
      setError('搜索失败，请稍后重试');
      console.error(err);
    }
  };

  return (
    <div>
      {/* 标题 */}
      <header className="text-center py-8">
        <h1 className="text-3xl font-bold text-gray-900">搜索创意</h1>
        <p className="text-gray-600 mt-2">按关键词、标签、分类、来源、日期搜索</p>
      </header>

      {/* 搜索表单 */}
      <div className="max-w-2xl mx-auto mt-6">
        <div className="bg-white rounded-lg shadow-md p-4 space-y-4">
          <div className="flex gap-2">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="输入关键词搜索，例如：巨型、AI视频、海报..."
              className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
            <button
              onClick={handleSearch}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
            >
              搜索
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-700 mb-1">分类</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="all">全部分类</option>
                {Object.entries(CATEGORY_MAP).map(([key, value]) => (
                  <option key={key} value={key}>{value}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm text-gray-700 mb-1">来源</label>
              <select
                value={source}
                onChange={(e) => setSource(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="all">全部来源</option>
                <option value="youtube">YouTube</option>
                <option value="behance">Behance</option>
                <option value="dribbble">Dribbble</option>
                <option value="mozilla_hacks">Mozilla Hacks</option>
                <option value="smashing">Smashing Magazine</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-700 mb-1">发布日期（开始）</label>
              <input
                type="date"
                value={dateFrom}
                onChange={(e) => setDateFrom(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm text-gray-700 mb-1">发布日期（结束）</label>
              <input
                type="date"
                value={dateTo}
                onChange={(e) => setDateTo(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>

          {error && <p className="text-red-500 text-sm">{error}</p>}
        </div>
      </div>

      {/* 搜索结果 */}
      {loading ? (
        <div className="text-center py-8 text-gray-500">搜索中...</div>
      ) : results.length > 0 ? (
        <div className="mt-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            找到 {results.length} 条结果
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {results.map((item) => (
              <div key={item.id} className="bg-white rounded-lg shadow-md overflow-hidden">
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
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : !loading && query.trim() && (
        <div className="mt-6 text-center py-8 text-gray-500">
          没有找到相关内容
        </div>
      )}

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

export default Search;
