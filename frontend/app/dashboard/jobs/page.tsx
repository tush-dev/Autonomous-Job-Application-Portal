"use client";

import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import {
  Search, MapPin, Briefcase, ExternalLink, Loader2, Sparkles,
  ChevronDown, ChevronUp, Building2, Clock, DollarSign, Zap,
  Bookmark, BookmarkCheck, GraduationCap, Filter, SlidersHorizontal,
  Globe, ArrowUpDown,
} from "lucide-react";
import { apiClient } from "@/lib/api-client";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn, formatSalary, timeAgo } from "@/lib/utils";
import type { Job } from "@/types/api";
import { toast } from "sonner";

const container = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.04 } },
};

const fadeUp = {
  hidden: { opacity: 0, y: 12 },
  show: { opacity: 1, y: 0, transition: { duration: 0.35, ease: [0.25, 0.1, 0.25, 1] } },
};

export default function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [searching, setSearching] = useState(false);
  const [query, setQuery] = useState("");
  const [location, setLocation] = useState("");
  const [remote, setRemote] = useState("");
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalJobs, setTotalJobs] = useState(0);
  const [sortBy, setSortBy] = useState<"match" | "recent">("match");
  const [minMatchScore, setMinMatchScore] = useState(0);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [savedIds, setSavedIds] = useState<Set<string>>(new Set());
  const [hasResume, setHasResume] = useState<boolean | null>(null);

  useEffect(() => {
    apiClient.get("/resumes/count")
      .then((res) => {
        const available = (res.data?.count ?? 0) > 0;
        setHasResume(available);
        if (!available) setSortBy("recent");
      })
      .catch(() => setHasResume(null));
  }, []);

  const searchJobs = useCallback(async (p = 1) => {
    setSearching(true);
    try {
      const res = await apiClient.post("/jobs/search", {
        query,
        location: location || null,
        remote: remote || null,
        page: p,
        page_size: 12,
        min_match_score: minMatchScore > 0 ? minMatchScore : null,
        sort_by: sortBy,
      });
      setJobs(res.data.jobs || []);
      setTotalPages(res.data.total_pages || 1);
      setTotalJobs(res.data.total || 0);
      setPage(p);
    } catch (error: any) {
      const message = error?.response?.data?.error?.message || error?.response?.data?.detail || "Could not load jobs. Please try again.";
      toast.error(message);
    } finally {
      setSearching(false);
      setLoading(false);
    }
  }, [query, location, remote, minMatchScore, sortBy]);

  useEffect(() => { searchJobs(1); }, [searchJobs]);

  const toggleSave = async (jobId: string) => {
    try {
      if (savedIds.has(jobId)) {
        await apiClient.delete(`/jobs/${jobId}/save`);
        setSavedIds((p) => { const n = new Set(p); n.delete(jobId); return n; });
      } else {
        await apiClient.post(`/jobs/${jobId}/save`);
        setSavedIds((p) => { const n = new Set(p); n.add(jobId); return n; });
      }
    } catch {}
  };

  const firstVisiblePage = Math.max(1, Math.min(page - 2, totalPages - 4));
  const visiblePages = Array.from(
    { length: Math.min(totalPages, 5) },
    (_, index) => firstVisiblePage + index
  );

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-4 pb-6 sm:space-y-6 sm:pb-12">
      {/* Header */}
      <motion.div variants={fadeUp}>
        <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">Job Search</h1>
        <p className="mt-1 text-muted-foreground">
          AI-powered job matching based on your resume
        </p>
      </motion.div>

      {/* Search bar */}
      <motion.div variants={fadeUp}>
        <Card className="border-border/30">
          <CardContent className="p-3 sm:p-4">
            <div className="grid grid-cols-2 gap-2.5 sm:flex sm:flex-wrap sm:gap-3">
              <div className="relative col-span-2 min-w-0 sm:flex-1 sm:min-w-[200px]">
                <Search className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search jobs, skills, companies..."
                  className="pl-10 h-11 rounded-xl bg-muted/30 border-0 ring-1 ring-border/50 focus-visible:ring-primary"
                />
              </div>
              <div className="relative min-w-0 sm:w-36">
                <MapPin className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="Location"
                  className="pl-10 h-11 rounded-xl bg-muted/30 border-0 ring-1 ring-border/50 focus-visible:ring-primary"
                />
              </div>
              <select
                value={remote}
                onChange={(e) => setRemote(e.target.value)}
                className="h-11 min-w-0 rounded-xl bg-muted/30 border-0 ring-1 ring-border/50 focus-visible:ring-primary px-3 text-sm text-muted-foreground focus:outline-none"
              >
                <option value="">Any type</option>
                <option value="remote">Remote</option>
                <option value="hybrid">Hybrid</option>
                <option value="onsite">On-site</option>
              </select>
              <Button
                onClick={() => searchJobs(1)}
                disabled={searching}
                className="col-span-2 h-11 w-full rounded-xl px-6 gap-2 sm:w-auto"
              >
                {searching ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
                Search
              </Button>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Filters bar */}
      <motion.div variants={fadeUp} className="flex flex-col items-stretch gap-3 sm:flex-row sm:flex-wrap sm:items-center sm:justify-between">
        <div className="flex items-center justify-between gap-2 sm:justify-start">
          <SlidersHorizontal className="h-4 w-4 text-muted-foreground" />
          <select
            value={minMatchScore}
            onChange={(e) => { setMinMatchScore(Number(e.target.value)); setPage(1); }}
            className="h-9 rounded-xl bg-muted/30 border-0 ring-1 ring-border/50 px-3 text-xs text-muted-foreground focus:outline-none"
          >
            <option value={0}>Any match</option>
            <option value={20}>20%+ match</option>
            <option value={40}>40%+ match</option>
            <option value={60}>60%+ match</option>
            <option value={80}>80%+ match</option>
          </select>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-muted-foreground">
            {totalJobs} {totalJobs === 1 ? "job" : "jobs"} found
          </span>
          <Separator orientation="vertical" className="h-4" />
          <Button
            variant={sortBy === "match" ? "default" : "ghost"}
            size="sm"
            onClick={() => {
              if (hasResume === false) {
                toast.error("Upload a parsed resume to see matched jobs.");
                return;
              }
              setSortBy("match");
            }}
            disabled={hasResume === false}
            className="rounded-lg text-xs h-8 gap-1.5"
          >
            <Sparkles className="h-3 w-3" /> Match
          </Button>
          <Button
            variant={sortBy === "recent" ? "default" : "ghost"}
            size="sm"
            onClick={() => setSortBy("recent")}
            className="rounded-lg text-xs h-8 gap-1.5"
          >
            <Clock className="h-3 w-3" /> Recent
          </Button>
        </div>
      </motion.div>

      {/* Job cards */}
      {loading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-2">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-52 rounded-2xl" />
          ))}
        </div>
      ) : jobs.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-16 text-center">
            <div className="rounded-2xl bg-muted p-5 mb-4">
              <Briefcase className="h-10 w-10 text-muted-foreground" />
            </div>
            <h3 className="text-lg font-semibold">No jobs found</h3>
            <p className="text-sm text-muted-foreground mt-1 max-w-sm">
              {minMatchScore > 0
                ? `No jobs match your ${minMatchScore}%+ filter. Try lowering the threshold or upload a resume to get better matches.`
                : "Try adjusting your search or filters to find more opportunities."}
            </p>
            {minMatchScore > 0 && (
              <Button variant="outline" className="mt-4" onClick={() => setMinMatchScore(0)}>
                Clear filter
              </Button>
            )}
          </CardContent>
        </Card>
      ) : (
        <motion.div variants={container} className="grid gap-4 md:grid-cols-2 lg:grid-cols-2">
          {jobs.map((job, i) => {
            const match = job.match;
            const score = match?.match_score ?? 0;
            const isExpanded = expandedId === job.id;
            return (
              <motion.div key={job.id} variants={fadeUp}>
                <Card
                  className={cn(
                    "group relative overflow-hidden transition-all duration-300 cursor-pointer",
                    isExpanded ? "border-primary/30" : "hover:border-border/80"
                  )}
                  onClick={() => setExpandedId(isExpanded ? null : job.id)}
                >
                  {/* Match score gradient bar */}
                  {match && (
                    <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-primary/30 to-transparent" />
                  )}

                  <CardContent className="p-4 sm:p-5">
                    <div className="flex items-start gap-3 sm:gap-4">
                      {/* Company logo placeholder */}
                      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-primary/10 to-purple-500/10 sm:h-12 sm:w-12">
                        <Building2 className="h-5 w-5 text-primary sm:h-6 sm:w-6" />
                      </div>

                      <div className="flex-1 min-w-0">
                        {/* Title row */}
                        <div className="flex items-start justify-between gap-2">
                          <div>
                            <h3 className="font-semibold truncate">{job.title}</h3>
                            <p className="text-sm text-muted-foreground">
                              {job.company?.name || "Unknown"}
                            </p>
                          </div>
                          <div className="flex items-center gap-1 shrink-0">
                            {match && (
                              <div className={cn(
                                "flex flex-col items-center rounded-xl px-2.5 py-1.5",
                                score >= 60 ? "bg-emerald-500/10" : score >= 30 ? "bg-amber-500/10" : "bg-muted"
                              )}>
                                <span className={cn(
                                  "text-sm font-bold leading-none",
                                  score >= 60 ? "text-emerald-400" : score >= 30 ? "text-amber-400" : "text-muted-foreground"
                                )}>
                                  {score.toFixed(0)}%
                                </span>
                                <span className="text-[9px] text-muted-foreground">match</span>
                              </div>
                            )}
                            <button
                              onClick={(e) => { e.stopPropagation(); toggleSave(job.id); }}
                              className="rounded-lg p-1.5 hover:bg-muted transition-colors"
                            >
                              {savedIds.has(job.id) ? (
                                <BookmarkCheck className="h-4 w-4 text-primary" />
                              ) : (
                                <Bookmark className="h-4 w-4 text-muted-foreground" />
                              )}
                            </button>
                          </div>
                        </div>

                        {/* Meta row */}
                        <div className="mt-2 flex flex-wrap gap-x-3 gap-y-1 text-xs text-muted-foreground">
                          {job.location && (
                            <span className="inline-flex items-center gap-1">
                              <MapPin className="h-3 w-3" /> {job.location}
                            </span>
                          )}
                          <span className="inline-flex items-center gap-1 capitalize">
                            <Globe className="h-3 w-3" /> {job.remote}
                          </span>
                          {job.salary_min && (
                            <span className="inline-flex items-center gap-1">
                              <DollarSign className="h-3 w-3" /> {formatSalary(job.salary_min, job.salary_max)}
                            </span>
                          )}
                        </div>

                        {/* Skills badges */}
                        {match && (
                          <div className="mt-3 flex flex-wrap gap-1.5">
                            {match.skills_matched.slice(0, 3).map((s) => (
                              <Badge key={s} variant="success" className="text-[10px] px-1.5 py-0">
                                {s}
                              </Badge>
                            ))}
                            {match.missing_skills.length > 0 && (
                              <Badge variant="destructive" className="text-[10px] px-1.5 py-0">
                                -{match.missing_skills.slice(0, 2).join(", ")}
                                {match.missing_skills.length > 2 && ` +${match.missing_skills.length - 2}`}
                              </Badge>
                            )}
                          </div>
                        )}

                        {/* Expanded analysis */}
                        {isExpanded && match && (
                          <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: "auto", opacity: 1 }}
                            className="mt-4 pt-4 border-t border-border/30 space-y-3"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <div className="grid grid-cols-3 gap-3">
                              <div className="rounded-xl bg-muted/50 p-3 text-center">
                                <p className="text-xs text-muted-foreground">ATS</p>
                                <p className="text-lg font-bold text-blue-400">
                                  {match.ats_compatibility?.toFixed(0) ?? "—"}%
                                </p>
                              </div>
                              <div className="rounded-xl bg-muted/50 p-3 text-center">
                                <p className="text-xs text-muted-foreground">Interview</p>
                                <p className="text-lg font-bold text-emerald-400">
                                  {match.interview_probability?.toFixed(0) ?? "—"}%
                                </p>
                              </div>
                              <div className="rounded-xl bg-muted/50 p-3 text-center">
                                <p className="text-xs text-muted-foreground">Growth</p>
                                <p className="text-lg font-bold text-purple-400">
                                  {match.match_score.toFixed(0)}%
                                </p>
                              </div>
                            </div>

                            {match.missing_skills.length > 0 && (
                              <div className="flex items-start gap-2 text-xs text-muted-foreground">
                                <GraduationCap className="h-3.5 w-3.5 mt-0.5 shrink-0" />
                                <span>Learn: {match.missing_skills.slice(0, 4).join(", ")}</span>
                              </div>
                            )}

                            {match.reasoning && (
                              <div className="rounded-xl bg-primary/5 p-3 text-xs text-muted-foreground italic leading-relaxed">
                                <Sparkles className="h-3 w-3 inline mr-1 text-primary" />
                                {match.reasoning}
                              </div>
                            )}

                            <div className="flex gap-2 pt-1">
                              <Button
                                size="sm"
                                className="rounded-xl h-9 text-xs flex-1 gap-1.5"
                                onClick={() => window.open(job.application_url || "#", "_blank")}
                              >
                                <ExternalLink className="h-3 w-3" /> Apply
                              </Button>
                              <Button
                                variant="outline"
                                size="sm"
                                className="rounded-xl h-9 text-xs gap-1.5"
                              >
                                <Zap className="h-3 w-3" /> Tailor Resume
                              </Button>
                            </div>
                          </motion.div>
                        )}

                        {/* Bottom indicator */}
                        <div className="mt-3 flex items-center justify-between">
                          <span className="text-[11px] text-muted-foreground">
                            {job.posted_at && timeAgo
                              ? timeAgo(job.posted_at)
                              : "Recently posted"}
                          </span>
                          <div className="flex items-center gap-2">
                            {job.application_url && (
                              <Button
                                size="sm"
                                className="h-8 rounded-lg px-3 text-[11px] font-semibold"
                                onClick={(event) => {
                                  event.stopPropagation();
                                  window.open(job.application_url, "_blank", "noopener,noreferrer");
                                }}
                              >
                                Apply now <ExternalLink className="ml-1.5 h-3 w-3" />
                              </Button>
                            )}
                            {match && (
                            <button
                              className="flex items-center gap-1 text-[11px] text-muted-foreground hover:text-foreground transition-colors"
                            >
                              {isExpanded ? (
                                <><ChevronUp className="h-3 w-3" /> Less</>
                              ) : (
                                <><ChevronDown className="h-3 w-3" /> AI Analysis</>
                              )}
                            </button>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            );
          })}
        </motion.div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <motion.div variants={fadeUp} className="flex items-center justify-center gap-3 pt-2">
          <Button
            variant="outline"
            size="sm"
            disabled={page <= 1}
            onClick={() => {
              searchJobs(page - 1);
              window.scrollTo({ top: 0, behavior: "smooth" });
            }}
            className="rounded-xl"
          >
            Previous
          </Button>
          <div className="flex items-center gap-1.5">
            {visiblePages.map((p) => {
              return (
                <Button
                  key={p}
                  variant={p === page ? "default" : "ghost"}
                  size="sm"
                  className="rounded-lg h-8 w-8 p-0 text-xs"
                  onClick={() => {
                    searchJobs(p);
                    window.scrollTo({ top: 0, behavior: "smooth" });
                  }}
                >
                  {p}
                </Button>
              );
            })}
          </div>
          <Button
            variant="outline"
            size="sm"
            disabled={page >= totalPages}
            onClick={() => {
              searchJobs(page + 1);
              window.scrollTo({ top: 0, behavior: "smooth" });
            }}
            className="rounded-xl"
          >
            Next
          </Button>
        </motion.div>
      )}
    </motion.div>
  );
}
