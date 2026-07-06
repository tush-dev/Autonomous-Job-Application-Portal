"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { MessageSquare, X, Sparkles, Send, Bot, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";

const quickPrompts = [
  "How can I improve my resume?",
  "What jobs match my skills?",
  "Prepare me for an interview",
  "Suggest skills to learn",
];

export function FloatingAI() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Array<{ role: "user" | "assistant"; content: string }>>([
    {
      role: "assistant",
      content: "Hi! I'm your Career Copilot. Ask me anything about your job search, resume, or career growth.",
    },
  ]);
  const [input, setInput] = useState("");

  const handleSend = async () => {
    if (!input.trim()) return;
    const msg = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: msg }]);
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "I'm analyzing your profile and will provide personalized recommendations shortly." },
      ]);
    }, 1000);
  };

  return (
    <>
      {/* Trigger button */}
      <motion.button
        onClick={() => setOpen(true)}
        className={cn(
          "fixed bottom-6 right-6 z-50 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-primary to-purple-600 text-white shadow-2xl shadow-primary/30 hover:shadow-primary/40 transition-all duration-200",
          open && "scale-0 opacity-0 pointer-events-none"
        )}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        <MessageSquare className="h-6 w-6" />
      </motion.button>

      {/* Chat panel */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            transition={{ duration: 0.2, ease: [0.25, 0.1, 0.25, 1] }}
            className="fixed bottom-6 right-6 z-50 flex w-[380px] flex-col rounded-2xl border border-border/50 bg-card/95 backdrop-blur-xl shadow-2xl overflow-hidden"
          >
            {/* Header */}
            <div className="flex items-center justify-between border-b border-border/30 px-5 py-4">
              <div className="flex items-center gap-3">
                <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-purple-600">
                  <Bot className="h-4 w-4 text-white" />
                </div>
                <div>
                  <p className="text-sm font-semibold">Career Copilot</p>
                  <p className="text-[10px] text-muted-foreground">AI Assistant</p>
                </div>
              </div>
              <Button variant="ghost" size="icon" className="rounded-lg" onClick={() => setOpen(false)}>
                <X className="h-4 w-4" />
              </Button>
            </div>

            {/* Messages */}
            <ScrollArea className="flex-1 p-5 h-[400px]">
              <div className="space-y-4">
                {messages.map((msg, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.05 }}
                    className={cn(
                      "flex gap-3",
                      msg.role === "user" && "flex-row-reverse"
                    )}
                  >
                    <div
                      className={cn(
                        "flex h-8 w-8 shrink-0 items-center justify-center rounded-xl",
                        msg.role === "assistant"
                          ? "bg-primary/10 text-primary"
                          : "bg-muted text-muted-foreground"
                      )}
                    >
                      {msg.role === "assistant" ? (
                        <Bot className="h-4 w-4" />
                      ) : (
                        <User className="h-4 w-4" />
                      )}
                    </div>
                    <div
                      className={cn(
                        "rounded-2xl px-4 py-2.5 text-sm max-w-[80%]",
                        msg.role === "assistant"
                          ? "bg-muted/50 text-foreground"
                          : "bg-primary text-primary-foreground"
                      )}
                    >
                      {msg.content}
                    </div>
                  </motion.div>
                ))}
              </div>
            </ScrollArea>

            {/* Quick prompts */}
            <div className="flex flex-wrap gap-1.5 px-5 pb-2">
              {quickPrompts.map((prompt) => (
                <button
                  key={prompt}
                  onClick={() => {
                    setMessages((prev) => [...prev, { role: "user", content: prompt }]);
                  }}
                  className="rounded-lg bg-muted/50 px-2.5 py-1 text-[11px] text-muted-foreground hover:bg-muted transition-colors"
                >
                  {prompt}
                </button>
              ))}
            </div>

            {/* Input */}
            <div className="border-t border-border/30 p-4">
              <div className="flex items-center gap-2">
                <Input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask anything..."
                  className="flex-1 h-10 rounded-xl bg-muted/30 border-0 ring-1 ring-border/50 focus-visible:ring-primary"
                  onKeyDown={(e) => e.key === "Enter" && handleSend()}
                />
                <Button size="icon" className="rounded-xl h-10 w-10 shrink-0" onClick={handleSend}>
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
