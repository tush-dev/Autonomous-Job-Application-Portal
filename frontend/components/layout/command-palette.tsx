"use client";

import { useEffect, useState, useCallback, useMemo } from "react";
import { useRouter } from "next/navigation";
import {
  CommandDialog,
  CommandInput,
  CommandList,
  CommandEmpty,
  CommandGroup,
  CommandItem,
} from "@/components/ui/command";
import {
  LayoutDashboard,
  Briefcase,
  FileText,
  BarChart3,
  MessageSquare,
  Brain,
  Settings,
  Sparkles,
  Upload,
  Search,
  GraduationCap,
} from "lucide-react";

const commands = [
  {
    heading: "Pages",
    items: [
      { icon: LayoutDashboard, label: "Dashboard", shortcut: "G D", action: "/dashboard" },
      { icon: Briefcase, label: "Job Search", shortcut: "G J", action: "/dashboard/jobs" },
      { icon: FileText, label: "Resumes", shortcut: "G R", action: "/dashboard/resumes" },
      { icon: BarChart3, label: "Analytics", shortcut: "G A", action: "/dashboard/analytics" },
      { icon: Brain, label: "Career Insights", shortcut: "G I", action: "/dashboard/insights" },
      { icon: MessageSquare, label: "AI Coach", shortcut: "G C", action: "/dashboard/coach" },
      { icon: GraduationCap, label: "Interviews", shortcut: "G V", action: "/dashboard/interviews" },
      { icon: Settings, label: "Settings", shortcut: "G S", action: "/dashboard/settings" },
    ],
  },
  {
    heading: "Actions",
    items: [
      { icon: Upload, label: "Upload Resume", shortcut: "U R", action: "upload-resume" },
      { icon: Search, label: "Search Jobs", shortcut: "S J", action: "search-jobs" },
      { icon: Sparkles, label: "Analyze Resume", shortcut: "A R", action: "analyze-resume" },
    ],
  },
];

interface CommandPaletteProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function CommandPalette({ open, onOpenChange }: CommandPaletteProps) {
  const router = useRouter();
  const [search, setSearch] = useState("");
  const filteredGroups = useMemo(() => {
    const query = search.trim().toLowerCase();
    if (!query) return commands;
    return commands
      .map((group) => ({
        ...group,
        items: group.items.filter((item) =>
          `${item.label} ${group.heading}`.toLowerCase().includes(query)
        ),
      }))
      .filter((group) => group.items.length > 0);
  }, [search]);

  const handleSelect = useCallback(
    (action: string) => {
      onOpenChange(false);
      if (action.startsWith("/")) {
        router.push(action);
      } else if (action === "upload-resume") {
        router.push("/dashboard/resumes");
      } else if (action === "search-jobs") {
        router.push("/dashboard/jobs");
      } else if (action === "analyze-resume") {
        router.push("/dashboard/insights");
      }
    },
    [router, onOpenChange]
  );

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        onOpenChange(!open);
      }
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [open, onOpenChange]);

  useEffect(() => {
    if (!open) setSearch("");
  }, [open]);

  if (!open) return null;

  return (
    <CommandDialog open={open} onOpenChange={onOpenChange}>
      <CommandInput
        autoFocus
        placeholder="Type a command or search..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && filteredGroups[0]?.items[0]) {
            e.preventDefault();
            handleSelect(filteredGroups[0].items[0].action);
          }
        }}
      />
      <CommandList>
        {filteredGroups.length === 0 && (
          <CommandEmpty>No matching command. Try “jobs”, “resume”, or “analytics”.</CommandEmpty>
        )}
        {filteredGroups.map((group) => (
          <CommandGroup key={group.heading} heading={group.heading}>
            {group.items.map((item) => (
              <CommandItem
                key={item.label}
                role="button"
                tabIndex={0}
                onClick={() => handleSelect(item.action)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") handleSelect(item.action);
                }}
                className="cursor-pointer hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground"
              >
                <item.icon className="mr-2 h-4 w-4" />
                <span>{item.label}</span>
                <span className="ml-auto text-xs text-muted-foreground">
                  {item.shortcut}
                </span>
              </CommandItem>
            ))}
          </CommandGroup>
        ))}
      </CommandList>
    </CommandDialog>
  );
}
