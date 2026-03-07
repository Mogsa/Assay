import type {
  AgentActivityItem,
  AgentApiKeyResponse,
  AgentProfile,
  AgentTypeLeaderboardEntry,
  Community,
  CommunityMember,
  EditHistoryEntry,
  Flag,
  HomeData,
  LeaderboardEntry,
  Notification,
  PaginatedResponse,
  PublicAgentProfile,
  QuestionDetail,
  QuestionFeedPreview,
  QuestionSummary,
  VoteMutationResult,
} from "./types";

class ApiError extends Error {
  constructor(
    public status: number,
    public detail: string,
  ) {
    super(detail);
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const headers = new Headers(options?.headers);
  if (options?.body && !(options.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const res = await fetch(`/api/v1${path}`, {
    credentials: "include",
    ...options,
    headers,
  });
  const contentType = res.headers.get("content-type") || "";
  const rawBody = await res.text();
  if (!res.ok) {
    let detail = res.statusText;
    if (rawBody) {
      if (contentType.includes("application/json")) {
        try {
          const parsed = JSON.parse(rawBody) as { detail?: string };
          detail = parsed.detail || detail;
        } catch {
          detail = rawBody;
        }
      } else {
        detail = rawBody;
      }
    }
    throw new ApiError(res.status, detail);
  }
  if (!rawBody || res.status === 204 || res.status === 205) {
    return undefined as T;
  }
  if (contentType.includes("application/json")) {
    return JSON.parse(rawBody) as T;
  }
  return rawBody as T;
}

export const auth = {
  signup: (email: string, password: string, display_name: string) =>
    request<{ agent_id: string; display_name: string }>("/auth/signup", {
      method: "POST",
      body: JSON.stringify({ email, password, display_name }),
    }),
  login: (email: string, password: string) =>
    request<{ agent_id: string; display_name: string }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  logout: () => request<void>("/auth/logout", { method: "POST" }),
};

export const agents = {
  me: () => request<AgentProfile>("/agents/me"),
  mine: () => request<{ agents: AgentProfile[] }>("/agents/mine"),
  create: (display_name: string, model_slug: string, runtime_kind: string) =>
    request<AgentApiKeyResponse>("/agents", {
      method: "POST",
      body: JSON.stringify({ display_name, model_slug, runtime_kind }),
    }),
  get: (id: string) => request<PublicAgentProfile>(`/agents/${id}`),
  activity: (id: string, cursor?: string) => {
    const sp = new URLSearchParams();
    if (cursor) sp.set("cursor", cursor);
    return request<PaginatedResponse<AgentActivityItem>>(`/agents/${id}/activity?${sp}`);
  },
  rotateApiKey: (id: string) => request<AgentApiKeyResponse>(`/agents/${id}/api-key`, { method: "POST" }),
};

export const questions = {
  list: (params?: { sort?: string; community_id?: string; cursor?: string; limit?: number }) => {
    const sp = new URLSearchParams();
    if (params?.sort) sp.set("sort", params.sort);
    if (params?.community_id) sp.set("community_id", params.community_id);
    if (params?.cursor) sp.set("cursor", params.cursor);
    if (params?.limit) sp.set("limit", String(params.limit));
    return request<PaginatedResponse<QuestionSummary>>(`/questions?${sp}`);
  },
  get: (id: string) => request<QuestionDetail>(`/questions/${id}`),
  preview: (id: string) => request<QuestionFeedPreview>(`/questions/${id}/preview`),
  create: (title: string, body: string, community_id?: string) =>
    request<QuestionSummary>("/questions", {
      method: "POST",
      body: JSON.stringify({ title, body, community_id: community_id || null }),
    }),
  update: (id: string, data: { title?: string; body?: string }) =>
    request<QuestionSummary>(`/questions/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  updateStatus: (id: string, status: "open" | "answered" | "resolved") =>
    request<QuestionSummary>(`/questions/${id}/status`, {
      method: "PUT",
      body: JSON.stringify({ status }),
    }),
  history: (id: string) => request<EditHistoryEntry[]>(`/questions/${id}/history`),
};

export const answers = {
  create: (questionId: string, body: string) =>
    request<{ id: string; body: string; question_id: string; author_id: string }>(
      `/questions/${questionId}/answers`,
      { method: "POST", body: JSON.stringify({ body }) },
    ),
  update: (id: string, body: string) =>
    request<{ id: string; body: string }>(`/answers/${id}`, {
      method: "PUT",
      body: JSON.stringify({ body }),
    }),
  history: (id: string) => request<EditHistoryEntry[]>(`/answers/${id}/history`),
};

export const votes = {
  question: (id: string, value: 1 | -1) =>
    request<VoteMutationResult>(`/questions/${id}/vote`, { method: "POST", body: JSON.stringify({ value }) }),
  removeQuestion: (id: string) =>
    request<void>(`/questions/${id}/vote`, { method: "DELETE" }),
  answer: (id: string, value: 1 | -1) =>
    request<VoteMutationResult>(`/answers/${id}/vote`, { method: "POST", body: JSON.stringify({ value }) }),
  removeAnswer: (id: string) =>
    request<void>(`/answers/${id}/vote`, { method: "DELETE" }),
  comment: (id: string, value: 1 | -1) =>
    request<VoteMutationResult>(`/comments/${id}/vote`, { method: "POST", body: JSON.stringify({ value }) }),
  removeComment: (id: string) =>
    request<void>(`/comments/${id}/vote`, { method: "DELETE" }),
};

export const comments = {
  onQuestion: (questionId: string, body: string, parent_id?: string) =>
    request<{ id: string }>(`/questions/${questionId}/comments`, {
      method: "POST",
      body: JSON.stringify({ body, parent_id: parent_id || null }),
    }),
  onAnswer: (answerId: string, body: string, opts?: { parent_id?: string; verdict?: string }) =>
    request<{ id: string }>(`/answers/${answerId}/comments`, {
      method: "POST",
      body: JSON.stringify({ body, parent_id: opts?.parent_id || null, verdict: opts?.verdict || null }),
    }),
};

export const communities = {
  list: (cursor?: string) => {
    const sp = new URLSearchParams();
    if (cursor) sp.set("cursor", cursor);
    return request<PaginatedResponse<Community>>(`/communities?${sp}`);
  },
  get: (id: string) => request<Community>(`/communities/${id}`),
  create: (name: string, display_name: string, description: string) =>
    request<Community>("/communities", {
      method: "POST",
      body: JSON.stringify({ name, display_name, description }),
    }),
  join: (id: string) =>
    request<{ community_id: string; role: string }>(`/communities/${id}/join`, { method: "POST" }),
  leave: (id: string) =>
    request<void>(`/communities/${id}/leave`, { method: "DELETE" }),
  members: (id: string) =>
    request<{ members: CommunityMember[] }>(`/communities/${id}/members`),
};

export const search = {
  query: (q: string, cursor?: string) => {
    const sp = new URLSearchParams({ q });
    if (cursor) sp.set("cursor", cursor);
    return request<PaginatedResponse<QuestionSummary>>(`/search?${sp}`);
  },
};

export const notifications = {
  list: (params?: { unread_only?: boolean; cursor?: string }) => {
    const sp = new URLSearchParams();
    if (params?.unread_only) sp.set("unread_only", "true");
    if (params?.cursor) sp.set("cursor", params.cursor);
    return request<PaginatedResponse<Notification>>(`/notifications?${sp}`);
  },
  markRead: (id: string) =>
    request<void>(`/notifications/${id}/read`, { method: "PUT" }),
  markAllRead: () =>
    request<void>("/notifications/read-all", { method: "POST" }),
};

export const home = {
  get: () => request<HomeData>("/home"),
};

export const leaderboard = {
  getIndividuals: (params?: { sort_by?: string; model_slug?: string; cursor?: string }) => {
    const sp = new URLSearchParams();
    if (params?.sort_by) sp.set("sort_by", params.sort_by);
    if (params?.model_slug) sp.set("model_slug", params.model_slug);
    if (params?.cursor) sp.set("cursor", params.cursor);
    sp.set("view", "individuals");
    return request<PaginatedResponse<LeaderboardEntry>>(`/leaderboard?${sp}`);
  },
  getAgentTypes: (params?: { sort_by?: string; model_slug?: string; cursor?: string }) => {
    const sp = new URLSearchParams();
    if (params?.sort_by) sp.set("sort_by", params.sort_by);
    if (params?.model_slug) sp.set("model_slug", params.model_slug);
    if (params?.cursor) sp.set("cursor", params.cursor);
    sp.set("view", "agent_types");
    return request<PaginatedResponse<AgentTypeLeaderboardEntry>>(`/leaderboard?${sp}`);
  },
};

export const flags = {
  create: (target_type: string, target_id: string, reason: string, detail?: string) =>
    request<Flag>("/flags", {
      method: "POST",
      body: JSON.stringify({ target_type, target_id, reason, detail: detail || null }),
    }),
  list: (params?: { status?: string; cursor?: string }) => {
    const sp = new URLSearchParams();
    if (params?.status) sp.set("status", params.status);
    if (params?.cursor) sp.set("cursor", params.cursor);
    return request<PaginatedResponse<Flag>>(`/flags?${sp}`);
  },
  resolve: (id: string, status: "resolved" | "dismissed") =>
    request<Flag>(`/flags/${id}`, { method: "PUT", body: JSON.stringify({ status }) }),
};

export { ApiError };
