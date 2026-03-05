"use client";

import { useState } from "react";
import { comments as commentsApi, ApiError } from "@/lib/api";

interface CommentFormProps {
  targetType: "question" | "answer";
  targetId: string;
  parentId?: string;
  onSubmitted: () => void;
}

export function CommentForm({ targetType, targetId, parentId, onSubmitted }: CommentFormProps) {
  const [body, setBody] = useState("");
  const [open, setOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="mt-2 text-xs text-xtext-secondary hover:text-xtext-primary"
      >
        Add a comment
      </button>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      if (targetType === "question") {
        await commentsApi.onQuestion(targetId, body, parentId);
      } else {
        await commentsApi.onAnswer(targetId, body, { parent_id: parentId });
      }
      setBody("");
      setOpen(false);
      onSubmitted();
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Failed to post comment");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="mt-2">
      {error && <p className="mb-1 text-xs text-xdanger">{error}</p>}
      <textarea
        value={body}
        onChange={(e) => setBody(e.target.value)}
        placeholder="Add a comment\u2026"
        required
        rows={2}
        className="w-full rounded border border-xborder bg-xbg-secondary px-2 py-1 text-sm text-xtext-primary focus:border-xaccent focus:outline-none"
      />
      <div className="mt-1 flex gap-2">
        <button
          type="submit"
          disabled={submitting}
          className="text-xs font-medium text-xaccent hover:text-xaccent"
        >
          {submitting ? "Posting\u2026" : "Comment"}
        </button>
        <button
          type="button"
          onClick={() => setOpen(false)}
          className="text-xs text-gray-400 hover:text-gray-600"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}
