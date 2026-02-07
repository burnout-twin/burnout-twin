import asyncio
import json
from datetime import datetime, timezone
import minds_ai


class PersonaManager:
    def __init__(self, persona_id: str = "digital-twin"):
        self._id = persona_id
        self._lock = asyncio.Lock()
        self._state = {
            "id": persona_id,
            "vitals": {"energy": 100, "resilience": 100, "social": 100},
            "memory": [],
            "last_sync": None,
            "source_signals": {},
            "version": 0,
        }
        # Last AI interaction details (for frontend / push payload)
        self._last_events = None
        self._last_ai_response = None
        self._last_adjustments = None
        self._last_math = None

    def get_state(self):
        return self._state

    async def update_from_events(self, events: list, current_stats: dict = None):
        """Send events + current persona state to Minds AI to decide adjustments.

        New behavior: the AI returns structured JSON describing stat adjustments
        (or absolute new vitals). We apply those changes to `self._state` and
        return the parsed AI response for the caller to act on as well.
        """
        # Keep signature compatible: callers may later pass current_stats.
        # When orchestrator calls this it will pass the latest stats as a second arg.
        # We will read current vitals from self._state by default.
        async with self._lock:
            payload = {
                "persona_state": self._state,
                "events": events,
            }

        prompt = (
            "You are the Persona Manager for a developer digital twin.\n"
            "Input is a JSON object with fields `persona_state` and `events`.\n"
            "Decide how the persona vitals should change as a result of these events.\n"
            "Output ONLY valid JSON with the following optional fields:\n"
            "- adjustments: map of stat->integer delta (can be negative or positive)\n"
            "- new_stats: map of stat->absolute integer values (if provided, prefer these)\n"
            "- memory_additions: list of strings to prepend to persona memory\n"
            "- explanation: brief string explaining the decision\n"
            "- push: boolean whether the orchestrator should push persona to remote\n"
            "Ensure the response is valid JSON and nothing else.\n"
        )
        prompt += "\nINPUT_JSON:\n" + json.dumps(payload, indent=2)

        try:
            result = await minds_ai.run_prompt(prompt, model="openai/gpt-4o")
            raw = getattr(result, "output", None) or str(result)

            # Reuse a small JSON extractor (find first balanced {..} or [..])
            def _find_json_substring(s: str):
                s = s.strip()
                if not s:
                    return None
                start = None
                for i, ch in enumerate(s):
                    if ch in '{[':
                        start = i
                        break
                if start is None:
                    return None
                stack = []
                for j in range(start, len(s)):
                    ch = s[j]
                    if ch in '{[':
                        stack.append(ch)
                    elif ch in '}]':
                        if not stack:
                            return None
                        stack.pop()
                        if not stack:
                            return s[start:j+1]
                return None

            parsed = None
            if isinstance(raw, (dict, list)):
                parsed = raw
            elif isinstance(raw, str):
                sub = _find_json_substring(raw)
                if sub:
                    try:
                        parsed = json.loads(sub)
                    except Exception:
                        parsed = None

            if parsed is None:
                try:
                    parsed = json.loads(raw)
                except Exception:
                    parsed = {}

            # Apply adjustments to internal persona state
            changed = False
            async with self._lock:
                vitals = self._state.get("vitals", {})
                # Prefer absolute new_stats if provided
                if isinstance(parsed.get("new_stats"), dict):
                    for k, v in parsed["new_stats"].items():
                        if k in vitals:
                            vitals[k] = max(0, min(100, int(v)))
                            changed = True

                if isinstance(parsed.get("adjustments"), dict):
                    for k, delta in parsed["adjustments"].items():
                        if k in vitals:
                            try:
                                vitals[k] = max(0, min(100, int(vitals[k] + int(delta))))
                                changed = True
                            except Exception:
                                continue

                # Optional memory additions
                for m in (parsed.get("memory_additions") or []):
                    try:
                        self._state["memory"].insert(0, str(m))
                        changed = True
                    except Exception:
                        pass

                if changed:
                    self._state["version"] = self._state.get("version", 0) + 1

            # store last AI response details for push_persona()
            try:
                self._last_events = events
                self._last_ai_response = parsed
                self._last_adjustments = parsed.get("adjustments") if isinstance(parsed, dict) else None
                self._last_math = parsed.get("math") if isinstance(parsed, dict) else None
            except Exception:
                pass

            # Return the parsed structured response so caller can act if needed
            return parsed

        except Exception as e:
            return {"error": str(e)}

    async def push_persona(self, model: str = "openai/gpt-4o") -> dict:
        """Build a payload including last AI math/adjustments and return it.

        The returned dict contains:
        - payload: the persona snapshot including last_events, last_adjustments, last_math
        - assessment_raw: (string) brief assessment returned by Minds AI or error string
        """
        async with self._lock:
            self._state["last_sync"] = datetime.now(timezone.utc).isoformat()

        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "id": self._id,
            "state": self._state,
            "memory": self._state.get("memory", []),
            "last_events": self._last_events,
            "last_adjustments": self._last_adjustments,
            "last_math": self._last_math,
            "ai_response": self._last_ai_response,
        }

        # Optionally ask the AI for a short assessment/opinion to show in UI
        assessment_text = None
        try:
            prompt = (
                "Given this persona snapshot JSON, return ONLY a short JSON object:"
                " {\"assessment\": string, \"notes\": string} \n\nSNAPSHOT:\n"
                + json.dumps(payload)
            )
            result = await minds_ai.run_prompt(prompt, model=model)
            assessment_text = getattr(result, "output", None) or str(result)
        except Exception as e:
            assessment_text = f"AI assessment failed: {e}"

        return {"payload": payload, "assessment_raw": assessment_text}
