"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  Brain, TrendingUp, Target, Star, Lightbulb, AlertCircle,
  CheckCircle2, FileText, Sparkles, ArrowUpRight,
  BookOpen, BarChart3, Zap, Shield,
} from "lucide-react";
import { apiClient } from "@/lib/api-client";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";
import type { CareerInsightsData } from "@/types/api";

const container = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.05 } },
};

const fadeUp = {
  hidden: { opacity: 0, y: 12 },
  show: { opacity: 1, y: 0, transition: { duration: 0.35, ease: [0.25, 0.1, 0.25, 1] } },
};

const scoreConfig: Record<string, { label: string; color: string; icon: React.ElementType }> = {
  resume_health_score: { label: "Resume Health", color: "text-emerald-400", icon: Shield },
  ats_score: { label: "ATS Compatibility", color: "text-blue-400", icon: FileText },
  technical_strength: { label: "Technical Strength", color: "text-purple-400", icon: Zap },
  communication_score: { label: "Communication", color: "text-amber-400", icon: TrendingUp },
  leadership_score: { label: "Leadership", color: "text-rose-400", icon: Star },
  project_quality: { label: "Project Quality", color: "text-cyan-400", icon: Target },
  skill_coverage: { label: "Skill Coverage", color: "text-indigo-400", icon: BarChart3 },
  completeness: { label: "Completeness", color: "text-emerald-400", icon: CheckCircle2 },
  readability: { label: "Readability", color: "text-orange-400", icon: BookOpen },
};

export default function InsightsPage() {
  const [data, setData] = useState<CareerInsightsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient
      .get("/matching/insights")
      .then((res) => setData(res.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-12 w-64 rounded-xl" />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-28 rounded-2xl" />
          ))}
        </div>
        <Skeleton className="h-96 rounded-2xl" />
      </div>
    );
  }

  const insights = data;

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-8 pb-12">
      {/* Header */}
      <motion.div variants={fadeUp}>
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-purple-500/20 to-primary/20">
            <Brain className="h-5 w-5 text-purple-400" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Career Insights</h1>
            <p className="text-muted-foreground">
              AI-powered analysis of your resume and career trajectory
            </p>
          </div>
        </div>
      </motion.div>

      {/* Score cards */}
      <motion.div variants={fadeUp} className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { label: "Resume Health", value: insights?.resume_health_score, color: "text-emerald-400", bg: "bg-emerald-500/10" },
          { label: "ATS Score", value: insights?.ats_score, color: "text-blue-400", bg: "bg-blue-500/10" },
          { label: "Technical Strength", value: insights?.technical_strength, color: "text-purple-400", bg: "bg-purple-500/10" },
          { label: "Career Level", value: insights?.career_level, color: "text-amber-400", bg: "bg-amber-500/10", isLabel: true },
        ].map((stat) => (
          <Card key={stat.label} className="group hover:border-primary/30 transition-all duration-300">
            <CardContent className="p-6">
              <p className="text-sm text-muted-foreground">{stat.label}</p>
              <p className={cn("mt-1 text-3xl font-bold", stat.color)}>
                {stat.isLabel ? stat.value : `${(stat.value as number)?.toFixed(0) ?? "—"}`}
                {!stat.isLabel && stat.value != null && <span className="text-lg text-muted-foreground/50">%</span>}
              </p>
            </CardContent>
          </Card>
        ))}
      </motion.div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Detailed Scores */}
        <motion.div variants={fadeUp} className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <BarChart3 className="h-4 w-4 text-primary" />
                <CardTitle className="text-lg">Detailed Scores</CardTitle>
              </div>
              <CardDescription>Breakdown of your resume across key dimensions</CardDescription>
            </CardHeader>
            <CardContent className="space-y-5">
              {Object.entries(scoreConfig).map(([key, config]) => {
                const value = (insights as any)?.[key];
                if (value == null) return null;
                const Icon = config.icon;
                return (
                  <div key={key} className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <div className="flex items-center gap-2">
                        <Icon className={cn("h-4 w-4", config.color)} />
                        <span>{config.label}</span>
                      </div>
                      <span className={cn("font-semibold", config.color)}>
                        {value.toFixed(0)}%
                      </span>
                    </div>
                    <Progress value={value} className="h-2" />
                  </div>
                );
              })}
            </CardContent>
          </Card>

          {/* AI Suggestions */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Lightbulb className="h-4 w-4 text-amber-400" />
                <CardTitle className="text-lg">AI Suggestions</CardTitle>
              </div>
              <CardDescription>Actionable improvements for your resume</CardDescription>
            </CardHeader>
            <CardContent className="space-y-5">
              {insights?.suggested_skills && insights.suggested_skills.length > 0 && (
                <div>
                  <p className="text-sm font-medium mb-2 flex items-center gap-1.5">
                    <Sparkles className="h-4 w-4 text-primary" /> Suggested Skills
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {insights.suggested_skills.map((skill) => (
                      <Badge key={skill} variant="outline" className="text-xs">
                        {skill}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {insights?.weak_bullet_points && insights.weak_bullet_points.length > 0 && (
                <div>
                  <p className="text-sm font-medium mb-2 flex items-center gap-1.5">
                    <AlertCircle className="h-4 w-4 text-amber-400" /> Weak Bullet Points
                  </p>
                  <div className="space-y-1.5">
                    {insights.weak_bullet_points.slice(0, 4).map((point, i) => (
                      <div key={i} className="rounded-lg bg-muted/50 px-3 py-2 text-xs text-muted-foreground">
                        {point}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {insights?.formatting_suggestions && insights.formatting_suggestions.length > 0 && (
                <div>
                  <p className="text-sm font-medium mb-2 flex items-center gap-1.5">
                    <FileText className="h-4 w-4 text-blue-400" /> Formatting Suggestions
                  </p>
                  <div className="space-y-1.5">
                    {insights.formatting_suggestions.slice(0, 4).map((suggestion, i) => (
                      <div key={i} className="flex items-start gap-2 text-xs text-muted-foreground">
                        <CheckCircle2 className="h-3 w-3 text-emerald-400 mt-0.5 shrink-0" />
                        <span>{suggestion}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Sidebar */}
        <motion.div variants={fadeUp} className="space-y-6">
          {/* Missing Metrics */}
          {insights?.missing_metrics && insights.missing_metrics.length > 0 && (
            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Target className="h-4 w-4 text-rose-400" />
                  <CardTitle className="text-sm">Missing Metrics</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {insights.missing_metrics.map((metric, i) => (
                    <div key={i} className="flex items-center gap-2 text-sm text-muted-foreground">
                      <ArrowUpRight className="h-3 w-3 text-rose-400 shrink-0" />
                      <span>{metric}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Action Verbs */}
          {insights?.weak_action_verbs && insights.weak_action_verbs.length > 0 && (
            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Zap className="h-4 w-4 text-amber-400" />
                  <CardTitle className="text-sm">Action Verbs</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {insights.weak_action_verbs.map((verb, i) => (
                    <div key={i} className="flex items-center gap-2 text-sm">
                      <Badge variant="warning" className="text-[10px]">{verb}</Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Industry Alignment */}
          {insights?.industry_alignment && (
            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <TrendingUp className="h-4 w-4 text-emerald-400" />
                  <CardTitle className="text-sm">Industry Alignment</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">{insights.industry_alignment}</p>
              </CardContent>
            </Card>
          )}

          {/* Upgrade CTA */}
          <Card className="bg-gradient-to-br from-primary/10 via-purple-500/5 to-emerald-500/5 border-0">
            <CardContent className="p-6 text-center">
              <Sparkles className="h-8 w-8 text-primary mx-auto" />
              <p className="mt-3 font-semibold">Unlock Full Analysis</p>
              <p className="text-xs text-muted-foreground mt-1">
                Get personalized career roadmap and skill recommendations
              </p>
              <Button className="mt-4 w-full rounded-xl gap-2" size="sm">
                <Zap className="h-4 w-4" /> Analyze with AI
              </Button>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </motion.div>
  );
}
