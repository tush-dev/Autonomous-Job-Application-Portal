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
  raw_text?: string;
  parsed_data?: ParsedResumeData;
  parsing_confidence?: number;
  parsing_status: string;
  parsing_error?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ParsedResumeData {
  name: string;
  email: string;
  phone: string;
  skills: string[];
  experience: ResumeEntry[];
  projects: ResumeEntry[];
  education: ResumeEntry[];
  certifications: string[];
  summary: string;
}

export interface ResumeEntry {
  title?: string;
  organization?: string;
  date?: string;
  description?: string;
  highlights?: string[];
}

export interface JobMatchBrief {
  match_score: number;
  skills_matched: string[];
  missing_skills: string[];
  ats_compatibility?: number;
  interview_probability?: number;
  reasoning?: string;
  is_recommended: boolean;
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
  is_saved: boolean;
  has_applied: boolean;
  posted_at: string;
  match?: JobMatchBrief | null;
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

export interface JobMatchData {
  match_score: number;
  skills_matched: string[];
  missing_skills: string[];
  ats_compatibility?: number;
  interview_probability?: number;
  salary_fit?: number;
  experience_fit?: number;
  location_fit?: number;
  growth_potential?: number;
  learning_difficulty?: string;
  reasoning?: string;
  is_recommended: boolean;
}

export type JobWithMatch = Job;

export interface CareerInsightsData {
  resume_health_score?: number;
  ats_score?: number;
  technical_strength?: number;
  communication_score?: number;
  leadership_score?: number;
  project_quality?: number;
  skill_coverage?: number;
  completeness?: number;
  readability?: number;
  industry_alignment?: string;
  career_level?: string;
  suggested_skills: string[];
  weak_bullet_points: string[];
  missing_metrics: string[];
  weak_action_verbs: string[];
  formatting_suggestions: string[];
  insights: Record<string, unknown>;
}

export interface DashboardData {
  resume_health: CareerInsightsData | null;
  recommended_jobs: JobWithMatch[];
  recent_jobs: JobWithMatch[];
  upcoming_interviews: Array<{
    id: string;
    interview_type: string;
    scheduled_at: string | null;
    status: string;
  }>;
  application_stats: {
    total: number;
    applied: number;
    interview: number;
    offer: number;
    rejected: number;
  };
  learning_path: LearningPathItem[];
  career_insights: CareerInsightsData | null;
}

export interface LearningPathItem {
  id: string;
  skill_name: string;
  category?: string;
  difficulty?: string;
  priority?: string;
  resources?: Record<string, unknown>;
  progress: number;
  completed: boolean;
  estimated_hours?: number;
}
