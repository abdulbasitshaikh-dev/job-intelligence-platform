export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
}

export interface JobPreference {
  id: number;
  user_id: number;
  keywords: string[];
  locations: string[];
  employment_types: string[];
  work_modes: string[];
  min_salary: number | null;
  max_salary: number | null;
  currency: string;
  created_at: string;
  updated_at: string;
}

export interface Job {
  id: number;
  source_id: number;
  source_name?: string;
  external_id: string;
  title: string;
  company: string;
  location: string;
  description: string;
  url: string;
  canonical_url: string;
  employment_type: 'Full-time' | 'Part-time' | 'Contract' | 'Internship' | 'Temporary' | 'Other';
  work_mode: 'Remote' | 'Hybrid' | 'On-site' | 'Unspecified';
  salary_min: number | null;
  salary_max: number | null;
  currency: string;
  posted_at: string | null;
  first_seen_at: string;
  last_seen_at: string;
  is_active: boolean;
  dedupe_hash: string;
  match_score?: number;
  match_reasons?: string[];
  is_saved?: boolean;
  application_status?: string;
}

export interface JobApplication {
  id: number;
  user_id: number;
  job_id: number;
  status: 'interested' | 'applied' | 'interview' | 'rejected' | 'offer' | 'withdrawn';
  notes: string | null;
  applied_at: string | null;
  created_at: string;
  updated_at: string;
  job?: Job;
}

export interface NotificationConfig {
  id: number;
  user_id: number;
  email_notifications: boolean;
  webhook_url: string | null;
  min_match_score: number;
  created_at: string;
  updated_at: string;
}

export interface Source {
  id: number;
  name: string;
  base_url: string;
  source_type: 'HTML' | 'API' | 'BROWSER';
  scraper_type: string;
  enabled: boolean;
  configuration: Record<string, any>;
  rate_limit_delay: number;
  last_run_at: string | null;
  last_success_at: string | null;
  last_failure_at: string | null;
  consecutive_failures: number;
  created_at: string;
  updated_at: string;
}

export interface ScraperRun {
  id: number;
  source_id: number;
  started_at: string;
  completed_at: string | null;
  status: 'PENDING' | 'IN_PROGRESS' | 'SUCCESS' | 'FAILED';
  pages_fetched: number;
  jobs_found: number;
  jobs_created: number;
  duplicates_found: number;
  error_message: string | null;
  duration_seconds: number | null;
}

export interface PaginatedResponse<T> {
  items: T[];
  page: number;
  page_size: number;
  total: number;
  pages: number;
}

export interface PlatformStats {
  active_jobs: number;
  total_jobs: number;
  configured_sources: number;
  healthy_sources: number;
  last_successful_sync: string | null;
  jobs_added_recently: number;
}

export interface SystemStats {
  total_users: number;
  total_jobs: number;
  active_jobs: number;
  total_sources: number;
  total_scraper_runs: number;
  successful_runs?: number;
  failed_runs?: number;
  last_successful_sync?: string | null;
}

export interface SystemHealth {
  status: string;
  components: {
    database: { status: string };
    redis: { status: string };
    celery: { status: string; broker: string };
    scheduler: { status: string; schedule: string };
  };
  last_run: {
    id: number | null;
    status: string;
    timestamp: string | null;
  } | null;
}

