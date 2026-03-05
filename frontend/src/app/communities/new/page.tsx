"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { communities as communitiesApi, ApiError } from "@/lib/api";

export default function NewCommunityPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const c = await communitiesApi.create(name, displayName, description);
      router.push(`/communities/${c.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Failed to create community");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="mx-auto max-w-lg py-6">
      <h1 className="mb-6 text-2xl font-bold">Create Community</h1>
      {error && <p className="mb-4 text-sm text-xdanger">{error}</p>}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="name" className="mb-1 block text-sm font-medium">
            Slug
          </label>
          <input
            id="name"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, "-"))}
            placeholder="machine-learning"
            required
            className="w-full rounded border border-xborder bg-xbg-secondary px-3 py-2 text-sm text-xtext-primary focus:border-xaccent focus:outline-none"
          />
          <p className="mt-1 text-xs text-xtext-secondary">Lowercase, hyphens only</p>
        </div>
        <div>
          <label htmlFor="displayName" className="mb-1 block text-sm font-medium">
            Display Name
          </label>
          <input
            id="displayName"
            type="text"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            placeholder="Machine Learning"
            required
            className="w-full rounded border border-xborder bg-xbg-secondary px-3 py-2 text-sm text-xtext-primary focus:border-xaccent focus:outline-none"
          />
        </div>
        <div>
          <label htmlFor="description" className="mb-1 block text-sm font-medium">
            Description
          </label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="What is this community about?"
            required
            rows={3}
            className="w-full rounded border border-xborder bg-xbg-secondary px-3 py-2 text-sm text-xtext-primary focus:border-xaccent focus:outline-none"
          />
        </div>
        <button
          type="submit"
          disabled={submitting}
          className="rounded bg-xaccent px-6 py-2 text-sm font-medium text-white hover:bg-xaccent-hover disabled:opacity-50"
        >
          {submitting ? "Creating\u2026" : "Create Community"}
        </button>
      </form>
    </div>
  );
}
