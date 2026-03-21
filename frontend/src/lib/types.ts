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

export interface QuestionListBase {
  id: string;
  title: string;
  author: AuthorSummary;
  community_id: string | null;
  status: "open" | "answered" | "resolved";
  frontier_score: number;
  created_via: "manual" | "autonomous";
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
  created_via: "manual" | "autonomous";
  created_at: string;
}

export interface AnswerInQuestion {
  id: string;
  body: string;
  author: AuthorSummary;
  frontier_score: number;
  created_via: "manual" | "autonomous";
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
  link_type: "references" | "extends" | "contradicts";
  reason: string | null;
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
  created_via: "manual" | "autonomous";
  created_at: string;
}

export interface PreviewAnswer {
  id: string;
  body: string;
  author: AuthorSummary;
  frontier_score: number;
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
  frontier_score: number;
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

// --- Analytics ---

export interface GraphNode {
  id: string;
  type: "question" | "answer" | "comment";
  title: string | null;
  body_preview: string;
  score: number;
  answer_count: number | null;
  link_count: number;
  status: "open" | "answered" | "resolved" | null;
  author_id: string;
  author_name: string;
  model_slug: string | null;
  question_id: string | null;
  answer_id: string | null;
  verdict: string | null;
  created_at: string;
  community_id: string | null;
}

export interface GraphEdge {
  source: string;
  target: string;
  edge_type: "structural" | "extends" | "contradicts" | "references";
  created_by: string | null;
  created_at: string;
}

export interface GraphAgent {
  id: string;
  display_name: string;
  model_slug: string | null;
  kind: "agent" | "human";
}

export interface GraphCommunity {
  id: string;
  name: string;
}

export interface GraphResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
  agents: GraphAgent[];
  communities: GraphCommunity[];
}

export interface SpawnedFrom {
  answer_id: string;
  question_title: string;
}

export interface FrontierQuestion {
  id: string;
  title: string;
  answer_count: number;
  link_count: number;
  spawned_from: SpawnedFrom | null;
  created_at: string;
}

export interface ActiveDebate {
  question_id: string;
  question_title: string;
  contradicts_count: number;
  involved_agents: string[];
}

export interface IsolatedQuestion {
  id: string;
  title: string;
  answer_count: number;
  created_at: string;
}

export interface FrontierResponse {
  frontier_questions: FrontierQuestion[];
  active_debates: ActiveDebate[];
  isolated_questions: IsolatedQuestion[];
}

export type FrontierStatus = "frontier" | "debated" | "resolved" | "explored" | "isolated";

export interface GraphFilterState {
  showFrontier: boolean;
  showDebated: boolean;
  showResolved: boolean;
  showExplored: boolean;
  showIsolated: boolean;
  showExtends: boolean;
  showContradicts: boolean;
  showReferences: boolean;
  view: "overview" | "community";
  selectedCommunityId: string | null;
  selectedNodeId: string | null;
}

export const DEFAULT_FILTERS: GraphFilterState = {
  showFrontier: true,
  showDebated: true,
  showResolved: true,
  showExplored: true,
  showIsolated: true,
  showExtends: true,
  showContradicts: true,
  showReferences: true,
  view: "overview",
  selectedCommunityId: null,
  selectedNodeId: null,
};

export interface ResearchStats {
  links_created: number;
  links_by_type: Record<string, number>;
  progeny_count: number;
}

// --- Ratings ---

export interface RatingCreate {
  target_type: "question" | "answer" | "comment";
  target_id: string;
  rigour: number;
  novelty: number;
  generativity: number;
  reasoning?: string;
}

export interface RatingResponse {
  id: string;
  rater_id: string;
  rater_name: string;
  target_type: string;
  target_id: string;
  rigour: number;
  novelty: number;
  generativity: number;
  is_human: boolean;
  created_at: string;
}

export interface RatingConsensus {
  rigour: number;
  novelty: number;
  generativity: number;
}

export interface RatingsForItem {
  ratings: RatingResponse[];
  consensus: RatingConsensus;
  human_rating: RatingResponse | null;
  frontier_score: number;
}
