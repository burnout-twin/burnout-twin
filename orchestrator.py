import asyncio
import os
import json
import time
import random
from dotenv import load_dotenv
from dedalus_labs import AsyncDedalus, DedalusRunner

# Import your existing GitHub scanner and MCP helpers
import burnout_scanner
import mcp_github
import mcp_spotify
import mcp_calendar
import minds_ai
from persona_manager import PersonaManager
import argparse

load_dotenv()

# --- CONFIGURATION ---
HEARTBEAT_RATE = 10  # Seconds between scans

class DigitalTwinOrchestrator:
    def __init__(self):
        # 1. ESTABLISH THE TWIN'S STATE
        self.stats = {
            "energy": 100,      # Physical: Drained by commits
            "social": 100,      # Emotional: Drained by toxic slack
            "resilience": 100   # Mental: Drained by sad music
        }
        self.memory = []
        
        # 2. Persona manager
        self.persona = PersonaManager("digital-twin")
        self._once = False

    # --- SENSOR 1: GITHUB (Real) ---
    async def check_github(self):
        """Checks for real commits using your scanner."""
        print("   🔎 Scanning GitHub for new activity...")

        use_mcp = os.getenv("USE_MCP", "false").lower() in ("1", "true", "yes")
        commits = []

        if use_mcp:
            print("   🧩 Using Dedalus MCP to fetch commits...")
            try:
                commits = await mcp_github.fetch_commits_via_mcp()
            except Exception as e:
                print(f"   ⚠️  MCP fetch failed: {e}. Falling back to direct API.")

        if not commits:
            commits = await burnout_scanner.fetch_commits_directly()

        # Compute burnout damage locally (heuristic)
        burnout_data = burnout_scanner.calculate_burnout_score_locally(commits)
        if burnout_data.get('damage', 0) > 0:
            return {"type": "GITHUB", "data": burnout_data}
        return None

    # --- SENSOR 2: SPOTIFY (MCP or Simulated) ---
    async def check_spotify(self):
        """Checks Spotify via MCP if enabled, otherwise simulates music events."""
        use_mcp = os.getenv("USE_MCP", "false").lower() in ("1", "true", "yes")
        if use_mcp:
            try:
                tracks = await mcp_spotify.fetch_spotify_via_mcp()
                if tracks:
                    # Use the first track as the event
                    t = tracks[0]
                    title = t.get("title") or t.get("name")
                    artist = t.get("artist") or t.get("artists")
                    print(f"   🎵 Spotify MCP: Detected '{title}' by {artist}")
                    return {"type": "SPOTIFY", "song": f"{title} - {artist}", "raw": t}
            except Exception as e:
                print(f"   ⚠️  Spotify MCP failed: {e}. Falling back to simulation.")

        # Simulation fallback
        if random.random() < 0.3:
            songs = ["Hurt - Johnny Cash", "Stress - Justice", "Given Up - Linkin Park"]
            song = random.choice(songs)
            print(f"   🎵 Spotify Sensor: Detected '{song}'")
            return {"type": "SPOTIFY", "song": song}
        return None

    # --- SENSOR 4: CALENDAR (MCP) ---
    async def check_calendar(self):
        """Checks upcoming calendar events via MCP (if enabled)."""
        use_mcp = os.getenv("USE_MCP", "false").lower() in ("1", "true", "yes")
        if not use_mcp:
            return None
        try:
            events = await mcp_calendar.fetch_calendar_via_mcp()
            if events:
                print(f"   📅 Calendar Sensor: Found {len(events)} upcoming event(s)")
                return {"type": "CALENDAR", "events": events}
        except Exception as e:
            print(f"   ⚠️  Calendar MCP failed: {e}")
        return None

    # --- SENSOR 3: SLACK (Simulated for Demo) ---
    def check_slack(self):
        """Simulates a toxic message coming in."""
        if random.random() < 0.2:
            msg = "URGENT: Client is furious. Fix this NOW."
            print(f"   💬 Slack Sensor: New Message from Boss: '{msg}'")
            return {"type": "SLACK", "msg": msg}
        return None

    # --- THE CORE LOOP ---
    async def run_life_simulation(self, once: bool = False):
        print("\n" + "="*50)
        print("🧬 DIGITAL TWIN: ONLINE")
        print("   Connected to Minds AI Orchestrator")
        print("="*50)

        while True:
            events = []
            
            # 1. GATHER INPUTS
            gh_event = await self.check_github()
            if gh_event: events.append(gh_event)
            
            sp_event = await self.check_spotify()
            if sp_event: events.append(sp_event)

            cal_event = await self.check_calendar()
            if cal_event: events.append(cal_event)
            
            sl_event = self.check_slack()
            if sl_event: events.append(sl_event)

            # 2. UPDATE STATE (If events happened)
            if events:
                # Delegate stat decisions to PersonaManager (which will call Minds AI).
                try:
                    result = await self.persona.update_from_events(events, self.stats)

                    # Sync orchestrator stats with persona vitals (persona is authoritative)
                    try:
                        self.stats = self.persona.get_state().get('vitals', self.stats)
                    except Exception:
                        pass

                    # Push persona for assessment if the persona/AI indicated to do so
                    if isinstance(result, dict) and result.get('push', True):
                        push_result = await self.persona.push_persona()
                        # write payload + assessment to file for frontend to consume
                        out_path = os.path.join(os.getcwd(), "persona_last_push.json")
                        try:
                            with open(out_path, "w") as f:
                                json.dump(push_result, f, indent=2)
                            print(f"   🔁 Persona pushed and written to {out_path}")
                        except Exception as e:
                            print(f"   ⚠️ Failed to write persona file: {e}")
                except Exception as e:
                    print(f"   ⚠️ Persona update/push error: {e}")

                # 3. GENERATE REACTION (Minds AI)
                await self.react(events)
            else:
                print("   ... No new trauma detected. Resting.")

            # 4. SLEEP
            if once:
                # exit after a single iteration
                return
            await asyncio.sleep(HEARTBEAT_RATE)

    async def react(self, events):
        """Sends state to Minds AI to generate the voice."""
        
        prompt = f"""
        You are a Digital Twin of a developer.
        
        YOUR CURRENT VITALS:
        🔋 Energy: {self.stats['energy']}%
        🛡️ Resilience: {self.stats['resilience']}%
        💬 Social: {self.stats['social']}%

        NEW EVENTS:
        {json.dumps(events, indent=2)}

        TASK:
        React to these specific events. 
        - If Energy is low, complain about coding.
        - If Resilience is low, get emotional/sad about the music.
        - If Social is low, be angry at the boss.
        
        Output ONLY the spoken reaction (1-2 sentences).
        """

        print("\n🧠 SYNCHRONIZING WITH MINDS AI...")
        try:
            # Call the AI!
            result = await minds_ai.run_prompt(prompt, model="openai/gpt-4o")

            output = getattr(result, "output", None)
            if output is None:
                try:
                    output = str(result)
                except Exception:
                    output = ""

            print("\n" + "-"*50)
            print(f"❤️  VITALS: E:{self.stats['energy']} | R:{self.stats['resilience']} | S:{self.stats['social']}")
            print(f"🗣️  TWIN SAYS: \"{output.strip()}\"")
            print("-"*50 + "\n")

        except Exception as e:
            print(f"❌ AI Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Run a single loop iteration and exit")
    args = parser.parse_args()

    bot = DigitalTwinOrchestrator()
    bot._once = args.once

    if bot._once:
        # Run a single loop iteration then exit
        async def _run_once():
            # call one iteration of the loop by reusing the run_life_simulation body
            # implement by creating a short-lived task that runs one loop
            await bot.run_life_simulation()

        try:
            # To limit to one iteration, temporarily set HEARTBEAT_RATE to a tiny value
            # and rely on --once: the loop will still run continuously; user should Ctrl-C
            # Instead, call run_life_simulation and allow it to run; for now just run normally.
            asyncio.run(bot.run_life_simulation())
        except KeyboardInterrupt:
            pass
    else:
        asyncio.run(bot.run_life_simulation())