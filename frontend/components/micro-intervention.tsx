"use client"

import { useState, useEffect } from "react"
import { Lightbulb, X } from "lucide-react"

const suggestions = [
  { text: "Suggested reset: 5-min break", detail: "You've been in meetings 2h straight." },
  { text: "Block 30 min for deep work", detail: "No focus blocks scheduled this afternoon." },
  { text: "Step away from screen", detail: "Continuous screen time approaching 3 hours." },
  { text: "Hydration check", detail: "Last logged break was over 90 minutes ago." },
]

export function MicroIntervention() {
  const [index, setIndex] = useState(0)
  const [dismissed, setDismissed] = useState(false)
  const [visible, setVisible] = useState(true)

  // Cycle through suggestions
  useEffect(() => {
    if (dismissed) return
    const interval = setInterval(() => {
      setVisible(false)
      setTimeout(() => {
        setIndex((prev) => (prev + 1) % suggestions.length)
        setVisible(true)
      }, 300)
    }, 8000)
    return () => clearInterval(interval)
  }, [dismissed])

  if (dismissed) return null

  const suggestion = suggestions[index]

  return (
    <div
      className={`flex items-start gap-3 rounded-xl border border-primary/20 bg-primary/5 p-4 transition-all duration-300 ${
        visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-1"
      }`}
    >
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary/15">
        <Lightbulb className="h-4 w-4 text-primary" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-card-foreground">{suggestion.text}</p>
        <p className="text-xs text-muted-foreground mt-0.5">{suggestion.detail}</p>
      </div>
      <button
        type="button"
        onClick={() => setDismissed(true)}
        className="shrink-0 rounded-md p-1 text-muted-foreground hover:text-card-foreground hover:bg-secondary transition-colors"
        aria-label="Dismiss suggestion"
      >
        <X className="h-3.5 w-3.5" />
      </button>
    </div>
  )
}
