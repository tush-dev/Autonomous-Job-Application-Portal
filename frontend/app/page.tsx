"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { ArrowRight, Sparkles, Search, FileText, Zap } from "lucide-react";

const features = [
  {
    icon: Search,
    title: "Smart Job Search",
    description:
      "AI-powered search across 50+ job boards. Find roles that match your skills and preferences.",
  },
  {
    icon: FileText,
    title: "Resume Tailoring",
    description:
      "Generate ATS-optimized resumes for each application. Keywords optimized, always truthful.",
  },
  {
    icon: Sparkles,
    title: "AI Cover Letters",
    description:
      "Human-sounding cover letters generated in seconds. Choose from professional, short, or custom tones.",
  },
  {
    icon: Zap,
    title: "Auto-Apply",
    description:
      "Automatically submit applications with tailored resumes and cover letters. Track everything.",
  },
];

export default function LandingPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="border-b">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <div className="flex items-center gap-2">
            <Sparkles className="h-6 w-6 text-primary" />
            <span className="text-xl font-bold">JobAgent</span>
          </div>
          <nav className="flex items-center gap-4">
            <Link
              href="/login"
              className="text-sm font-medium text-muted-foreground hover:text-foreground"
            >
              Sign in
            </Link>
            <Link
              href="/signup"
              className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
            >
              Get Started
              <ArrowRight className="h-4 w-4" />
            </Link>
          </nav>
        </div>
      </header>

      <main className="flex-1">
        <section className="container mx-auto px-4 py-24 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <h1 className="mx-auto max-w-4xl text-5xl font-bold tracking-tight sm:text-6xl">
              Your AI-Powered
              <span className="text-primary"> Career Accelerator</span>
            </h1>
            <p className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground">
              Upload your resume once. JobAgent searches, matches, tailors
              resumes, and submits applications — so you can focus on
              interviewing.
            </p>
            <div className="mt-10 flex items-center justify-center gap-4">
              <Link
                href="/signup"
                className="inline-flex items-center gap-2 rounded-lg bg-primary px-8 py-3 text-lg font-medium text-primary-foreground hover:bg-primary/90"
              >
                Start Free
                <ArrowRight className="h-5 w-5" />
              </Link>
              <Link
                href="/login"
                className="inline-flex items-center gap-2 rounded-lg border px-8 py-3 text-lg font-medium hover:bg-accent"
              >
                Sign In
              </Link>
            </div>
          </motion.div>
        </section>

        <section className="border-t py-24">
          <div className="container mx-auto px-4">
            <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-4">
              {features.map((feature, index) => (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  className="rounded-xl border p-6"
                >
                  <feature.icon className="mb-4 h-10 w-10 text-primary" />
                  <h3 className="mb-2 text-lg font-semibold">
                    {feature.title}
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    {feature.description}
                  </p>
                </motion.div>
              ))}
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t py-8">
        <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
          &copy; {new Date().getFullYear()} JobAgent. All rights reserved.
        </div>
      </footer>
    </div>
  );
}
