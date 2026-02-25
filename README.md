# Screenshot Synchronizer

A macOS tool that captures screenshots with a global hotkey, analyzes them with Google Gemini Vision AI, and streams the results to any browser on your local network in real time.

**Primary use case:** View and get AI analysis of your Mac screen on your iPhone — without AirDrop, iCloud, or any cloud relay.

---

## Features

- **One-key capture** — press `Cmd+Shift+P` anywhere on macOS to trigger a screenshot
- **AI-powered analysis** — each screenshot is automatically sent to Google Gemini 2.5 Flash for analysis using a customizable prompt
- **Live push to mobile** — results appear on any connected browser over Wi-Fi or Personal Hotspot via WebSocket
- **Markdown rendering** — AI responses render with syntax-highlighted code blocks in the browser UI

## Requirements

| Requirement | Detail |
|---|---|
| Operating System | macOS (requires the built-in `screencapture` command) |
| Python | 3.7 or later |
| Google Gemini API Key | [Get one free at Google AI Studio](https://aistudio.google.com/app/apikey) |

## Installation

**1. Clone the repository**

```bash
git clone https://github.com/mingqianyu0524/screenshot_syncronizer.git
cd screenshot_syncronizer
```

**2. Create and activate a virtual environment**

```bash
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies**

```bash
pip install flask flask-socketio python-socketio python-engineio \
            setproctitle pynput python-dotenv google-genai Pillow
```

## Configuration

Create a `.env` file in the project root:

```bash
touch .env
```

Add the following variables:

```env
# Required — your Google Gemini API key
GEMINI_API_KEY=your_google_gemini_api_key_here

# Optional — the prompt sent to Gemini with each screenshot
# Defaults to "Explain what is in this image" if not set
PROMPT=Describe what is on this screen in detail.
```

> **Note:** The `.env` file is gitignored and will never be committed.

## Usage

### Starting the server

**Interactive mode** (logs printed to terminal):

```bash
source venv/bin/activate
python main.py
```

**Silent / background mode** (logs written to `nohup.out`):

```bash
./run_silent.sh
```

> If you cloned the project to a different location, update the hardcoded path inside `run_silent.sh` before using it.

### Stopping the server

```bash
./kill_script.sh
```

### Capturing a screenshot

With the server running, press **`Cmd+Shift+P`** on your Mac. The screenshot will be captured, analyzed by Gemini, and pushed to all connected browsers within a few seconds.

Press **`ESC`** to stop the keyboard listener (without stopping the server).

### Viewing results on your iPhone

**Option A — Same Wi-Fi network**

1. Find your Mac's local IP address:
   ```bash
   ipconfig getifaddr en0
   ```
2. Open this URL in your iPhone browser:
   ```
   http://<your-mac-ip>:5050
   ```

**Option B — iPhone Personal Hotspot**

1. Find your Mac's hostname in **System Settings → General → Sharing → Local Hostname** (e.g., `MacBook-Pro.local`)
2. Open this URL in your iPhone browser:
   ```
   http://<your-mac-hostname>:5050
   ```

## How It Works

```
[Cmd+Shift+P]
     │
     ▼
 client.py  ──── screencapture ──── resources/screenshot_*.png
     │                                        │
     │                              Google Gemini Vision API
     │                                        │
     └──── Socket.IO (broadcast_event) ──▶ server.py
                                              │
                                   Socket.IO (update_content)
                                              │
                                             ▼
                                      iPhone Browser
                               (screenshot + AI analysis)
```

Screenshots are saved locally to the `resources/` directory and are never uploaded anywhere except to the Gemini API for analysis.

## Project Structure

```
screenshot_syncronizer/
├── main.py           # Starts server.py and client.py as subprocesses
├── server.py         # Flask + Socket.IO server (port 5050)
├── client.py         # Hotkey listener, screenshot capture, and Socket.IO client
├── llm.py            # Google Gemini Vision API wrapper
├── run_silent.sh     # Launches main.py in the background
├── kill_script.sh    # Terminates all running service processes
├── templates/
│   └── index.html    # Browser UI (screenshot + Markdown AI response)
└── resources/        # Auto-created; stores captured PNG screenshots
```
