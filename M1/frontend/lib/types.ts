export type UserRole = "STUDENT" | "RECRUITER" | "ADMIN";

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface SkillBadge {
  name: string;
  category: string;
  proficiency: "BEGINNER" | "INTERMEDIATE" | "ADVANCED" | "EXPERT";
  years_experience: number;
  is_verified: boolean;
}

export interface Education {
  id?: string;
  institution_name: string;
  degree: string;
  major: string;
  start_date: string;
  end_date?: string | null;
  gpa?: number | null;
  relevant_coursework?: string[];
}

export interface Project {
  id?: string;
  title: string;
  role: string;
  summary: string;
  bullets: string[];
  technologies_used: string[];
  repo_url?: string | null;
  live_url?: string | null;
}

export interface WorkExperience {
  id?: string;
  company_name: string;
  role_title: string;
  location?: string | null;
  start_date: string;
  end_date?: string | null;
  bullets: string[];
  technologies_used: string[];
}

export interface CandidateProfile {
  id: string;
  user_id: string;
  university_name: string;
  degree_major: string;
  gpa?: number | null;
  graduation_term: string;
  graduation_year: number;
  requires_sponsorship: boolean;
  preferred_locations: string[];
  skills: SkillBadge[];
  educations: Education[];
  projects: Project[];
  work_experiences: WorkExperience[];
  created_at: string;
  updated_at: string;
}

export interface ResumeUploadResponse {
  resume_id: string;
  candidate_id: string;
  file_name: string;
  file_size_bytes: number;
  sha256_hash: string;
  is_primary: boolean;
  sections_extracted_count: number;
  parsed_skills_count: number;
  parsed_projects_count: number;
  message: string;
  uploaded_at: string;
}

export interface JobRequirement {
  id: string;
  requirement_type: string;
  description: string;
  is_mandatory: boolean;
}

export interface Job {
  id: string;
  title: string;
  company_name: string;
  location: string;
  is_remote: boolean;
  raw_description: string;
  cleaned_markdown: string;
  min_gpa: number;
  required_graduation_years: number[];
  visa_sponsorship_available: boolean;
  monthly_stipend_cents?: number | null;
  is_active: boolean;
  deadline?: string | null;
  requirements: JobRequirement[];
  created_at: string;
  updated_at: string;
  match_score?: number; 
}

export interface JobListResponse {
  items: Job[];
  total: number;
  page: number;
  page_size: number;
}

export type ApplicationStage =
  | "WISHLIST"
  | "APPLIED"
  | "SCREENING"
  | "TECHNICAL_ASSESSMENT"
  | "INTERVIEW"
  | "OFFER"
  | "REJECTED"
  | "WITHDRAWN";

export interface StageHistoryEntry {
  id: string;
  previous_stage: string | null;
  new_stage: string;
  notes?: string | null;
  transitioned_at: string;
}

export interface Application {
  id: string;
  candidate_id: string;
  job_id: string;
  job_title?: string;
  company_name?: string;
  current_stage: ApplicationStage;
  overall_match_score?: number | null;
  match_breakdown?: Record<string, any>;
  skill_gap_roadmap?: Record<string, any>;
  cover_letter_markdown?: string | null;
  applied_at?: string | null;
  created_at: string;
  updated_at: string;
  stage_history: StageHistoryEntry[];
}

export interface KanbanBoard {
  wishlist: Application[];
  applied: Application[];
  screening: Application[];
  technical_assessment: Application[];
  interview: Application[];
  offer: Application[];
  rejected: Application[];
  withdrawn: Application[];
}

export interface StandardJobPosting {
  id: string;
  job_title: string;
  company: string;
  location: string;
  work_mode: string;
  is_remote: boolean;
  job_description: string;
  responsibilities: string[];
  required_skills: string[];
  preferred_skills: string[];
  qualifications: string[];
  experience_requirements: string | string[];
  education_requirements: string | string[];
  stipend?: string | null;
  domain: string;
  tags: string[];
  posted_at: string;
}

export interface MatchedChunkInfo {
  chunk_type: string;
  content_snippet: string;
  score: number;
}

export interface SemanticSearchResultItem {
  job: StandardJobPosting;
  relevance_score: number;
  matched_chunks: MatchedChunkInfo[];
}

export interface SemanticSearchRequest {
  query: string;
  domain?: string | null;
  is_remote?: boolean | null;
  top_k?: number;
  use_reranker?: boolean;
}

export interface SemanticSearchResponse {
  total_matches: number;
  query: string;
  results: SemanticSearchResultItem[];
}

export interface ScoreBreakdown {
  required_skills_score: number;
  preferred_skills_score: number;
  projects_experience_score: number;
  education_qualifications_score: number;
  semantic_relevance_score: number;
}

export interface JobMatchResult {
  job: StandardJobPosting;
  overall_match_score: number;
  score_breakdown: ScoreBreakdown;
  matched_skills: string[];
  missing_required_skills: string[];
  missing_preferred_skills: string[];
  reasoning: string;
  recommendation_tier: string;
}

export interface MatchRequest {
  candidate_profile: any;
  top_k?: number;
  domain?: string | null;
  is_remote?: boolean | null;
  use_llm_reasoning?: boolean;
}

export interface MatchResponse {
  candidate_name: string;
  candidate_skills: string[];
  total_evaluated_jobs: number;
  results: JobMatchResult[];
}
