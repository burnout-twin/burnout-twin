"use client"

import { useState, useEffect } from "react"
import { MessageSquare, TrendingDown, TrendingUp, Minus } from "lucide-react"

type Metric = {
  label: string
  value: number
  max: number
  color: string
  trend: "up" | "down" | "stable"
}

const initialMetrics: Metric[] = [
  { label: "Health Battery", value: 90, max: 100, color: "hsl(var(--primary))", trend: "up" },
  { label: "Cognitive Load", value: 30, max: 100, color: "hsl(var(--accent))", trend: "stable" },
  { label: "Recovery Debt", value: 15, max: 100, color: "hsl(163 40% 45%)", trend: "down" },
  { label: "Social Energy", value: 65, max: 100, color: "hsl(220 60% 55%)", trend: "up" },
]

const insights = [
  "Wait. Analyze trade-offs?",
  "Schedule recovery block after standup.",
  "Cognitive load trending up. Reduce context switches.",
  "Social energy is stable. Safe to accept the 1:1.",
]

function TrendIcon({ trend }: { trend: "up" | "down" | "stable" }) {
  if (trend === "up") return <TrendingUp className="h-3 w-3 text-primary" />
  if (trend === "down") return <TrendingDown className="h-3 w-3 text-destructive" />
  return <Minus className="h-3 w-3 text-muted-foreground" />
}

function AnimatedBar({ value, color, delay }: { value: number; color: string; delay: number }) {
  const [width, setWidth] = useState(0)

  useEffect(() => {
    const timer = setTimeout(() => setWidth(value), delay)
    return () => clearTimeout(timer)
  }, [value, delay])

  return (
    <div className="relative h-3 w-full overflow-hidden rounded-full bg-secondary">
      <div
        className="absolute inset-y-0 left-0 rounded-full transition-all duration-1000 ease-out"
        style={{ width: `${width}%`, backgroundColor: color }}
      />
      {/* Glow effect for high values */}
      {value > 75 && (
        <div
          className="absolute inset-y-0 left-0 rounded-full opacity-30 blur-sm transition-all duration-1000 ease-out"
          style={{ width: `${width}%`, backgroundColor: color }}
        />
      )}
    </div>
  )
}

export function ConwayLogic() {
  const [currentInsight, setCurrentInsight] = useState(0)
  const [isVisible, setIsVisible] = useState(true)

  useEffect(() => {
    const interval = setInterval(() => {
      setIsVisible(false)
      setTimeout(() => {
        setCurrentInsight((prev) => (prev + 1) % insights.length)
        setIsVisible(true)
      }, 300)
    }, 4000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="flex h-full flex-col">
      <div className="px-6 pt-6 pb-4">
        <h2 className="text-lg font-semibold text-card-foreground">Conway Logic</h2>
        <p className="text-xs text-muted-foreground mt-0.5">Predictive burnout engine</p>
      </div>

      <div className="flex-1 px-6 pb-3">
        <div className="flex flex-col gap-4">
          {initialMetrics.map((metric, index) => (
            <div
              key={metric.label}
              className="animate-slide-in-right"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-1.5">
                  <span className="text-sm font-medium text-card-foreground">{metric.label}</span>
                  <TrendIcon trend={metric.trend} />
                </div>
                <span className="text-sm font-semibold text-card-foreground tabular-nums">
                  {metric.value}%
                </span>
              </div>
              <AnimatedBar value={metric.value} color={metric.color} delay={300 + index * 150} />
            </div>
          ))}
        </div>
      </div>

      {/* Insight bubble */}
      <div className="px-6 pb-6">
        <div
          className={`flex items-start gap-2.5 rounded-xl border border-accent/30 bg-accent/5 p-3 transition-all duration-300 ${
            isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-1"
          }`}
        >
          <MessageSquare className="h-4 w-4 shrink-0 mt-0.5 text-accent" />
          <p className="text-sm font-medium text-card-foreground leading-snug">
            {insights[currentInsight]}
          </p>
        </div>
      </div>
    </div>
  )
}
