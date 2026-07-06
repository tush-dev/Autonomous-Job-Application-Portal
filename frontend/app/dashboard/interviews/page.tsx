"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  Calendar,
  Clock,
  MapPin,
  Video,
  Loader2,
  CheckCircle2,
  XCircle,
} from "lucide-react";
import { apiClient } from "@/lib/api-client";

interface Interview {
  id: string;
  application_id: string;
  interview_type?: string;
  scheduled_at: string;
  duration_minutes: number;
  location?: string;
  meeting_link?: string;
  notes?: string;
  status: string;
  job_title?: string;
  company_name?: string;
}

export default function InterviewsPage() {
  const [interviews, setInterviews] = useState<Interview[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchInterviews();
  }, []);

  async function fetchInterviews() {
    try {
      const res = await apiClient.get("/interviews");
      setInterviews(res.data);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  }

  const upcoming = interviews.filter((i) => i.status === "SCHEDULED");
  const past = interviews.filter((i) => i.status !== "SCHEDULED");

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Interviews</h1>
        <p className="mt-1 text-muted-foreground">Manage your upcoming and past interviews</p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      ) : interviews.length === 0 ? (
        <div className="rounded-xl border py-16 text-center">
          <Calendar className="mx-auto h-12 w-12 text-muted-foreground/50" />
          <p className="mt-4 text-lg font-medium">No interviews scheduled</p>
          <p className="text-sm text-muted-foreground">Interviews will appear here once you have applications in progress</p>
        </div>
      ) : (
        <>
          {upcoming.length > 0 && (
            <section>
              <h2 className="mb-3 text-lg font-semibold">Upcoming ({upcoming.length})</h2>
              <div className="space-y-3">
                {upcoming.map((interview, i) => (
                  <motion.div
                    key={interview.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.05 }}
                    className="rounded-xl border-l-4 border-l-green-500 bg-background p-5"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold">{interview.job_title || "Interview"}</h3>
                        {interview.company_name && (
                          <p className="text-sm text-muted-foreground">{interview.company_name}</p>
                        )}
                      </div>
                      <span className="inline-flex items-center gap-1 rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-700">
                        <Clock className="h-3 w-3" /> Scheduled
                      </span>
                    </div>

                    <div className="mt-4 flex flex-wrap gap-4 text-sm text-muted-foreground">
                      <span className="inline-flex items-center gap-1.5">
                        <Calendar className="h-4 w-4" />
                        {new Date(interview.scheduled_at).toLocaleDateString("en-US", {
                          weekday: "short", month: "short", day: "numeric", year: "numeric",
                        })}
                      </span>
                      <span className="inline-flex items-center gap-1.5">
                        <Clock className="h-4 w-4" />
                        {new Date(interview.scheduled_at).toLocaleTimeString("en-US", {
                          hour: "2-digit", minute: "2-digit",
                        })}
                        {" "}({interview.duration_minutes} min)
                      </span>
                      {interview.location && (
                        <span className="inline-flex items-center gap-1.5">
                          <MapPin className="h-4 w-4" /> {interview.location}
                        </span>
                      )}
                      {interview.meeting_link && (
                        <a
                          href={interview.meeting_link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1.5 text-primary hover:underline"
                        >
                          <Video className="h-4 w-4" /> Join
                        </a>
                      )}
                    </div>

                    {interview.notes && (
                      <p className="mt-3 text-sm text-muted-foreground">{interview.notes}</p>
                    )}
                  </motion.div>
                ))}
              </div>
            </section>
          )}

          {past.length > 0 && (
            <section>
              <h2 className="mb-3 text-lg font-semibold">Past ({past.length})</h2>
              <div className="space-y-2">
                {past.map((interview, i) => (
                  <motion.div
                    key={interview.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.03 }}
                    className="rounded-xl border p-4 opacity-70"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1 min-w-0">
                        <p className="font-medium">{interview.job_title || "Interview"}</p>
                        {interview.company_name && (
                          <p className="text-xs text-muted-foreground">{interview.company_name}</p>
                        )}
                      </div>
                      <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${
                        interview.status === "COMPLETED"
                          ? "bg-green-100 text-green-700"
                          : interview.status === "CANCELLED"
                          ? "bg-red-100 text-red-700"
                          : "bg-gray-100 text-gray-700"
                      }`}>
                        {interview.status === "COMPLETED" ? (
                          <CheckCircle2 className="h-3 w-3" />
                        ) : (
                          <XCircle className="h-3 w-3" />
                        )}
                        {interview.status.charAt(0) + interview.status.slice(1).toLowerCase()}
                      </span>
                    </div>
                    <p className="mt-1 text-xs text-muted-foreground">
                      {new Date(interview.scheduled_at).toLocaleDateString()}
                    </p>
                  </motion.div>
                ))}
              </div>
            </section>
          )}
        </>
      )}
    </motion.div>
  );
}
