import React, { useState, useEffect } from 'react';
import { api, type Settings as SettingsType } from '../api/client';

export const Settings: React.FC = () => {
  const [settings, setSettings] = useState<SettingsType | null>(null);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const data = await api.getSettings();
      setSettings(data);
    } catch (error) {
      console.error('加载配置失败:', error);
    }
  };

  const handleSave = async () => {
    if (!settings) return;
    setSaving(true);
    setSaved(false);
    try {
      await api.updateSettings(settings);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (error) {
      console.error('保存配置失败:', error);
    } finally {
      setSaving(false);
    }
  };

  if (!settings) {
    return <div className="text-center py-8 text-gray-500">加载中...</div>;
  }

  return (
    <div>
      <header className="text-center py-8">
        <h1 className="text-3xl font-bold text-gray-900">设置</h1>
        <p className="text-gray-600 mt-2">配置您的 Creative Radar</p>
      </header>

      <div className="max-w-4xl mx-auto space-y-6">
        {/* AI 配置 */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">AI 模型配置</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-700 mb-1">AI 提供商</label>
              <select
                value={settings.ai_provider}
                onChange={(e) => setSettings({ ...settings, ai_provider: e.target.value })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
              >
                <option value="lmstudio">LM Studio</option>
                <option value="ollama">Ollama</option>
                <option value="deepseek">DeepSeek</option>
                <option value="qwen">Qwen</option>
                <option value="openai">OpenAI</option>
              </select>
            </div>

            <div>
              <label className="block text-sm text-gray-700 mb-1">API 地址</label>
              <input
                type="text"
                value={settings.ai_base_url}
                onChange={(e) => setSettings({ ...settings, ai_base_url: e.target.value })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
                placeholder="http://127.0.0.1:1234/v1"
              />
            </div>

            <div>
              <label className="block text-sm text-gray-700 mb-1">API Key</label>
              <input
                type="password"
                value={settings.ai_api_key}
                onChange={(e) => setSettings({ ...settings, ai_api_key: e.target.value })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
                placeholder="API Key"
              />
            </div>

            <div>
              <label className="block text-sm text-gray-700 mb-1">模型名称</label>
              <input
                type="text"
                value={settings.ai_model}
                onChange={(e) => setSettings({ ...settings, ai_model: e.target.value })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
                placeholder="Qwen / DeepSeek / Ollama 模型名"
              />
            </div>

            <div>
              <label className="block text-sm text-gray-700 mb-1">温度 (0-1)</label>
              <input
                type="number"
                step="0.1"
                min="0"
                max="1"
                value={settings.ai_temperature}
                onChange={(e) => setSettings({ ...settings, ai_temperature: parseFloat(e.target.value) })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
              />
            </div>
          </div>
        </div>

        {/* 邮件配置 */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">邮件配置</h2>
          <div className="space-y-4">
            <div className="flex items-center">
              <input
                type="checkbox"
                id="email-enabled"
                checked={settings.daily_enabled}
                onChange={(e) => setSettings({ ...settings, daily_enabled: e.target.checked })}
                className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
              />
              <label htmlFor="email-enabled" className="ml-2 text-sm text-gray-700">
                每日邮件推送
              </label>
            </div>

            <div>
              <label className="block text-sm text-gray-700 mb-1">SMTP 服务器</label>
              <input
                type="text"
                value={settings.smtp_host || ''}
                onChange={(e) => setSettings({ ...settings, smtp_host: e.target.value })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
                placeholder="smtp.qq.com"
              />
            </div>

            <div>
              <label className="block text-sm text-gray-700 mb-1">端口</label>
              <input
                type="number"
                value={settings.smtp_port}
                onChange={(e) => setSettings({ ...settings, smtp_port: parseInt(e.target.value) })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-700 mb-1">邮箱</label>
                <input
                  type="text"
                  value={settings.smtp_user || ''}
                  onChange={(e) => setSettings({ ...settings, smtp_user: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-700 mb-1">授权码</label>
                <input
                  type="password"
                  value={settings.smtp_password || ''}
                  onChange={(e) => setSettings({ ...settings, smtp_password: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-700 mb-1">发件邮箱</label>
                <input
                  type="email"
                  value={settings.email_from || ''}
                  onChange={(e) => setSettings({ ...settings, email_from: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-700 mb-1">收件邮箱</label>
                <input
                  type="email"
                  value={settings.email_to || ''}
                  onChange={(e) => setSettings({ ...settings, email_to: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                />
              </div>
            </div>
          </div>
        </div>

        {/* 每日邮件 */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">每日邮件</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-700 mb-1">发送时间</label>
              <input
                type="time"
                value={settings.daily_time}
                onChange={(e) => setSettings({ ...settings, daily_time: e.target.value })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-700 mb-1">每日数量</label>
              <select
                value={settings.daily_count}
                onChange={(e) => setSettings({ ...settings, daily_count: parseInt(e.target.value) })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
              >
                <option value={10}>10 条</option>
                <option value={20}>20 条</option>
                <option value={30}>30 条</option>
                <option value={50}>50 条</option>
              </select>
            </div>
          </div>
        </div>

        {/* 数据源 */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">数据源</h2>
          <div className="space-y-3">
            {[
              { key: 'pinterest', label: 'Pinterest' },
              { key: 'behance', label: 'Behance' },
              { key: 'dribbble', label: 'Dribbble' },
              { key: 'youtube', label: 'YouTube' },
              { key: 'bilibili', label: 'Bilibili' },
              { key: 'topys', label: 'TOPYS' },
            ].map((source) => (
              <div key={source.key} className="flex items-center justify-between">
                <span className="text-sm text-gray-700">{source.label}</span>
                <input
                  type="checkbox"
                  checked={settings.daily_enabled}
                  onChange={() => {}}
                  className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                />
              </div>
            ))}
          </div>
        </div>

        {/* 保存按钮 */}
        <div className="text-center">
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition disabled:opacity-50"
          >
            {saving ? '保存中...' : '保存配置'}
          </button>
          {saved && <p className="mt-2 text-green-600">配置已保存 ✓</p>}
        </div>
      </div>

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

export default Settings;
