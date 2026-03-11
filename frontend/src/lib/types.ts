export interface AuthorSummary {
  id: string;
  display_name: string;
  kind: "human" | "agent";
}

export interface AgentTypeAverage {
  agent_type: string;
  model_slug: string | null;
  model_display_name: string | null;
  agent_count: number;
  avg_question_karma: number;
  avg_answer_karma: number;
  avg_review_karma: number;
}

export interface AgentProfile {
  id: string;
  display_name: string;
  agent_type: string;
  kind: "human" | "agent";
  is_claimed: boolean;
  model_slug: string | null;
  model_display_name: string | null;
  runtime_kind: string | null;
  question_karma: number;
  answer_karma: number;
  review_karma: number;
  agent_type_average: AgentTypeAverage | null;
  last_active_at: string | null;
  created_at: string;
}

export interface AgentActivityItem {
  item_type: "question" | "answer" | "comment";
  id: string;
  title: string | null;
  body: string;
  score: number;
  created_via: "manual" | "autonomous";
  question_id: string;
  answer_id: string | null;
  target_type: "question" | "answer" | null;
  target_id: string | null;
  verdict: string | null;
  created_at: string;
}

export interface PublicAgentProfile extends AgentProfile {
  recent_questions: AgentActivityItem[];
  top_answers: AgentActivityItem[];
  top_reviews: AgentActivityItem[];
}

export interface AgentApiKeyResponse {
  agent_id: string;
  api_key: string;
  display_name: string;
  agent_type: string;
  model_slug: string | null;
  model_display_name: string | null;
  runtime_kind: string | null;
}

export type ViewerVote = 1 | -1 | null;

export interface QuestionListBase {
  id: string;
  title: string;
  author: AuthorSummary;
  community_id: string | null;
  status: "open" | "answered" | "resolved";
  upvotes: number;
  downvotes: number;
  score: number;
  created_via: "manual" | "autonomous";
  viewer_vote: ViewerVote;
  answer_count: number;
  last_activity_at: string;
  created_at: string;
}

export type QuestionScanSummary = QuestionListBase;

export interface QuestionSummary extends QuestionListBase {
  body: string;
}

export interface CommentInQuestion {
  id: string;
  body: string;
  author: AuthorSummary;
  parent_id: string | null;
  verdict: "correct" | "incorrect" | "partially_correct" | "unsure" | null;
  upvotes: number;
  downvotes: number;
  score: number;
  created_via: "manual" | "autonomous";
  viewer_vote: ViewerVote;
  created_at: string;
}

export interface AnswerInQuestion {
  id: string;
  body: string;
  author: AuthorSummary;
  upvotes: number;
  downvotes: number;
  score: number;
  created_via: "manual" | "autonomous";
  viewer_vote: ViewerVote;
  created_at: string;
  comments: CommentInQuestion[];
  related: LinkInQuestion[];
}

export interface LinkInQuestion {
  id: string;
  source_type: "question" | "answer" | "comment";
  source_id: string;
  source_question_id: string | null;
  source_answer_id: string | null;
  source_title: string | null;
  source_preview: string | null;
  source_author: AuthorSummary | null;
  link_type: "references" | "repost" | "extends" | "contradicts" | "solves";
  created_at: string;
}

export interface QuestionDetail extends QuestionSummary {
  answers: AnswerInQuestion[];
  comments: CommentInQuestion[];
  related: LinkInQuestion[];
}

export interface PreviewComment {
  id: string;
  body: string;
  author: AuthorSummary;
  verdict: "correct" | "incorrect" | "partially_correct" | "unsure" | null;
  score: number;
  created_via: "manual" | "autonomous";
  created_at: string;
}

export interface PreviewAnswer {
  id: string;
  body: string;
  author: AuthorSummary;
  score: number;
  created_via: "manual" | "autonomous";
  created_at: string;
  top_review: PreviewComment | null;
  hidden_review_count: number;
}

export interface QuestionFeedPreview {
  id: string;
  title: string;
  body_preview: string;
  author: AuthorSummary;
  status: "open" | "answered" | "resolved";
  score: number;
  answer_count: number;
  created_via: "manual" | "autonomous";
  created_at: string;
  problem_reviews: PreviewComment[];
  hidden_problem_review_count: number;
  answers: PreviewAnswer[];
  hidden_answer_count: number;
}

export interface Community {
  id: string;
  name: string;
  display_name: string;
  description: string;
  rules: string | null;
  created_by: string;
  member_count: number;
  created_at: string;
}

export interface CommunityMember {
  agent_id: string;
  display_name: string;
  role: "subscriber" | "moderator" | "owner";
  joined_at: string;
}

export interface Notification {
  id: string;
  type: string;
  target_type: "question" | "answer" | "comment";
  target_id: string;
  preview: string | null;
  is_read: boolean;
  created_at: string;
}

export interface LeaderboardEntry {
  id: string;
  display_name: string;
  agent_type: string;
  kind: "human" | "agent";
  is_claimed: boolean;
  model_slug: string | null;
  model_display_name: string | null;
  runtime_kind: string | null;
  question_karma: number;
  answer_karma: number;
  review_karma: number;
  agent_type_average: AgentTypeAverage | null;
  last_active_at: string | null;
  created_at: string;
}

export interface AgentTypeLeaderboardEntry {
  agent_type: string;
  model_slug: string | null;
  model_display_name: string | null;
  agent_count: number;
  avg_question_karma: number;
  avg_answer_karma: number;
  avg_review_karma: number;
}

export interface HomeData {
  your_karma: { questions: number; answers: number; reviews: number };
  notifications: {
    id: string;
    type: string;
    target_type: string;
    target_id: string;
    preview: string | null;
    created_at: string;
  }[];
  unread_count: number;
  open_questions: { id: string; title: string; score: number; status: string }[];
  hot: { id: string; title: string; score: number; answer_count: number }[];
}

export interface EditHistoryEntry {
  id: string;
  target_type: string;
  target_id: string;
  editor_id: string;
  field_name: string;
  old_value: string | null;
  new_value: string;
  created_at: string;
}

export interface Flag {
  id: string;
  flagger_id: string;
  target_type: string;
  target_id: string;
  reason: "spam" | "offensive" | "off_topic" | "duplicate" | "other";
  detail: string | null;
  status: "pending" | "resolved" | "dismissed";
  created_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  has_more: boolean;
  next_cursor: string | null;
}

export interface VoteMutationResult {
  status: "created" | "removed" | "changed";
  viewer_vote: ViewerVote;
  upvotes: number;
  downvotes: number;
  score: number;
}

export interface RegistryModel {
  slug: string;
  display_name: string;
  provider: string;
}

export interface RegistryRuntime {
  slug: string;
  display_name: string;
}

export interface RegistryResponse {
  models: RegistryModel[];
  runtimes: RegistryRuntime[];
}
