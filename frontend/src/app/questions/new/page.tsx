"use client";

import { useState } from "react";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { communities as communitiesApi, questions as questionsApi, ApiError } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import type { Community } from "@/lib/types";

export default function NewQuestionPage() {
  const router = useRouter();
  const { user, loading } = useAuth();
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [communityId, setCommunityId] = useState("");
  const [communities, setCommunities] = useState<Community[]>([]);
  const [communityLoadError, setCommunityLoadError] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (loading || !user) return;
    communitiesApi
      .list()
      .then((res) => {
        setCommunities(res.items);
        setCommunityLoadError(null);
      })
      .catch((err) => {
        if (err instanceof ApiError) {
          setCommunityLoadError(err.detail || "Failed to load communities.");
        } else {
          setCommunityLoadError("Network error while loading communities.");
        }
      });
  }, [loading, user]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const q = await questionsApi.create(title, body, communityId || undefined);
      router.push(`/questions/${q.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Failed to post question");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="mx-auto max-w-2xl py-6">
      <h1 className="mb-6 text-2xl font-bold">Ask a Question</h1>
      {error && <p className="mb-4 text-sm text-xdanger">{error}</p>}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="title" className="mb-1 block text-sm font-medium">
            Title
          </label>
          <input
            id="title"
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="What's your question?"
            required
            maxLength={300}
            className="w-full rounded border border-xborder bg-xbg-secondary px-3 py-2 text-sm text-xtext-primary focus:border-xaccent focus:outline-none"
          />
        </div>
        <div>
          <label htmlFor="community" className="mb-1 block text-sm font-medium">
            Community (optional)
          </label>
          <select
            id="community"
            value={communityId}
            onChange={(e) => setCommunityId(e.target.value)}
            className="w-full rounded border border-xborder bg-xbg-secondary px-3 py-2 text-sm text-xtext-primary focus:border-xaccent focus:outline-none"
          >
            <option value="">No community</option>
            {communities.map((community) => (
              <option key={community.id} value={community.id}>
                {community.display_name}
              </option>
            ))}
          </select>
          {communityLoadError && <p className="mt-1 text-xs text-xdanger">{communityLoadError}</p>}
        </div>
        <div>
          <label htmlFor="body" className="mb-1 block text-sm font-medium">
            Body
          </label>
          <textarea
            id="body"
            value={body}
            onChange={(e) => setBody(e.target.value)}
            placeholder="Provide details, context, and what you've tried\u2026"
            required
            rows={10}
            className="w-full rounded border border-xborder bg-xbg-secondary px-3 py-2 text-sm text-xtext-primary focus:border-xaccent focus:outline-none"
          />
        </div>
        <button
          type="submit"
          disabled={submitting}
          className="rounded bg-xaccent px-6 py-2 text-sm font-medium text-white hover:bg-xaccent-hover disabled:opacity-50"
        >
          {submitting ? "Posting\u2026" : "Post Question"}
        </button>
      </form>
    </div>
  );
}
