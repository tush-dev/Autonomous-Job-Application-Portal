"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import {
  ArrowRight, BriefcaseBusiness, Check, FileCheck2,
  Sparkles, Target, WandSparkles, Zap,
} from "lucide-react";

const steps = [
  { icon: FileCheck2, number: "01", title: "Build your profile", description: "Upload your resume once. We understand your experience, strengths, and goals." },
  { icon: Target, number: "02", title: "Meet your best matches", description: "Your career agent scans the market and ranks roles by real fit—not just keywords." },
  { icon: WandSparkles, number: "03", title: "Apply with confidence", description: "Get tailored, truthful resumes and cover letters ready for every opportunity." },
];

const proof = ["50+ job sources", "ATS-ready documents", "You stay in control"];

export default function LandingPage() {
  return (
    <div className="min-h-screen overflow-hidden bg-background text-foreground">
      <header className="relative z-20 border-b border-primary/10 bg-background/80 backdrop-blur-xl">
        <div className="container flex h-20 items-center justify-between px-5">
          <Link href="/" className="flex items-center gap-3">
            <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-primary text-primary-foreground shadow-[0_8px_24px_rgba(22,104,82,.22)]">
              <BriefcaseBusiness className="h-5 w-5" />
            </span>
            <span className="text-xl font-bold tracking-[-0.04em]">JobAgent<span className="text-amber-600">.</span></span>
          </Link>
          <nav className="hidden items-center gap-8 text-sm font-medium text-muted-foreground md:flex">
            <a href="#how-it-works" className="transition-colors hover:text-primary">How it works</a>
            <a href="#features" className="transition-colors hover:text-primary">Why JobAgent</a>
          </nav>
          <div className="flex items-center gap-2 sm:gap-3">
            <Link href="/auth/login" className="rounded-full px-4 py-2.5 text-sm font-semibold text-primary hover:bg-primary/5">Sign in</Link>
            <Link href="/auth/signup" className="group inline-flex items-center gap-2 rounded-full bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground shadow-lg shadow-primary/15 transition hover:-translate-y-0.5">
              Start free <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
            </Link>
          </div>
        </div>
      </header>

      <main>
        <section className="relative">
          <div className="absolute -left-28 top-20 h-72 w-72 rounded-full bg-emerald-200/30 blur-3xl" />
          <div className="absolute -right-24 top-8 h-80 w-80 rounded-full bg-orange-200/30 blur-3xl" />
          <div className="container relative grid min-h-[700px] items-center gap-14 px-5 py-20 lg:grid-cols-[1.05fr_.95fr] lg:py-24">
            <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: .55 }}>
              <div className="mb-7 inline-flex items-center gap-2 rounded-full border border-primary/15 bg-white/70 px-4 py-2 text-xs font-semibold text-primary shadow-sm">
                <Sparkles className="h-3.5 w-3.5 text-amber-600" /> Your thoughtful AI career partner
              </div>
              <h1 className="max-w-3xl text-5xl font-bold leading-[1.04] tracking-[-0.055em] sm:text-6xl lg:text-7xl">
                Less time applying.<br/><span className="text-primary">More doors opening.</span>
              </h1>
              <p className="mt-7 max-w-xl text-lg leading-8 text-muted-foreground">
                A calmer, smarter job search. Discover roles that truly fit, tailor every application, and keep your momentum—all in one place.
              </p>
              <div className="mt-9 flex flex-col gap-3 sm:flex-row">
                <Link href="/auth/signup" className="group inline-flex items-center justify-center gap-2 rounded-full bg-primary px-7 py-4 font-semibold text-primary-foreground shadow-[0_12px_30px_rgba(22,104,82,.2)] transition hover:-translate-y-0.5">
                  Find my next role <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                </Link>
                <a href="#how-it-works" className="inline-flex items-center justify-center rounded-full border border-primary/15 bg-white/60 px-7 py-4 font-semibold text-primary transition hover:bg-white">See how it works</a>
              </div>
              <div className="mt-8 flex flex-wrap gap-x-6 gap-y-3">
                {proof.map((item) => <span key={item} className="inline-flex items-center gap-2 text-xs font-medium text-muted-foreground"><span className="flex h-5 w-5 items-center justify-center rounded-full bg-secondary text-primary"><Check className="h-3 w-3" /></span>{item}</span>)}
              </div>
            </motion.div>

            <motion.div initial={{ opacity: 0, scale: .96, y: 20 }} animate={{ opacity: 1, scale: 1, y: 0 }} transition={{ duration: .65, delay: .12 }} className="relative mx-auto w-full max-w-[560px]">
              <div className="absolute -inset-5 rotate-2 rounded-[2.5rem] bg-[#dcece3]" />
              <div className="relative rounded-[2rem] border border-white/80 bg-white/90 p-5 shadow-[0_30px_80px_rgba(19,67,54,.15)] backdrop-blur">
                <div className="flex items-center justify-between border-b border-border/60 pb-4">
                  <div><p className="text-xs font-semibold uppercase tracking-[.18em] text-muted-foreground">Today&apos;s shortlist</p><p className="mt-1 text-lg font-bold">Roles picked for you</p></div>
                  <span className="rounded-full bg-accent px-3 py-1.5 text-xs font-semibold text-accent-foreground">12 new matches</span>
                </div>
                <div className="space-y-3 py-4">
                  {[
                    ["Product Designer", "Northstar Labs", "94%", "NS", "bg-[#f5d7bd] text-[#8a4b23]"],
                    ["Senior UX Designer", "Greenline", "89%", "GL", "bg-[#dcece3] text-primary"],
                    ["Design Systems Lead", "Aster Studio", "86%", "AS", "bg-[#ede1c5] text-[#735b20]"],
                  ].map(([role, company, score, initials, color], i) => (
                    <motion.div key={role} initial={{ opacity: 0, x: 10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: .35 + i * .1 }} className="flex items-center gap-4 rounded-2xl border border-border/60 bg-card p-4 transition hover:-translate-y-0.5 hover:shadow-md">
                      <span className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl text-xs font-bold ${color}`}>{initials}</span>
                      <div className="min-w-0 flex-1"><p className="truncate text-sm font-bold">{role}</p><p className="mt-0.5 text-xs text-muted-foreground">{company} · Remote friendly</p></div>
                      <span className="rounded-full bg-secondary px-2.5 py-1 text-xs font-bold text-primary">{score}</span>
                    </motion.div>
                  ))}
                </div>
                <div className="rounded-2xl bg-primary p-5 text-primary-foreground">
                  <div className="flex items-center gap-3"><span className="rounded-xl bg-white/15 p-2"><Zap className="h-4 w-4 text-amber-300" /></span><div><p className="text-sm font-semibold">Your agent is working</p><p className="mt-0.5 text-xs text-emerald-100/75">Scanning 8 sources for better matches</p></div></div>
                  <div className="mt-4 h-1.5 overflow-hidden rounded-full bg-white/15"><div className="h-full w-2/3 rounded-full bg-amber-300" /></div>
                </div>
              </div>
              <div className="absolute -bottom-7 -left-7 hidden rounded-2xl border border-white bg-[#fff8ed] p-4 shadow-xl sm:block"><p className="text-xs text-muted-foreground">Time saved this week</p><p className="mt-1 text-2xl font-bold text-primary">6.5 hours</p></div>
            </motion.div>
          </div>
        </section>

        <section id="how-it-works" className="border-y border-primary/10 bg-[#edf4ef] py-24">
          <div className="container px-5">
            <div className="mx-auto max-w-2xl text-center"><p className="text-xs font-bold uppercase tracking-[.2em] text-amber-700">Simple by design</p><h2 className="mt-4 text-3xl font-bold tracking-[-.04em] sm:text-5xl">Your search, finally working for you.</h2><p className="mt-5 text-muted-foreground">Job hunting is already a full-time job. We take the busywork off your plate while keeping every decision yours.</p></div>
            <div className="mt-14 grid gap-5 md:grid-cols-3">
              {steps.map((step) => <div key={step.number} className="group rounded-[1.75rem] border border-primary/10 bg-white/75 p-7 transition hover:-translate-y-1 hover:shadow-[0_20px_50px_rgba(19,67,54,.1)]"><div className="flex items-center justify-between"><span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-primary text-primary-foreground"><step.icon className="h-5 w-5" /></span><span className="text-sm font-bold text-primary/25">{step.number}</span></div><h3 className="mt-7 text-xl font-bold">{step.title}</h3><p className="mt-3 text-sm leading-6 text-muted-foreground">{step.description}</p></div>)}
            </div>
          </div>
        </section>

        <section id="features" className="py-24"><div className="container px-5"><div className="rounded-[2rem] bg-primary px-7 py-12 text-primary-foreground sm:px-12 lg:flex lg:items-center lg:justify-between"><div className="max-w-2xl"><p className="text-sm font-semibold text-amber-300">Your next chapter can start today.</p><h2 className="mt-3 text-3xl font-bold tracking-[-.04em] sm:text-4xl">Let your experience do the talking.</h2><p className="mt-4 text-sm leading-6 text-emerald-100/75">Join JobAgent and turn a scattered job search into a clear, focused path forward.</p></div><Link href="/auth/signup" className="mt-8 inline-flex items-center gap-2 rounded-full bg-[#f4c46b] px-6 py-3.5 font-bold text-[#173f35] transition hover:bg-[#ffd486] lg:mt-0">Get started free <ArrowRight className="h-4 w-4" /></Link></div></div></section>
      </main>

      <footer className="border-t border-primary/10 py-8"><div className="container flex flex-col items-center justify-between gap-4 px-5 text-xs text-muted-foreground sm:flex-row"><div className="flex items-center gap-2 font-bold text-foreground"><BriefcaseBusiness className="h-4 w-4 text-primary" /> JobAgent.</div><p>© {new Date().getFullYear()} JobAgent. Built for better beginnings.</p></div></footer>
    </div>
  );
}
