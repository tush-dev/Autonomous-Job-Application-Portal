"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import {
  Upload, FileText, X, CheckCircle2, AlertCircle,
  Loader2, Sparkles, Eye, Trash2, Star, Download,
  ArrowUp, ArrowRight, FileUp,
} from "lucide-react";
import { apiClient } from "@/lib/api-client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { cn, formatDate, formatFileSize } from "@/lib/utils";
import type { Resume } from "@/types/api";
import { AxiosError } from "axios";

type UploadErrorPayload = {
  detail?: string | Array<{ msg?: string; loc?: Array<string | number> }>;
  message?: string;
};

function getUploadErrorMessage(error: unknown): string {
  const apiError = error as AxiosError<UploadErrorPayload>;
  const detail = apiError.response?.data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => item?.msg)
      .filter((message): message is string => Boolean(message));
    if (messages.length) return messages.join(". ");
  }
  if (typeof apiError.response?.data?.message === "string") {
    return apiError.response.data.message;
  }
  if (apiError.code === "ECONNABORTED") {
    return "Resume processing timed out. Please try again.";
  }
  return "Resume upload failed. Please check the file and try again.";
}

function confidencePercent(value?: number | null): number {
  if (value == null || !Number.isFinite(value)) return 0;
  return Math.max(0, Math.min(100, value <= 1 ? value * 100 : value));
}

const container = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.05 } },
};

const fadeUp = {
  hidden: { opacity: 0, y: 12 },
  show: { opacity: 1, y: 0, transition: { duration: 0.35, ease: [0.25, 0.1, 0.25, 1] } },
};

export default function ResumesPage() {
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    apiClient.get("/resumes")
      .then((res) => setResumes(res.data || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const handleUpload = useCallback(async (file: File) => {
    if (!file) return;
    const extension = file.name.split(".").pop()?.toLowerCase();
    if (!extension || !["pdf", "doc", "docx"].includes(extension)) {
      setUploadError("Please select a PDF, DOC, or DOCX resume.");
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      setUploadError("The resume must be smaller than 10 MB.");
      return;
    }
    setUploading(true);
    setUploadError("");
    try {
      const form = new FormData();
      form.append("file", file);
      const res = await apiClient.post("/resumes/upload", form, {
        headers: { "Content-Type": "multipart/form-data" },
        // Resume extraction and analysis may take longer than normal API calls.
        timeout: 120000,
      });
      if (res.data.parsing_status === "failed") {
        setUploadError("The file uploaded, but its text could not be parsed. Try a text-based PDF or DOCX file.");
      }
      setResumes((prev) => [res.data, ...prev]);
    } catch (error) {
      setUploadError(getUploadErrorMessage(error));
    } finally {
      setUploading(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file && (file.type === "application/pdf" || file.name.endsWith(".docx"))) {
      handleUpload(file);
    }
  }, [handleUpload]);

  const handleDelete = async (id: string) => {
    try {
      await apiClient.delete(`/resumes/${id}`);
      setResumes((prev) => prev.filter((r) => r.id !== id));
    } catch {}
  };

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-5 pb-6 sm:space-y-8 sm:pb-12">
      {/* Header */}
      <motion.div variants={fadeUp}>
        <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">Resumes</h1>
        <p className="mt-1 text-muted-foreground">
          Upload, manage, and analyze your resumes
        </p>
      </motion.div>

      {/* Drop zone */}
      <motion.div variants={fadeUp}>
        <div
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => fileRef.current?.click()}
          className={cn(
            "relative flex min-h-72 cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed px-4 py-8 text-center transition-all duration-300 sm:min-h-0 sm:p-12",
            dragOver
              ? "border-primary bg-primary/5 scale-[1.02]"
              : "border-border/50 hover:border-primary/50 hover:bg-muted/30"
          )}
        >
          <input
            ref={fileRef}
            type="file"
            accept=".pdf,.docx"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) handleUpload(file);
              e.target.value = "";
            }}
          />

          {uploading ? (
            <div className="text-center">
              <div className="relative mx-auto flex h-16 w-16 items-center justify-center">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
              </div>
              <p className="mt-4 font-medium">Uploading...</p>
              <p className="text-sm text-muted-foreground">Parsing your resume with AI</p>
              <Progress value={45} className="mx-auto mt-4 h-2 w-full max-w-64" />
            </div>
          ) : (
            <>
              <div className={cn(
                "rounded-2xl p-4 transition-all duration-300",
                dragOver ? "bg-primary/10 scale-110" : "bg-muted"
              )}>
                <FileUp className={cn("h-10 w-10", dragOver ? "text-primary" : "text-muted-foreground")} />
              </div>
              <p className="mt-4 text-lg font-semibold">
                {dragOver ? "Drop your resume here" : "Upload your resume"}
              </p>
              <p className="text-sm text-muted-foreground mt-1">
                Drag & drop or click to browse (PDF, DOCX)
              </p>
              <Button variant="outline" className="mt-4 rounded-xl gap-2" onClick={(e) => { e.stopPropagation(); fileRef.current?.click(); }}>
                <Upload className="h-4 w-4" /> Select File
              </Button>
            </>
          )}
        </div>
        {uploadError && (
          <div role="alert" className="mt-3 flex items-start gap-2 rounded-xl border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
            <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
            <span>{uploadError}</span>
          </div>
        )}
      </motion.div>

      {/* Resume list */}
      {loading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-44 rounded-2xl" />
          ))}
        </div>
      ) : resumes.length === 0 ? (
        <motion.div variants={fadeUp}>
          <Card>
            <CardContent className="flex flex-col items-center py-16 text-center">
              <div className="rounded-2xl bg-muted p-5 mb-4">
                <FileText className="h-10 w-10 text-muted-foreground" />
              </div>
              <h3 className="text-lg font-semibold">No resumes yet</h3>
              <p className="text-sm text-muted-foreground mt-1 max-w-sm">
                Upload your first resume to get AI-powered job matches and career insights
              </p>
            </CardContent>
          </Card>
        </motion.div>
      ) : (
        <motion.div variants={container} className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {resumes.map((resume, i) => (
            <motion.div key={resume.id} variants={fadeUp}>
              <Link href={`/dashboard/resumes/${resume.id}`}>
                <Card className="group hover:border-primary/30 transition-all duration-300 h-full">
                  <CardContent className="p-4 sm:p-5">
                    <div className="flex items-start justify-between">
                      <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-primary/20 to-purple-500/20">
                        <FileText className="h-6 w-6 text-primary" />
                      </div>
                      <div className="flex items-center gap-1">
                        {resume.is_active && (
                          <Star className="h-4 w-4 text-amber-400 fill-amber-400" />
                        )}
                        <button
                          onClick={(e) => { e.preventDefault(); handleDelete(resume.id); }}
                          className="rounded-lg p-2 text-muted-foreground transition-colors hover:bg-destructive/10 hover:text-destructive sm:opacity-0 sm:group-hover:opacity-100"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </button>
                      </div>
                    </div>

                    <div className="mt-4">
                      <p className="font-semibold truncate">{resume.file_name}</p>
                      <div className="mt-1 flex items-center gap-2 text-xs text-muted-foreground">
                        <span>{formatFileSize(resume.file_size)}</span>
                        <span>•</span>
                        <span>{formatDate(resume.created_at)}</span>
                      </div>
                    </div>

                    <div className="mt-4 flex items-center gap-2">
                      {resume.parsing_status === "completed" ? (
                        <Badge variant="success" className="text-[10px] gap-1">
                          <CheckCircle2 className="h-3 w-3" /> Parsed
                        </Badge>
                      ) : resume.parsing_status === "failed" ? (
                        <Badge variant="destructive" className="text-[10px] gap-1">
                          <AlertCircle className="h-3 w-3" /> Failed
                        </Badge>
                      ) : (
                        <Badge variant="outline" className="text-[10px] gap-1">
                          <Loader2 className="h-3 w-3 animate-spin" /> Processing
                        </Badge>
                      )}

                      {resume.parsing_confidence != null && (
                        <span className="text-[10px] text-muted-foreground">
                          {confidencePercent(resume.parsing_confidence).toFixed(0)}% confidence
                        </span>
                      )}
                    </div>

                    {resume.parsing_confidence != null && (
                      <Progress value={confidencePercent(resume.parsing_confidence)} className="mt-3 h-1" />
                    )}
                  </CardContent>
                </Card>
              </Link>
            </motion.div>
          ))}
        </motion.div>
      )}
    </motion.div>
  );
}
