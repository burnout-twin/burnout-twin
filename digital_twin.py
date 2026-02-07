import asyncio
import os
import json
import httpx
import random
import time
from datetime import datetime
from dotenv import load_dotenv
from dedalus_labs import AsyncDedalus, DedalusRunner

load_dotenv()

# --- CONFIGURATION ---
TARGET_REPO = "nishsm/sample-burnout-repo" 
POLL_INTERVAL = 5  # Seconds between checks

# ==========================================
# 1. SENSORS (The Senses)
# ==========================================
class SensorSuite:
    def __init__(self):
        self.last_commit_sha = None
        self.current_song = None
    
    async def check_github(self):
        """Polls GitHub for NEW commits only."""
        token = os.getenv("GITHUB_TOKEN")
        url = f"https://api.github.com/repos/{TARGET_REPO}/commits?per_page=1"
        headers = {"Authorization": f"token {token}"}
        
        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(url, headers=headers)
                if res.status_code == 200:
                    data = res.json()[0]
                    sha = data['sha']
                    # Only report if it's a NEW commit we haven't seen
                    if self.last_commit_sha and sha != self.last_commit_sha:
                        self.last_commit_sha = sha
                        return {
                            "type": "COMMIT",
                            "msg": data['commit']['message'],
                            "time": data['commit']['author']['date']
                        }
                    self.last_commit_sha = sha
        except:
            pass
        return None

    def check_spotify(self):
        """
        Simulates Spotify Data (since real OAuth is too slow for a 2min demo).
        It rotates songs to show the AI reacting to your mood.
        """
        # In a real app, this would hit the Spotify API.
        # For the hackathon, we simulate the "Burnout Playlist" progression.
        songs = [
            {"track": "Lofi Study Beats", "vibe": "Neutral"},
            {"track": "Stress (Justice)", "vibe": "High Anxiety"},
            {"track": "Hurt (Johnny Cash)", "vibe": "Depressive"},
            {"track": "Silence", "vibe": "Numb"}
        ]
        # Change song every 15 seconds for the demo
        index = int(time.time() / 15) % len(songs)
        new_song = songs[index]
        
        if new_song != self.current_song:
            self.current_song = new_song
            return {"type": "SPOTIFY", "track": new_song['track'], "vibe": new_song['vibe']}
        return None

# ==========================================
# 2. DIGITAL TWIN (The Persistence)
# ==========================================
class DigitalTwin:
    def __init__(self):
        # The Twin starts healthy
        self.stats = {"energy": 100, "social": 100, "resilience": 100}
        self.memory = [] 
        self.status = "ONLINE"

    def process_event(self, event):
        """Ingests a new event and updates stats immediately."""
        if not event:
            return False

        print(f"\n⚡ DETECTED EVENT: {event}")
        
        if event['type'] == 'COMMIT':
            # Commits drain energy
            self.stats['energy'] -= 15
            self.memory.append(f"Work: Committed '{event['msg']}'")
            
        elif event['type'] == 'SPOTIFY':
            # Music affects Mood (Resilience)
            if event['vibe'] == "Depressive":
                self.stats['resilience'] -= 20
                self.memory.append(f"Music: Listening to sad song '{event['track']}'")
            elif event['vibe'] == "High Anxiety":
                self.stats['energy'] -= 10
                self.stats['resilience'] -= 10
                self.memory.append(f"Music: Stressful song '{event['track']}'")
            else:
                self.memory.append(f"Music: Vibe shift to '{event['track']}'")

        # Clamp stats
        for k in self.stats:
            self.stats[k] = max(0, int(self.stats[k]))
            
        return True # Return True if we need to speak

    async def speak(self):
        """Reacts to the accumulated trauma."""
        api_key = os.getenv("DEDALUS_API_KEY")
        client = AsyncDedalus(
            api_key=api_key,
            base_url=os.getenv("DEDALUS_API_URL", "https://api.dedaluslabs.ai"),
            as_base_url=os.getenv("DEDALUS_AS_URL", "https://as.dedaluslabs.ai")
        )
        runner = DedalusRunner(client)

        prompt = f"""
        You are a Digital Twin of a developer. 
        You are currently running on a server, monitoring their life.

        CURRENT VITALS:
        🔋 Energy: {self.stats['energy']}%
        🛡️ Resilience: {self.stats['resilience']}%

        LATEST EVENT:
        {self.memory[-1] if self.memory else "None"}

        TASK:
        React to this specific event based on your stats.
        - If listening to sad music: Get emotional.
        - If coding: Complain about being tired.
        - Keep it very short (1 sentence). 
        """
        
        try:
            # We use the faster model for the loop
            result = await runner.run(input=prompt, model="openai/gpt-4o")
            return result.output.strip()
        except:
            return "..."

# ==========================================
# 3. THE SERVER LOOP (The Heartbeat)
# ==========================================
async def run_server():
    twin = DigitalTwin()
    sensors = SensorSuite()
    
    print("\n" + "="*50)
    print("🖥️  DIGITAL TWIN SERVER: ONLINE")
    print("📡  Listening for GitHub & Spotify events...")
    print("="*50)

    # Infinite "Game Loop"
    while True:
        # 1. Poll Sensors
        github_event = await sensors.check_github()
        spotify_event = sensors.check_spotify()
        
        # 2. Update Twin
        should_speak = False
        if twin.process_event(github_event): should_speak = True
        if twin.process_event(spotify_event): should_speak = True
        
        # 3. React (If something happened)
        if should_speak:
            print(f"   [VITALS] Energy: {twin.stats['energy']}% | Resilience: {twin.stats['resilience']}%")
            reaction = await twin.speak()
            print(f"   🗣️  TWIN: \"{reaction}\"")
            print("-" * 50)

        # 4. Wait (Heartbeat)
        await asyncio.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        print("\n\n🛑 SERVER SHUTDOWN.")