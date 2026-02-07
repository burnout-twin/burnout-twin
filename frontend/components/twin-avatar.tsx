"use client"

export type StressBand = "Calm" | "Focused" | "Strained" | "Overloaded"

const bandColor: Record<StressBand, string> = {
  Calm: "bg-primary/20 text-primary",
  Focused: "bg-[hsl(220_60%_55%/0.15)] text-[hsl(220_60%_55%)]",
  Strained: "bg-accent/20 text-accent",
  Overloaded: "bg-destructive/20 text-destructive",
}

export function TwinAvatar({
  band = "Calm",
  src = "/avatar-happy.png",
}: {
  band?: StressBand
  src?: string
}) {
  return (
    <div className="flex flex-col items-center gap-4">
      <div className="relative flex items-center justify-center">
        <img
          src={src}
          alt={`Avatar showing ${band} state`}
          className="h-64 w-64 rounded-full object-cover"
        />
      </div>

      {/* State label */}
      <span className={`rounded-full px-4 py-1.5 text-sm font-semibold ${bandColor[band]}`}>
        {band}
      </span>
    </div>
  )
}
