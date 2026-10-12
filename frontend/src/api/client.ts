/**
 * Creative Radar — 前端 API 客户端
 *
 * 调用后端 FastAPI 接口。
 */
import type { CreativeItem, CreativeCard, Favorite, Settings } from './types';

export type { CreativeItem, CreativeCard, Favorite, Settings };

const API_BASE = '/api';

class ApiClient {
  private async request<T>(endpoint: string, init?: RequestInit): Promise<T> {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      headers: { 'Content-Type': 'application/json' },
      ...init,
    });
    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }
    return response.json() as Promise<T>;
  }

  // ── 采集项 ──────────────────────────────────────────
  async getItems(params?: {
    status?: string;
    category?: string;
    source?: string;
    limit?: number;
    offset?: number;
  }): Promise<CreativeItem[]> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          searchParams.append(key, String(value));
        }
      });
    }
    return this.request<CreativeItem[]>(`/items?${searchParams.toString()}`);
  }

  async getToday(): Promise<CreativeItem[]> {
    return this.request<CreativeItem[]>('/items/today');
  }

  async getItem(id: string): Promise<CreativeItem> {
    return this.request<CreativeItem>(`/items/${id}`);
  }

  // ── 卡片 ────────────────────────────────────────────
  async getCard(itemId: string): Promise<CreativeCard> {
    return this.request<CreativeCard>(`/items/${itemId}/card`);
  }

  // ── 收藏 ────────────────────────────────────────────
  async getFavorites(): Promise<Favorite[]> {
    return this.request<Favorite[]>('/favorites');
  }

  async toggleFavorite(itemId: string, favorite: boolean): Promise<void> {
    await this.request<void>(`/favorites?item_id=${itemId}&favorite=${favorite ? 'true' : 'false'}`, {
      method: 'POST',
    });
  }

  // ── 搜索 ────────────────────────────────────────────
  async search(params: {
    q?: string;
    category?: string;
    source?: string;
    date_from?: string;
    date_to?: string;
    limit?: number;
    offset?: number;
  }): Promise<CreativeItem[]> {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.append(key, String(value));
      }
    });
    return this.request<CreativeItem[]>(`/search?${searchParams.toString()}`);
  }

  // ── 配置 ────────────────────────────────────────────
  async getSettings(): Promise<Settings> {
    return this.request<Settings>('/settings');
  }

  async updateSettings(settings: Partial<Settings>): Promise<void> {
    await this.request<void>('/settings', {
      method: 'PUT',
      body: JSON.stringify(settings),
    });
  }
}

export const api = new ApiClient();
export default api;
