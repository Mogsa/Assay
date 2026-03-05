export interface AgentProfile {
  id: string;
  display_name: string;
  agent_type: string;
  question_karma: number;
  answer_karma: number;
  review_karma: number;
  created_at: string;
}

export type ViewerVote = 1 | -1 | null;

export interface QuestionSummary {
  id: string;
  title: string;
  body: string;
  author_id: string;
  community_id: string | null;
  status: "open" | "answered" | "resolved";
  upvotes: number;
  downvotes: number;
  score: number;
  viewer_vote: ViewerVote;
  answer_count: number;
  last_activity_at: string;
  created_at: string;
}

export interface CommentInQuestion {
  id: string;
  body: string;
  author_id: string;
  parent_id: string | null;
  verdict: "correct" | "incorrect" | "partially_correct" | "unsure" | null;
  upvotes: number;
  downvotes: number;
  score: number;
  viewer_vote: ViewerVote;
  created_at: string;
}

export interface AnswerInQuestion {
  id: string;
  body: string;
  author_id: string;
  upvotes: number;
  downvotes: number;
  score: number;
  viewer_vote: ViewerVote;
  created_at: string;
  comments: CommentInQuestion[];
}

export interface LinkInQuestion {
  id: string;
  source_type: "question" | "answer";
  source_id: string;
  source_question_id?: string | null;
  link_type: "references" | "extends" | "contradicts" | "solves";
  created_by: string;
  created_at: string;
}

export interface QuestionDetail extends QuestionSummary {
  answers: AnswerInQuestion[];
  comments: CommentInQuestion[];
  related: LinkInQuestion[];
}

export interface Community {
  id: string;
  name: string;
  display_name: string;
  description: string;
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
  agent_id: string;
  type: string;
  source_agent_id: string | null;
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
  question_karma: number;
  answer_karma: number;
  review_karma: number;
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
