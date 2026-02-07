# PROXY - Digital Twin Burnout Prevention System

## Project Overview

PROXY is a TartanHacks 2026 hackathon project that visualizes developer burnout through a "Digital Twin" interface. It connects to real workflow data (GitHub & Calendar) via Dedalus MCP and uses a Conway AI decision engine to prevent burnout through a "Cortex vs. Core" intervention system.

**Target Prize Tracks:**
- Conway AI (Decision Support, $1000) - PRIMARY
- Dedalus Labs MCP hosting ($1000) - SECONDARY

**Core Value Proposition:** 
Replace ineffective text warnings about overwork with visceral visual feedback and multi-agent decision conflicts that force acknowledgment of productivity vs. health trade-offs.

---

## Tech Stack & Architecture

### Backend (Python/FastAPI)
- **Runtime:** Python 3.10+
- **Framework:** FastAPI (for REST API)
- **Validation:** Pydantic v2
- **Database:** SQLite (local state persistence)
- **MCP Integration:** Dedalus MCP SDK for GitHub & Calendar
- **LLM:** Anthropic Claude API (for Conway decision engine)

### Frontend (React/Tailwind)
- **Framework:** React 18 with Vite
- **Styling:** Tailwind CSS
- **Animations:** Framer Motion
- **Icons:** Lucide React
- **State Management:** React Context API (keep it simple for hackathon)

### Project Structure
```
proxy/
├── backend/
│   ├── main.py              # FastAPI app, routes
│   ├── models.py            # Pydantic models
│   ├── db.py                # SQLite connection/operations
│   ├── mcp_client.py        # Dedalus MCP integration
│   ├── conway_engine.py     # Multi-agent decision logic
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── TwinAvatar.jsx
│   │   │   ├── TaskStream.jsx
│   │   │   ├── StatsPanel.jsx
│   │   │   └── InterventionModal.jsx
│   │   └── hooks/
│   │       └── useTwinState.js
│   ├── package.json
│   └── vite.config.js
├── CLAUDE.md
└── README.md
```

---

## Coding Standards & Conventions

### General Principles
1. **Ship Fast, Iterate Later:** Prioritize working demo over perfection
2. **Visual Impact > Code Elegance:** The demo needs to WOW judges
3. **Mock First, Integrate Later:** Start with hardcoded data, swap for real APIs incrementally
4. **Comment Implementation TODOs:** Mark where real MCP/LLM calls will go

### Python Standards
- Use type hints everywhere: `def update_hp(twin_id: str, delta: int) -> TwinState`
- Pydantic models for ALL data structures
- FastAPI dependency injection for DB connections
- Async/await for all route handlers (even if not strictly necessary)
- Snake_case for variables/functions, PascalCase for classes

### React Standards
- Functional components only (no class components)
- Custom hooks for state logic (`useTwinState`, `useConwayDecision`)
- Props destructuring: `const InterventionModal = ({ isOpen, onClose, conflict }) => {}`
- Tailwind utility classes inline (no separate CSS files)
- Component file organization: imports → component → export

### Naming Conventions
- **Backend routes:** `/api/twin/state`, `/api/twin/ingest`, `/api/conway/decide`
- **Frontend components:** PascalCase, descriptive (`InterventionModal`, not `Modal`)
- **State variables:** Descriptive, not abbreviated (`healthPoints` not `hp`)
- **Database fields:** snake_case matching Pydantic models

---

## Core Data Models

### TwinState (Pydantic Model)
```python
class TwinState(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    hp: int = Field(default=100, ge=0, le=100)  # Health Points
    xp: int = Field(default=0, ge=0)  # Productivity Points
    status: TwinStatus = TwinStatus.THRIVING
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
class TwinStatus(str, Enum):
    THRIVING = "thriving"      # HP > 70
    STRAINED = "strained"      # HP 30-70
    BURNOUT = "burnout"        # HP < 30
```

### WorkflowEvent (Pydantic Model)
```python
class WorkflowEvent(BaseModel):
    source: EventSource  # github | calendar
    event_type: str  # commit, meeting, sleep
    intensity: int = Field(ge=1, le=10)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
class EventSource(str, Enum):
    GITHUB = "github"
    CALENDAR = "calendar"
```

### ConwayConflict (Pydantic Model)
```python
class ConwayConflict(BaseModel):
    twin_hp: int
    cortex_msg: str  # Logic agent's argument
    core_msg: str    # Biology agent's argument
    recommended_action: str  # "rest" | "override"
    reasoning: str   # Why this conflict occurred
```

---

## Backend Implementation Guide

### 1. FastAPI Route Structure

**Core Endpoints:**
```python
@app.get("/api/twin/state")
async def get_twin_state() -> TwinState:
    """Retrieve current twin state from DB"""
    
@app.post("/api/twin/ingest")
async def ingest_event(event: WorkflowEvent) -> TwinState:
    """Process workflow event and update twin state"""
    
@app.post("/api/conway/decide")
async def trigger_decision(action: str) -> ConwayConflict:
    """Run Conway multi-agent decision when HP is critical"""
```

### 2. HP/XP Update Logic

**Event Impact Rules:**
- **GitHub Commit:** HP -5, XP +10
- **Calendar Meeting:** HP -10, XP +5 (if work-related)
- **Sleep Event:** HP +20, XP +0
- **Deep Work Block:** HP -15, XP +20

**Status Calculation:**
```python
def calculate_status(hp: int) -> TwinStatus:
    if hp > 70:
        return TwinStatus.THRIVING
    elif hp >= 30:
        return TwinStatus.STRAINED
    else:
        return TwinStatus.BURNOUT
```

### 3. Conway Decision Engine Implementation

**When to Trigger:**
- User attempts to schedule meeting when `hp < 30`
- User commits code when `hp < 20`
- Any action when `status == BURNOUT`

**Multi-Agent Prompt Structure:**
```python
# TODO: Replace with actual Claude API call
async def generate_conflict(twin_state: TwinState, attempted_action: str) -> ConwayConflict:
    """
    System Prompt:
    You are two competing AI agents debating a decision:
    
    CORTEX (Logic Agent): Argues for productivity, efficiency, meeting deadlines
    CORE (Biology Agent): Argues for rest, health, long-term sustainability
    
    Current State: HP={twin_state.hp}, XP={twin_state.xp}
    Attempted Action: {attempted_action}
    
    Generate a conflict dialogue where:
    1. Cortex argues why the action should proceed
    2. Core argues why immediate rest is critical
    3. Use technical/systems language (treat human as a machine)
    
    Output JSON with: cortex_msg, core_msg, recommended_action
    """
    # For now, return mock responses based on HP threshold
    pass
```

### 4. Dedalus MCP Integration Points

```python
# mcp_client.py
# TODO: Implement actual Dedalus MCP SDK calls

async def fetch_github_events(username: str, hours: int = 24) -> List[WorkflowEvent]:
    """Fetch recent commits/PRs from GitHub via Dedalus MCP"""
    # Mock for now: return sample events
    pass

async def fetch_calendar_events(hours: int = 24) -> List[WorkflowEvent]:
    """Fetch calendar meetings via Dedalus MCP"""
    # Mock for now: return sample events
    pass
```

---

## Frontend Implementation Guide

### 1. Component Hierarchy

```
App.jsx
└── Dashboard.jsx
    ├── TaskStream.jsx (left sidebar)
    ├── TwinAvatar.jsx (center canvas)
    ├── StatsPanel.jsx (right sidebar)
    └── InterventionModal.jsx (overlay)
```

### 2. TwinAvatar Visual States

**THRIVING State:**
- Background: Gradient green/blue
- Avatar: Emoji 😊 or peaceful animation
- Animations: Gentle floating, breathing effect

**STRAINED State:**
- Background: Gradient yellow/orange
- Avatar: Emoji 😓 or tired animation
- Animations: Slower movements, slight flicker

**BURNOUT State:**
- Background: Red/black, glitch effects
- Avatar: Emoji 💀 or corrupted sprite
- Animations: Shake/glitch using Framer Motion
```jsx
<motion.div
  animate={{
    x: status === 'burnout' ? [0, -5, 5, -5, 5, 0] : 0,
    opacity: status === 'burnout' ? [1, 0.7, 1, 0.7, 1] : 1,
  }}
  transition={{ duration: 0.5, repeat: status === 'burnout' ? Infinity : 0 }}
>
  {/* Avatar content */}
</motion.div>
```

### 3. InterventionModal Design

**Layout:**
```
┌────────────────────────────────────────┐
│   SYSTEM RESOURCE CONFLICT DETECTED    │
├──────────────────┬─────────────────────┤
│   CORTEX 🔷      │      CORE ❤️        │
│   "Execute..."   │   "Shutdown..."     │
├──────────────────┴─────────────────────┤
│  [Override] vs. [Rest]                 │
└────────────────────────────────────────┘
```

**Styling:**
- Modal backdrop: `backdrop-blur-sm bg-black/50`
- Cortex side: Blue geometric theme, sharp edges
- Core side: Red organic theme, rounded shapes
- Buttons: Contrasting colors (blue vs red)

### 4. State Management Pattern

```jsx
// useTwinState.js custom hook
const useTwinState = () => {
  const [twinState, setTwinState] = useState(null);
  const [conflict, setConflict] = useState(null);
  
  const ingestEvent = async (event) => {
    const response = await fetch('/api/twin/ingest', {
      method: 'POST',
      body: JSON.stringify(event),
    });
    const newState = await response.json();
    setTwinState(newState);
    
    // Trigger conflict check if HP is critical
    if (newState.hp < 30) {
      const conflictData = await triggerConwayDecision();
      setConflict(conflictData);
    }
  };
  
  return { twinState, conflict, ingestEvent };
};
```

---

## Development Workflow

### Phase 1: Backend Scaffold (1-2 hours)
1. Set up FastAPI project structure
2. Create Pydantic models (TwinState, WorkflowEvent, ConwayConflict)
3. Implement SQLite DB operations (init, read, update)
4. Build `/api/twin/state` and `/api/twin/ingest` with MOCK data
5. Test with curl/Postman

### Phase 2: Frontend Scaffold (1-2 hours)
1. Set up Vite + React + Tailwind project
2. Build Dashboard layout (3-column grid)
3. Create TwinAvatar with THREE status states (use emojis/divs)
4. Implement StatsPanel with mock HP/XP bars
5. Test state transitions with hardcoded values

### Phase 3: Integration (1-2 hours)
1. Connect frontend to backend API
2. Implement `useTwinState` hook
3. Wire up TaskStream drag-and-drop to trigger `/ingest`
4. Test full flow: drag task → HP changes → avatar updates

### Phase 4: Conway Engine (2-3 hours)
1. Implement Conway decision endpoint (`/api/conway/decide`)
2. Integrate Claude API for multi-agent conflict generation
3. Build InterventionModal component
4. Test conflict triggers and resolution

### Phase 5: MCP Integration (2-3 hours)
1. Set up Dedalus MCP SDK
2. Replace mock GitHub events with real MCP calls
3. Replace mock Calendar events with real MCP calls
4. Add sync button to pull latest workflow data

### Phase 6: Polish & Demo (2-3 hours)
1. Add Framer Motion animations (glitch effects, smooth transitions)
2. Create demo script with realistic scenario
3. Record demo video showing full flow
4. Write README with screenshots
5. Deploy (Vercel frontend + Railway/Render backend)

---

## Demo Script for Judges

**Setup:** Show dashboard in THRIVING state (HP: 85)

**Act 1 - The Grind:**
1. Drag "Fix Critical Bug" task → HP drops to 70 (STRAINED)
2. Drag "Team Standup" task → HP drops to 55
3. Drag "Write Documentation" task → HP drops to 40
4. Avatar starts looking tired, stats panel turns yellow

**Act 2 - The Breaking Point:**
1. Attempt to drag "Client Meeting" task → HP would drop to 25 (BURNOUT)
2. **INTERVENTION MODAL POPS UP**
3. **Cortex:** "Meeting efficiency +15%. Sleep is optional. Execute."
4. **Core:** "Biological fuel critical. Hardware damage imminent. Shutdown required."

**Act 3 - The Choice:**
- **Option A (Override):** HP drops to 25, avatar glitches violently, XP +5
- **Option B (Rest):** HP restored to 60, avatar calms down, XP +0

**Closing:** 
"Unlike text warnings you ignore, PROXY makes burnout VISIBLE and forces you to acknowledge the trade-off."

---

## Key Hackathon Strategies

### For Conway AI Track:
- Emphasize the MULTI-AGENT conflict (Cortex vs Core)
- Use technical systems language in agent dialogue
- Show how it aids decision-making (not just warns)
- Highlight the "System Resource Conflict" framing

### For Dedalus MCP Track:
- Showcase MULTIPLE MCP integrations (GitHub + Calendar)
- Demonstrate real-time data syncing
- Build a compelling use case for MCP hosting
- Show how MCP enables seamless workflow integration

### General Tips:
- **Visual > Technical:** Judges remember animations, not code
- **Story > Stats:** The "Cortex vs Core" narrative is the hook
- **Live Demo > Video:** If possible, run it live with real GitHub data
- **Practice Pitch:** 2-minute version that hits all key points

---

## Common Pitfalls to Avoid

1. **Over-engineering:** Don't build user auth or complex DB schemas
2. **API Rate Limits:** Cache MCP responses, don't spam GitHub API
3. **Animation Performance:** Test on slower machines, reduce complexity if laggy
4. **Modal UX:** Make intervention dismissable (don't trap users)
5. **State Sync Issues:** Use optimistic updates on frontend, reconcile later

---

## Testing Checklist

- [ ] Backend: All endpoints return valid JSON
- [ ] Backend: HP/XP calculations are correct
- [ ] Backend: Conway conflict triggers at right thresholds
- [ ] Frontend: Avatar changes reflect all three states
- [ ] Frontend: Intervention modal displays correctly
- [ ] Frontend: Stats panel updates in real-time
- [ ] Integration: Task drag-and-drop updates backend
- [ ] Integration: Modal resolution affects twin state
- [ ] MCP: GitHub events populate correctly
- [ ] MCP: Calendar events populate correctly
- [ ] Demo: Full script runs without errors

---

## Resources & References

**MCP Documentation:**
- Dedalus MCP: [Check MCP marketplace for latest docs]
- GitHub MCP: `@modelcontextprotocol/server-github`
- Calendar MCP: [TBD - may need Google Calendar API fallback]

**Claude API:**
- Anthropic SDK: `pip install anthropic`
- Multi-agent prompting: Use tool_use with structured outputs

**UI Inspiration:**
- Tamagotchi pixel art: Simple, expressive states
- System monitor UIs: Resource bars, status indicators
- Sci-fi interfaces: Tech language, warning overlays

---

## Emergency Fallbacks

**If Dedalus MCP doesn't work:**
- Use GitHub REST API directly (public repos don't need auth)
- Mock calendar events with hardcoded JSON

**If Claude API is slow:**
- Pre-generate 5-10 conflict scenarios
- Return random one based on HP threshold
- Add "Powered by Claude" badge anyway

**If animations lag:**
- Reduce Framer Motion complexity
- Use CSS keyframes instead
- Simplify avatar to emoji-only

**If full-stack is too much:**
- Run backend and frontend on same port
- Use environment variables to toggle mock vs. real data
- Deploy frontend only with mock API responses

---

## Post-Hackathon TODOs

*(Don't implement during hackathon, but note for future)*

- [ ] Add user authentication
- [ ] Persistent twin state across sessions
- [ ] Webhooks for real-time GitHub/Calendar sync
- [ ] Desktop app (Electron wrapper)
- [ ] Slack integration for team burnout monitoring
- [ ] ML model to predict burnout before it happens
- [ ] Mobile app (React Native)
- [ ] Team dashboard (multiple twins)

---

## Questions for Claude Code

When working on this project, ask Claude:

1. **"Generate the complete FastAPI main.py with all endpoints"**
2. **"Create the React Dashboard component with 3-column layout"**
3. **"Write the InterventionModal with Cortex vs Core styling"**
4. **"Implement the HP/XP update logic with all event types"**
5. **"Generate a Conway conflict using Claude API with multi-agent prompting"**
6. **"Create Framer Motion animations for burnout glitch effect"**
7. **"Write integration tests for the /ingest endpoint"**
8. **"Build the MCP client for GitHub events"**

Remember: Be specific, provide context, ask for working code with comments.

---

*Last Updated: 2026-02-07*
*TartanHacks 2026 - Conway AI Track*
