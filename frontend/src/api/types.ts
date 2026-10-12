export interface CreativeItem {
  id: string;
  source: string;
  source_url: string;
  title: string;
  description: string;
  author: string;
  published_at: string;
  content_type: string;
  category: string;
  tags: string[];
  thumbnail: string;
  media_url: string;
  language: string;
  raw: any;
  status: string;
  score: number;
  top_candidate: boolean;
  dedup_key: string;
  created_at: string;
  updated_at: string;
}

export interface CreativeCard {
  id: string;
  item_id: string;
  ai_summary: string;
  recommendation: string;
  creative_core: string;
  visual_analysis: string;
  creative_tricks: string;
  imitation_method: string;
  application: string;
  ai_prompt: string;
  created_at: string;
}

export interface Favorite {
  id: string;
  item_id: string;
  user: string;
  created_at: string;
}

export interface Settings {
  id: number;
  ai_provider: string;
  ai_base_url: string;
  ai_api_key: string;
  ai_model: string;
  ai_temperature: number;
  ai_max_tokens: number;
  daily_enabled: boolean;
  smtp_host: string;
  smtp_port: number;
  smtp_user: string;
  smtp_password: string;
  email_from: string;
  email_to: string;
  daily_count: number;
  daily_time: string;
}
