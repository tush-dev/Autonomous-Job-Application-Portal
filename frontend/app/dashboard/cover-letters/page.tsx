"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { FileText, Loader2, Trash2, Copy, CheckCircle2, Sparkles, Eye } from "lucide-react";
import { apiClient } from "@/lib/api-client";

interface CoverLetterItem {
  id: string;
  application_id: string;
  content: string;
  tone: string;
  word_count: number;
  ai_generated: boolean;
  user_edited: boolean;
  version: number;
  job_title?: string;
  company_name?: string;
  created_at: string;
  updated_at: string | null;
}

export default function CoverLettersPage() {
  const [letters, setLetters] = useState<CoverLetterItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [previewId, setPreviewId] = useState<string | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  useEffect(() => {
    fetchCoverLetters();
  }, []);

  async function fetchCoverLetters() {
    try {
      const res = await apiClient.get("/cover-letters");
      setLetters(res.data);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  }

  async function deleteCoverLetter(id: string) {
    try {
      await apiClient.delete(`/cover-letters/${id}`);
      setLetters((prev) => prev.filter((l) => l.id !== id));
    } catch {
      // ignore
    }
  }

  async function copyContent(id: string, content: string) {
    try {
      await navigator.clipboard.writeText(content);
      setCopiedId(id);
      setTimeout(() => setCopiedId(null), 2000);
    } catch {
      // ignore
    }
  }

  const previewLetter = letters.find((l) => l.id === previewId);

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Cover Letters</h1>
        <p className="mt-1 text-muted-foreground">View and manage your AI-generated cover letters</p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      ) : letters.length === 0 ? (
        <div className="rounded-xl border py-16 text-center">
          <FileText className="mx-auto h-12 w-12 text-muted-foreground/50" />
          <p className="mt-4 text-lg font-medium">No cover letters yet</p>
          <p className="text-sm text-muted-foreground">
            Generate cover letters from your applications to see them here
          </p>
        </div>
      ) : (
        <div className="grid gap-4 lg:grid-cols-2">
          {letters.map((letter, i) => (
            <motion.div
              key={letter.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.03 }}
              className="rounded-xl border bg-background p-5"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <Sparkles className="h-4 w-4 text-primary shrink-0" />
                    <h3 className="font-semibold truncate">
                      {letter.job_title || "Untitled Position"}
                    </h3>
                  </div>
                  {letter.company_name && (
                    <p className="mt-0.5 text-sm text-muted-foreground">{letter.company_name}</p>
                  )}
                </div>
                <span className="inline-flex items-center gap-1 rounded-full bg-primary/10 px-2.5 py-0.5 text-xs font-medium text-primary shrink-0">
                  {letter.tone}
                </span>
              </div>

              <div className="mt-3 flex items-center gap-3 text-xs text-muted-foreground">
                <span>{letter.word_count} words</span>
                <span>v{letter.version}</span>
                {letter.ai_generated && <span className="text-primary">AI-generated</span>}
                <span className="ml-auto">
                  {new Date(letter.created_at).toLocaleDateString()}
                </span>
              </div>

              <p className="mt-3 line-clamp-3 text-sm text-muted-foreground">
                {letter.content}
              </p>

              <div className="mt-4 flex items-center gap-2">
                <button
                  onClick={() => setPreviewId(letter.id)}
                  className="inline-flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-medium hover:bg-accent transition-colors"
                >
                  <Eye className="h-3.5 w-3.5" />
                  Preview
                </button>
                <button
                  onClick={() => copyContent(letter.id, letter.content)}
                  className="inline-flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-medium hover:bg-accent transition-colors"
                >
                  {copiedId === letter.id ? (
                    <CheckCircle2 className="h-3.5 w-3.5 text-green-500" />
                  ) : (
                    <Copy className="h-3.5 w-3.5" />
                  )}
                  {copiedId === letter.id ? "Copied!" : "Copy"}
                </button>
                <button
                  onClick={() => deleteCoverLetter(letter.id)}
                  className="ml-auto inline-flex items-center gap-1.5 rounded-lg border border-red-200 px-3 py-1.5 text-xs font-medium text-red-600 hover:bg-red-50 transition-colors"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                  Delete
                </button>
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {previewLetter && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" onClick={() => setPreviewId(null)}>
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="relative max-h-[80vh] w-full max-w-2xl overflow-y-auto rounded-2xl bg-background p-8 shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold">{previewLetter.job_title || "Cover Letter"}</h2>
                {previewLetter.company_name && (
                  <p className="text-sm text-muted-foreground">{previewLetter.company_name}</p>
                )}
              </div>
              <button
                onClick={() => setPreviewId(null)}
                className="rounded-lg border px-3 py-1.5 text-xs font-medium hover:bg-accent"
              >
                Close
              </button>
            </div>
            <div className="prose prose-sm max-w-none whitespace-pre-wrap text-sm leading-relaxed">
              {previewLetter.content}
            </div>
          </motion.div>
        </div>
      )}
    </motion.div>
  );
}
