"use client"

import { useState } from "react"
import { TrendingUp, TrendingDown, Minus } from "lucide-react"

type TimeRange = "24h" | "7d"

// Simulated stress data (0-100)
const data24h = [20, 25, 22, 35, 55, 48, 60, 45, 38, 30, 42, 35, 28, 30, 25, 32, 45, 58, 40, 32, 28, 22, 20, 18]
const data7d = [30, 42, 38, 55, 48, 35, 28]

function miniPath(values: number[], width: number, height: number, padding = 4) {
  const w = width - padding * 2
  const h = height - padding * 2
  const max = Math.max(...values)
  const min = Math.min(...values)
  const range = max - min || 1
  const stepX = w / (values.length - 1)

  return values
    .map((v, i) => {
      const x = padding + i * stepX
      const y = padding + h - ((v - min) / range) * h
      return `${i === 0 ? "M" : "L"} ${x.toFixed(1)} ${y.toFixed(1)}`
    })
    .join(" ")
}

function spikeIndices(values: number[], threshold = 50) {
  return values.reduce<number[]>((acc, v, i) => {
    if (v >= threshold) acc.push(i)
    return acc
  }, [])
}

function currentDirection(values: number[]): "up" | "down" | "stable" {
  const recent = values.slice(-3)
  const diff = recent[recent.length - 1] - recent[0]
  if (diff > 5) return "up"
  if (diff < -5) return "down"
  return "stable"
}

export function StressTrend() {
  const [range, setRange] = useState<TimeRange>("24h")
  const values = range === "24h" ? data24h : data7d
  const labels = range === "24h" ? ["12 AM", "6 AM", "12 PM", "6 PM", "Now"] : ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

  const chartW = 320
  const chartH = 100
  const padding = 6
  const path = miniPath(values, chartW, chartH, padding)
  const spikes = spikeIndices(values)
  const direction = currentDirection(values)

  const stepX = (chartW - padding * 2) / (values.length - 1)
  const max = Math.max(...values)
  const min = Math.min(...values)
  const rangeVal = max - min || 1

  // Current point coords
  const lastIdx = values.length - 1
  const cx = padding + lastIdx * stepX
  const cy = padding + (chartH - padding * 2) - ((values[lastIdx] - min) / rangeVal) * (chartH - padding * 2)

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-card-foreground">Stress Trend</h3>
        <div className="flex items-center gap-1 rounded-lg bg-secondary p-0.5">
          {(["24h", "7d"] as const).map((r) => (
            <button
              key={r}
              type="button"
              onClick={() => setRange(r)}
              className={`rounded-md px-2.5 py-1 text-xs font-medium transition-colors ${
                range === r ? "bg-card text-card-foreground shadow-sm" : "text-muted-foreground hover:text-card-foreground"
              }`}
            >
              {r}
            </button>
          ))}
        </div>
      </div>

      {/* Chart */}
      <svg
        viewBox={`0 0 ${chartW} ${chartH}`}
        className="w-full"
        role="img"
        aria-label={`Stress trend over last ${range}`}
      >
        {/* Gradient fill under line */}
        <defs>
          <linearGradient id="trendFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="hsl(var(--primary))" stopOpacity="0.15" />
            <stop offset="100%" stopColor="hsl(var(--primary))" stopOpacity="0" />
          </linearGradient>
        </defs>

        {/* Area fill */}
        <path
          d={`${path} L ${padding + lastIdx * stepX} ${chartH - padding} L ${padding} ${chartH - padding} Z`}
          fill="url(#trendFill)"
        />

        {/* Line */}
        <path d={path} fill="none" stroke="hsl(var(--primary))" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />

        {/* Spike dots */}
        {spikes.map((i) => {
          const sx = padding + i * stepX
          const sy = padding + (chartH - padding * 2) - ((values[i] - min) / rangeVal) * (chartH - padding * 2)
          return (
            <circle
              key={i}
              cx={sx}
              cy={sy}
              r="3.5"
              fill="hsl(var(--accent))"
              stroke="hsl(var(--card))"
              strokeWidth="1.5"
            />
          )
        })}

        {/* Current point */}
        <circle cx={cx} cy={cy} r="4.5" fill="hsl(var(--primary))" stroke="hsl(var(--card))" strokeWidth="2" />
      </svg>

      {/* Labels row */}
      <div className="flex justify-between px-1">
        {labels.map((l) => (
          <span key={l} className="text-[10px] text-muted-foreground">
            {l}
          </span>
        ))}
      </div>

      {/* Direction indicator */}
      <div className="flex items-center gap-1.5">
        {direction === "up" ? (
          <TrendingUp className="h-3.5 w-3.5 text-accent" />
        ) : direction === "down" ? (
          <TrendingDown className="h-3.5 w-3.5 text-primary" />
        ) : (
          <Minus className="h-3.5 w-3.5 text-muted-foreground" />
        )}
        <span className="text-xs text-muted-foreground">
          {direction === "up" ? "Trending up" : direction === "down" ? "Trending down" : "Holding steady"}
        </span>
      </div>
    </div>
  )
}
