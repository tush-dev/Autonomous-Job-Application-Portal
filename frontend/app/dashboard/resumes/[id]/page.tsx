"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  Save,
  Loader2,
  FileText,
  CheckCircle2,
  AlertCircle,
  ExternalLink,
  Plus,
  Trash2,
  Download,
} from "lucide-react";
import { apiClient } from "@/lib/api-client";
import type { Resume, ParsedResumeData, ResumeEntry } from "@/types/api";
import { toast } from "sonner";

interface EditableData {
  name: string;
  email: string;
  phone: string;
  summary: string;
  skills: string[];
  experience: ResumeEntry[];
  education: ResumeEntry[];
  projects: ResumeEntry[];
  certifications: string[];
}

export default function ResumeDetailPage() {
  const params = useParams();
  const router = useRouter();
  const resumeId = params.id as string;

  const [resume, setResume] = useState<Resume | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [data, setData] = useState<EditableData>({
    name: "",
    email: "",
    phone: "",
    summary: "",
    skills: [],
    experience: [],
    education: [],
    projects: [],
    certifications: [],
  });

  useEffect(() => {
    fetchResume();
  }, [resumeId]);

  async function fetchResume() {
    try {
      const res = await apiClient.get(`/resumes/${resumeId}`);
      const r: Resume = res.data;
      setResume(r);
      if (r.parsed_data) {
        const pd = r.parsed_data as any;
        setData({
          name: pd.name || "",
          email: pd.email || "",
          phone: pd.phone || "",
          summary: pd.summary || "",
          skills: pd.skills || [],
          experience: (pd.experience || []).map(normalizeEntry),
          education: (pd.education || []).map(normalizeEntry),
          projects: (pd.projects || []).map(normalizeEntry),
          certifications: pd.certifications || [],
        });
      }
    } catch {
      toast.error("Failed to load resume");
    } finally {
      setLoading(false);
    }
  }

  function normalizeEntry(e: any): ResumeEntry {
    return {
      title: e.title || "",
      organization: e.organization || "",
      date: e.date || "",
      description: e.description || "",
      highlights: e.highlights || [],
    };
  }

  async function handleSave() {
    setSaving(true);
    try {
      await apiClient.put(`/resumes/${resumeId}`, {
        parsed_data: data,
      });
      toast.success("Resume updated");
    } catch {
      toast.error("Save failed");
    } finally {
      setSaving(false);
    }
  }

  function addItem(field: "experience" | "education" | "projects") {
    setData((prev) => ({
      ...prev,
      [field]: [...prev[field], { title: "", organization: "", date: "", description: "", highlights: [] }],
    }));
  }

  function removeItem(field: "experience" | "education" | "projects", idx: number) {
    setData((prev) => ({
      ...prev,
      [field]: prev[field].filter((_, i) => i !== idx),
    }));
  }

  function updateItem(
    field: "experience" | "education" | "projects",
    idx: number,
    key: keyof ResumeEntry,
    value: any
  ) {
    setData((prev) => {
      const items = [...prev[field]];
      items[idx] = { ...items[idx], [key]: value };
      return { ...prev, [field]: items };
    });
  }

  function addHighlight(field: "experience" | "education" | "projects", idx: number) {
    setData((prev) => {
      const items = [...prev[field]];
      items[idx] = { ...items[idx], highlights: [...(items[idx].highlights || []), ""] };
      return { ...prev, [field]: items };
    });
  }

  function updateHighlight(
    field: "experience" | "education" | "projects",
    itemIdx: number,
    hlIdx: number,
    value: string
  ) {
    setData((prev) => {
      const items = [...prev[field]];
      const highlights = [...(items[itemIdx].highlights || [])];
      highlights[hlIdx] = value;
      items[itemIdx] = { ...items[itemIdx], highlights };
      return { ...prev, [field]: items };
    });
  }

  function removeHighlight(field: "experience" | "education" | "projects", itemIdx: number, hlIdx: number) {
    setData((prev) => {
      const items = [...prev[field]];
      const highlights = (items[itemIdx].highlights || []).filter((_, i) => i !== hlIdx);
      items[itemIdx] = { ...items[itemIdx], highlights };
      return { ...prev, [field]: items };
    });
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!resume) {
    return (
      <div className="rounded-xl border py-16 text-center">
        <AlertCircle className="mx-auto h-12 w-12 text-muted-foreground/50" />
        <p className="mt-4 text-lg font-medium">Resume not found</p>
      </div>
    );
  }

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={() => router.push("/dashboard/resumes")}
            className="rounded-lg p-2 hover:bg-accent"
          >
            <ArrowLeft className="h-5 w-5" />
          </button>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold truncate max-w-md">{resume.file_name}</h1>
              {resume.parsing_status === "completed" ? (
                <span className="inline-flex items-center gap-1 text-xs text-green-600 bg-green-50 dark:bg-green-950 px-2 py-0.5 rounded-full">
                  <CheckCircle2 className="h-3 w-3" /> Parsed
                </span>
              ) : resume.parsing_status === "failed" ? (
                <span className="inline-flex items-center gap-1 text-xs text-red-600 bg-red-50 dark:bg-red-950 px-2 py-0.5 rounded-full">
                  <AlertCircle className="h-3 w-3" /> Failed
                </span>
              ) : null}
            </div>
            <p className="text-sm text-muted-foreground">
              {(resume.file_size / 1024).toFixed(0)} KB &middot; {resume.file_type}
              {resume.parsing_confidence !== null && resume.parsing_confidence !== undefined && (
                <span> &middot; Confidence: {(resume.parsing_confidence * 100).toFixed(0)}%</span>
              )}
            </p>
          </div>
        </div>
        <button
          onClick={handleSave}
          disabled={saving}
          className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
        >
          {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
          {saving ? "Saving..." : "Save Changes"}
        </button>
      </div>

      {resume.parsing_error && (
        <div className="rounded-lg border border-red-200 bg-red-50 dark:bg-red-950 p-4 text-sm text-red-700 dark:text-red-300">
          <strong>Parsing Error:</strong> {resume.parsing_error}
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>Personal Information</CardHeader>
            <div className="grid gap-4 sm:grid-cols-3">
              <Field label="Full Name" value={data.name} onChange={(v) => setData((p) => ({ ...p, name: v }))} />
              <Field label="Email" value={data.email} onChange={(v) => setData((p) => ({ ...p, email: v }))} />
              <Field label="Phone" value={data.phone} onChange={(v) => setData((p) => ({ ...p, phone: v }))} />
            </div>
          </Card>

          <Card>
            <CardHeader>Professional Summary</CardHeader>
            <textarea
              value={data.summary}
              onChange={(e) => setData((p) => ({ ...p, summary: e.target.value }))}
              className="w-full rounded-lg border bg-background px-3 py-2 text-sm min-h-[100px] focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </Card>

          <Card>
            <CardHeader>Skills</CardHeader>
            <div className="flex flex-wrap gap-2">
              {data.skills.map((skill, i) => (
                <span key={i} className="inline-flex items-center gap-1 rounded-md bg-secondary px-2 py-1 text-sm">
                  {skill}
                  <button
                    onClick={() => setData((p) => ({ ...p, skills: p.skills.filter((_, j) => j !== i) }))}
                    className="text-muted-foreground hover:text-red-500"
                  >
                    <Trash2 className="h-3 w-3" />
                  </button>
                </span>
              ))}
              <button
                onClick={() => {
                  const skill = prompt("Enter skill name:");
                  if (skill) setData((p) => ({ ...p, skills: [...p.skills, skill] }));
                }}
                className="inline-flex items-center gap-1 rounded-md border border-dashed px-3 py-1 text-sm text-muted-foreground hover:text-foreground"
              >
                <Plus className="h-3 w-3" /> Add Skill
              </button>
            </div>
          </Card>

          <EntrySection
            title="Experience"
            items={data.experience}
            field="experience"
            onAdd={addItem}
            onRemove={removeItem}
            onUpdate={updateItem}
            onAddHighlight={addHighlight}
            onUpdateHighlight={updateHighlight}
            onRemoveHighlight={removeHighlight}
          />

          <EntrySection
            title="Education"
            items={data.education}
            field="education"
            onAdd={addItem}
            onRemove={removeItem}
            onUpdate={updateItem}
            onAddHighlight={addHighlight}
            onUpdateHighlight={updateHighlight}
            onRemoveHighlight={removeHighlight}
          />

          <EntrySection
            title="Projects"
            items={data.projects}
            field="projects"
            onAdd={addItem}
            onRemove={removeItem}
            onUpdate={updateItem}
            onAddHighlight={addHighlight}
            onUpdateHighlight={updateHighlight}
            onRemoveHighlight={removeHighlight}
          />

          <Card>
            <CardHeader>Certifications</CardHeader>
            <div className="space-y-2">
              {data.certifications.map((cert, i) => (
                <div key={i} className="flex items-center gap-2">
                  <input
                    value={cert}
                    onChange={(e) =>
                      setData((p) => {
                        const certs = [...p.certifications];
                        certs[i] = e.target.value;
                        return { ...p, certifications: certs };
                      })
                    }
                    className="flex-1 rounded-lg border bg-background px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                  <button
                    onClick={() =>
                      setData((p) => ({ ...p, certifications: p.certifications.filter((_, j) => j !== i) }))
                    }
                    className="text-muted-foreground hover:text-red-500"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              ))}
              <button
                onClick={() => setData((p) => ({ ...p, certifications: [...p.certifications, ""] }))}
                className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
              >
                <Plus className="h-3 w-3" /> Add Certification
              </button>
            </div>
          </Card>
        </div>

        <div className="space-y-4">
          <Card>
            <CardHeader>File Info</CardHeader>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Type</span>
                <span>{resume.file_type}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Size</span>
                <span>{(resume.file_size / 1024).toFixed(0)} KB</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Status</span>
                <span>{resume.parsing_status}</span>
              </div>
              {resume.parsing_confidence !== null && resume.parsing_confidence !== undefined && (
                <div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Confidence</span>
                    <span>{(resume.parsing_confidence * 100).toFixed(0)}%</span>
                  </div>
                  <div className="mt-1 h-1.5 rounded-full bg-muted">
                    <div
                      className="h-full rounded-full bg-primary transition-all"
                      style={{ width: `${(resume.parsing_confidence * 100).toFixed(0)}%` }}
                    />
                  </div>
                </div>
              )}
            </div>
          </Card>

          <Card>
            <CardHeader>Quick Actions</CardHeader>
            <div className="space-y-2">
              <button
                onClick={async () => {
                  try {
                    const res = await apiClient.get(`/resumes/${resumeId}/download`, {
                      responseType: "blob",
                    });
                    const url = URL.createObjectURL(res.data);
                    const link = document.createElement("a");
                    link.href = url;
                    link.download = resume.file_name;
                    document.body.appendChild(link);
                    link.click();
                    link.remove();
                    URL.revokeObjectURL(url);
                  } catch {
                    toast.error("Download failed");
                  }
                }}
                className="w-full inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-sm hover:bg-accent"
              >
                <Download className="h-4 w-4" /> Download Original
              </button>
              <button
                onClick={() => router.push(`/dashboard/resumes`)}
                className="w-full inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-sm hover:bg-accent"
              >
                <ArrowLeft className="h-4 w-4" /> Back to Resumes
              </button>
            </div>
          </Card>
        </div>
      </div>
    </motion.div>
  );
}

function Card({ children }: { children: React.ReactNode }) {
  return <div className="rounded-xl border p-5">{children}</div>;
}

function CardHeader({ children }: { children: React.ReactNode }) {
  return <h2 className="font-semibold mb-3">{children}</h2>;
}

function Field({
  label,
  value,
  onChange,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <div>
      <label className="block text-xs text-muted-foreground mb-1">{label}</label>
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-lg border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
      />
    </div>
  );
}

function EntrySection({
  title,
  items,
  field,
  onAdd,
  onRemove,
  onUpdate,
  onAddHighlight,
  onUpdateHighlight,
  onRemoveHighlight,
}: {
  title: string;
  items: ResumeEntry[];
  field: "experience" | "education" | "projects";
  onAdd: (field: "experience" | "education" | "projects") => void;
  onRemove: (field: "experience" | "education" | "projects", idx: number) => void;
  onUpdate: (field: "experience" | "education" | "projects", idx: number, key: keyof ResumeEntry, value: any) => void;
  onAddHighlight: (field: "experience" | "education" | "projects", idx: number) => void;
  onUpdateHighlight: (field: "experience" | "education" | "projects", itemIdx: number, hlIdx: number, value: string) => void;
  onRemoveHighlight: (field: "experience" | "education" | "projects", itemIdx: number, hlIdx: number) => void;
}) {
  return (
    <Card>
      <div className="flex items-center justify-between mb-3">
        <h2 className="font-semibold">{title}</h2>
        <button
          onClick={() => onAdd(field)}
          className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
        >
          <Plus className="h-3 w-3" /> Add
        </button>
      </div>
      <div className="space-y-4">
        {items.map((item, i) => (
          <div key={i} className="rounded-lg border p-4">
            <div className="flex justify-between mb-2">
              <span className="text-xs font-medium text-muted-foreground">Entry {i + 1}</span>
              <button
                onClick={() => onRemove(field, i)}
                className="text-muted-foreground hover:text-red-500"
              >
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
            <div className="grid gap-3 sm:grid-cols-2 mb-3">
              <input
                placeholder="Title"
                value={item.title || ""}
                onChange={(e) => onUpdate(field, i, "title", e.target.value)}
                className="rounded-lg border bg-background px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
              <input
                placeholder="Organization"
                value={item.organization || ""}
                onChange={(e) => onUpdate(field, i, "organization", e.target.value)}
                className="rounded-lg border bg-background px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
              <input
                placeholder="Date (e.g., 2020-2023)"
                value={item.date || ""}
                onChange={(e) => onUpdate(field, i, "date", e.target.value)}
                className="rounded-lg border bg-background px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            <textarea
              placeholder="Description"
              value={item.description || ""}
              onChange={(e) => onUpdate(field, i, "description", e.target.value)}
              className="w-full rounded-lg border bg-background px-3 py-1.5 text-sm min-h-[60px] focus:outline-none focus:ring-2 focus:ring-primary"
            />
            <div className="mt-2 space-y-1">
              {(item.highlights || []).map((hl, hli) => (
                <div key={hli} className="flex items-center gap-2">
                  <span className="text-xs text-muted-foreground">•</span>
                  <input
                    value={hl}
                    onChange={(e) => onUpdateHighlight(field, i, hli, e.target.value)}
                    className="flex-1 rounded border bg-background px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-primary"
                    placeholder="Highlight..."
                  />
                  <button
                    onClick={() => onRemoveHighlight(field, i, hli)}
                    className="text-muted-foreground hover:text-red-500"
                  >
                    <Trash2 className="h-3 w-3" />
                  </button>
                </div>
              ))}
              <button
                onClick={() => onAddHighlight(field, i)}
                className="text-xs text-muted-foreground hover:text-foreground"
              >
                + Add highlight
              </button>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
