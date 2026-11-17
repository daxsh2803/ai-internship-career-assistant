import {
  Application,
  AuthResponse,
  CandidateProfile,
  Job,
  JobListResponse,
  KanbanBoard,
  ResumeUploadResponse,
  User,
} from "./types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

class ApiClientError extends Error {
  constructor(
    public status: number,
    public message: string,
    public data?: any
  ) {
    super(message);
    this.name = "ApiClientError";
  }
}

class ApiClient {
  private getAuthHeader(): Record<string, string> {
    if (typeof window === "undefined") return {};
    const token = localStorage.getItem("auth_token");
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    const headers = {
      "Content-Type": "application/json",
      ...this.getAuthHeader(),
      ...(options.headers as Record<string, string>),
    };

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      if (response.status === 401 && typeof window !== "undefined") {

        localStorage.removeItem("auth_token");
        localStorage.removeItem("auth_user");
      }

      if (!response.ok) {
        let errMessage = `HTTP ${response.status}: ${response.statusText}`;
        let errData = null;
        try {
          errData = await response.json();
          errMessage = errData.detail || errData.message || errMessage;
        } catch (_) {}
        throw new ApiClientError(response.status, errMessage, errData);
      }

      return (await response.json()) as T;
    } catch (err: any) {
      if (err instanceof ApiClientError) throw err;
      throw new ApiClientError(0, err.message || "Network request failed");
    }
  }

  async register(data: {
    email: string;
    password: string;
    full_name: string;
    role?: string;
  }): Promise<AuthResponse> {
    const res = await this.request<AuthResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    });
    if (typeof window !== "undefined") {
      localStorage.setItem("auth_token", res.access_token);
      localStorage.setItem("auth_user", JSON.stringify(res.user));
    }
    return res;
  }

  async login(data: {
    email: string;
    password: string;
  }): Promise<AuthResponse> {
    const res = await this.request<AuthResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    });
    if (typeof window !== "undefined") {
      localStorage.setItem("auth_token", res.access_token);
      localStorage.setItem("auth_user", JSON.stringify(res.user));
    }
    return res;
  }

  async getMe(): Promise<User> {
    return this.request<User>("/auth/me");
  }

  logout(): void {
    if (typeof window !== "undefined") {
      localStorage.removeItem("auth_token");
      localStorage.removeItem("auth_user");
      window.location.href = "/login";
    }
  }

  async getProfile(): Promise<CandidateProfile> {
    return this.request<CandidateProfile>("/profiles/me");
  }

  async createProfile(data: {
    university_name: string;
    degree_major: string;
    gpa?: number | null;
    graduation_term: string;
    graduation_year: number;
    requires_sponsorship?: boolean;
    preferred_locations?: string[];
  }): Promise<CandidateProfile> {
    return this.request<CandidateProfile>("/profiles", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async uploadResume(file: File): Promise<ResumeUploadResponse> {
    const url = `${API_BASE_URL}/profiles/resume/upload`;
    const formData = new FormData();
    formData.append("file", file);

    const headers: Record<string, string> = {
      ...this.getAuthHeader(),
    };

    const response = await fetch(url, {
      method: "POST",
      headers,
      body: formData,
    });

    if (!response.ok) {
      let errMessage = `Upload failed with status ${response.status}`;
      try {
        const err = await response.json();
        errMessage = err.detail || errMessage;
      } catch (_) {}
      throw new ApiClientError(response.status, errMessage);
    }

    return (await response.json()) as ResumeUploadResponse;
  }

  async listJobs(params?: {
    page?: number;
    page_size?: number;
    is_remote?: boolean;
    max_gpa?: number;
    q?: string;
  }): Promise<JobListResponse> {
    const query = new URLSearchParams();
    if (params?.page) query.append("page", params.page.toString());
    if (params?.page_size) query.append("page_size", params.page_size.toString());
    if (params?.is_remote !== undefined) query.append("is_remote", params.is_remote.toString());
    if (params?.max_gpa !== undefined) query.append("max_gpa", params.max_gpa.toString());
    if (params?.q) query.append("q", params.q);

    const queryString = query.toString() ? `?${query.toString()}` : "";
    return this.request<JobListResponse>(`/jobs${queryString}`);
  }

  async getJob(id: string): Promise<Job> {
    return this.request<Job>(`/jobs/${id}`);
  }

  async getKanban(): Promise<KanbanBoard> {
    return this.request<KanbanBoard>("/applications/kanban");
  }

  async createApplication(data: {
    job_id: string;
    cover_letter_markdown?: string;
  }): Promise<Application> {
    return this.request<Application>("/applications", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async updateApplicationStage(
    applicationId: string,
    newStage: string,
    notes?: string
  ): Promise<Application> {
    return this.request<Application>(`/applications/${applicationId}/stage`, {
      method: "PATCH",
      body: JSON.stringify({ new_stage: newStage, notes }),
    });
  }
}

export const apiClient = new ApiClient();
