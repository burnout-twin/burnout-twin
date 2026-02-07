# PROXY - Digital Twin Burnout Prevention System

## Project Overview (updated)

PROXY is a TartanHacks 2026 project that visualizes developer burnout via a "Digital Twin". It ingests workflow signals (GitHub commits, Spotify, Calendar) via Dedalus MCP adapters and uses an AI-driven Persona Manager to decide how the twin's vitals should change.

Core change: stat updates are now decided by the PersonaManager (AI). The orchestrator aggregates sensor inputs and delegates the decision about how much to increase/decrease vitals to Minds AI via the PersonaManager.

---

## High-level Architecture (current)

- `orchestrator.py`: central loop — polls sensors (MCP wrappers or local fallbacks), aggregates events, forwards them to `PersonaManager`, and asks `minds_ai` for reactive voice output.
- `persona_manager.py`: authoritative persona state; sends `persona_state + events` to Minds AI and applies returned `adjustments` or `new_stats` (structured JSON).
- `mcp_github.py`, `mcp_spotify.py`, `mcp_calendar.py`: small adapter modules that call Dedalus MCPs via `minds_ai.run_prompt(..., mcp_servers=[...])` and return parsed lists.
- `burnout_scanner.py`: direct GitHub fetcher and local heuristics; kept as a fallback for reliability.
- `minds_ai.py`: Dedalus runner wrapper used by both MCP adapters and persona manager.

Key policy: MCPs are external services invoked by the Dedalus runner. Orchestrator aggregates MCP outputs locally rather than wiring MCP-to-MCP in-repo.

---

## New PersonaManager Contract (what the AI should return)

When `persona_manager.update_from_events()` calls Minds AI it sends a JSON payload with fields `persona_state` and `events` and instructs the model to return ONLY valid JSON with any of these fields:

- `adjustments`: {"energy": -10, "resilience": +5, "social": -20}  (deltas to apply)
- `new_stats`: {"energy": 80, "resilience": 90, "social": 70}  (absolute replacements; preferred if present)
- `memory_additions`: ["GitHub: Fixed panic at 3AM"]  (strings to prepend to persona memory)
- `explanation`: "Because of repeated night commits..."  (human-readable rationale)
- `push`: true|false  (whether orchestrator should call `push_persona()` / request assessment)

Notes:
- Vitals are clamped to 0..100 after applying adjustments or new_stats.
- The orchestrator treats `persona_manager` as authoritative for `vitals`.

---

## How to Run (local dev)

Environment vars (recommended):

```bash
export USE_MCP=true           # enable MCP adapters (otherwise fallbacks run)
export DEDALUS_API_KEY=...    # Dedalus API key for Minds/Dedalus runner
export GITHUB_TOKEN=...      # fallback direct GitHub API fetch
```

Run a single loop iteration:

```bash
python3 orchestrator.py --once
```

Behavior notes:
- If `USE_MCP=true` the orchestrator will prefer MCP wrappers (`mcp_github`, `mcp_spotify`, `mcp_calendar`) which use Dedalus MCP servers specified inside those modules.
- If an MCP call fails, the orchestrator falls back to local logic (e.g., `burnout_scanner.fetch_commits_directly()`).

---

## Developer Guidance: Prompting & Robustness

- Keep prompts strict and include the exact JSON schema expected. Ask the model to "output ONLY valid JSON" to reduce parsing work.
- Use small helper to extract the first balanced JSON object from model output (implemented in `persona_manager.py`).
- Use `minds_ai.run_prompt()` for both MCP invocations and persona prompts — it wraps DedalusRunner and supports `mcp_servers`.
- Add retries and timeouts at network boundaries if needed.

---

## Files of Interest (repo)

- `orchestrator.py` — main loop & sensors
- `persona_manager.py` — AI-driven persona + JSON contract
- `mcp_github.py`, `mcp_spotify.py`, `mcp_calendar.py` — MCP adapters
- `burnout_scanner.py` — direct GitHub fallback and local heuristics
- `minds_ai.py` — Dedalus runner wrapper

Removed: `run.py` (demo script removed to keep repo focused on orchestrator flow).

---

## Quick Dev Tasks / Next Improvements

1. Harden JSON parsing: validate required keys and types, set defaults when missing.
2. Add unit tests for `persona_manager.update_from_events()` using mocked `minds_ai.run_prompt()` responses.
3. Add a debug mode that logs raw model outputs to a file for later prompt-engineering.
4. Optional: add a small REST wrapper to expose `persona_state` for a frontend prototype.

---

If you'd like, I can also:

- Add a sample prompt that yields conservative adjustments (small deltas) for safer behavior.
- Generate unit tests and a `requirements.txt` for CI.

Pick one and I'll implement it next.


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
