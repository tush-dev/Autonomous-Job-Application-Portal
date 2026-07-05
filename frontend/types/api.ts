export interface User {
  id: string;
  email: string;
  full_name: string;
  avatar_url?: string;
  role: "user" | "admin";
  is_verified: boolean;
  mfa_enabled: boolean;
  created_at: string;
}

export interface AuthResponse {
  user: User;
  access_token: string;
  refresh_token: string;
  expires_in: number;
  mfa_required?: boolean;
}

export interface Resume {
  id: string;
  file_name: string;
  file_size: number;
  file_type: string;
  parsed_data?: any;
  parsing_confidence?: number;
  parsing_status: string;
  is_active: boolean;
  created_at: string;
}

export interface Job {
  id: string;
  company?: {
    id: string;
    name: string;
    logo_url?: string;
  };
  source: string;
  title: string;
  location?: string;
  remote: string;
  salary_min?: number;
  salary_max?: number;
  salary_currency: string;
  skills_required: string[];
  application_url?: string;
  match_score?: number;
  match_reasons: string[];
  missing_skills: string[];
  estimated_interview_chance?: string;
  is_saved: boolean;
  has_applied: boolean;
  posted_at: string;
}

export interface Application {
  id: string;
  job: any;
  status: string;
  approval_required: boolean;
  submitted_at?: string;
  notes?: string;
  timeline: TimelineEvent[];
  cover_letter?: CoverLetter;
  created_at: string;
}

export interface TimelineEvent {
  id: string;
  event_type: string;
  description?: string;
  created_at: string;
}

export interface CoverLetter {
  id: string;
  content: string;
  tone: string;
  word_count: number;
  created_at: string;
}

export interface ApplicationStats {
  total: number;
  applied: number;
  screening: number;
  interview: number;
  offer: number;
  rejected: number;
  failed: number;
  interview_rate: number;
  offer_rate: number;
}

export interface Notification {
  id: string;
  type: string;
  title: string;
  body?: string;
  is_read: boolean;
  created_at: string;
}

export interface PaginationMeta {
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

export interface APIResponse<T> {
  success: boolean;
  data: T;
  pagination?: PaginationMeta;
  error?: {
    code: string;
    message: string;
    details?: Array<{ field?: string; message: string }>;
  };
}
