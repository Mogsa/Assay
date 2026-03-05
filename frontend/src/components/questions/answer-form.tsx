"use client";

import { useState } from "react";
import { answers, ApiError } from "@/lib/api";

interface AnswerFormProps {
  questionId: string;
  onSubmitted: () => void;
}

export function AnswerForm({ questionId, onSubmitted }: AnswerFormProps) {
  const [body, setBody] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await answers.create(questionId, body);
      setBody("");
      onSubmitted();
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Failed to post answer");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="mt-6">
      <h3 className="mb-2 text-lg font-semibold">Your Answer</h3>
      {error && <p className="mb-2 text-sm text-red-500">{error}</p>}
      <textarea
        value={body}
        onChange={(e) => setBody(e.target.value)}
        placeholder="Write your answer\u2026"
        required
        rows={6}
        className="w-full rounded border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
      />
      <button
        type="submit"
        disabled={submitting}
        className="mt-2 rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-500 disabled:opacity-50"
      >
        {submitting ? "Posting\u2026" : "Post Answer"}
      </button>
    </form>
  );
}
