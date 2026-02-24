# CLAUDE.md

This file provides guidance for AI assistants working with the `screenshot_syncronizer` codebase.

## Project Overview

**screenshot_syncronizer** is a macOS productivity tool that captures screenshots on a Mac and streams them — along with AI-powered analysis — to a mobile browser (or any HTTP client) over a local network.

**Core workflow:**
1. User presses `Cmd+Shift+P` on macOS
2. A screenshot is captured using the native `screencapture` command
3. The image is sent to the Google Gemini Vision API for analysis
4. The screenshot and AI-generated text are pushed in real time to a connected browser (e.g., iPhone Safari) via WebSocket

## Repository Structure

```
screenshot_syncronizer/
├── main.py              # Process orchestrator — spawns server.py and client.py as subprocesses
├── server.py            # Flask + Socket.IO web server (port 5050)
├── client.py            # Keyboard listener, screenshot capture, and Socket.IO client
├── llm.py               # Google Gemini Vision API integration
├── run_silent.sh        # Launch main.py as a background process (nohup)
├── kill_script.sh       # Terminate all running service processes by name
├── Readme.md            # QuickStart guide
├── templates/
│   └── index.html       # Browser UI — displays screenshots and AI analysis in real time
└── resources/           # Auto-created at runtime; stores captured PNG screenshots
```

## File Roles

### `main.py`
- Entry point for the entire system
- Spawns `server.py` and `client.py` as child subprocesses using `subprocess.Popen`
- Uses `sys.executable` to ensure the correct Python interpreter (from venv) is used
- Waits 2 seconds after starting the server before launching the client (startup ordering dependency)
- Handles `Ctrl+C` by terminating both subprocesses gracefully via `.terminate()`

### `server.py`
- Flask web server listening on `0.0.0.0:5050` (all interfaces, required for LAN access)
- Uses Flask-SocketIO to receive `broadcast_event` messages from `client.py` and re-emit them as `update_content` to all connected browsers
- Serves the web UI at `/` and screenshot images under `/images/<filename>` from the `resources/` directory
- CORS is unrestricted (`cors_allowed_origins="*"`) to allow cross-origin access from mobile browsers
- Sets its process title to `SysAudioDaemon` via `setproctitle` for process identification

### `client.py`
- Sets its process title to `SysInputHelper` via `setproctitle`
- Loads `.env` for `GEMINI_API_KEY` and `PROMPT` environment variables
- Monitors global keyboard input using `pynput` for the hotkey `Cmd+Shift+P`
- On hotkey trigger: captures a screenshot (timestamped filename), calls `llm.analyze_image()`, then emits a `broadcast_event` Socket.IO message to the local server
- `ESC` key stops the keyboard listener and exits `client.py`
- Connects to the server at `http://localhost:5050`

### `llm.py`
- Wraps the `google-genai` SDK (`google.genai.Client`)
- `analyze_image(image_path, prompt)` is the sole public function
- Uses model `gemini-2.5-flash`
- Opens the image with Pillow (`PIL.Image`) and passes it directly as a multimodal content item alongside the prompt string
- Returns the response text, or an error string on failure
- Reads `GEMINI_API_KEY` from environment via `python-dotenv`

### `templates/index.html`
- Pure frontend, no build step required
- Loads Socket.IO 4.x, markdown-it, and highlight.js from CDNs
- On `update_content` event: updates the displayed screenshot image (with cache-busting timestamp) and renders the AI response text as Markdown with syntax-highlighted code blocks
- Styled for mobile (Apple system fonts, card layout)

## Environment Setup

### Prerequisites
- macOS (required — depends on `screencapture` command)
- Python 3.7+

### Required Python packages

Install into a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install flask flask-socketio python-socketio python-engineio setproctitle pynput python-dotenv google-genai Pillow
```

### Environment variables

Create a `.env` file in the project root (it is gitignored):

```
GEMINI_API_KEY=your_google_gemini_api_key_here
PROMPT=Describe what is on this screen in detail.
```

- `GEMINI_API_KEY` — required; used by `llm.py` to authenticate with the Gemini API
- `PROMPT` — optional; if unset, `client.py` passes `None`, and `llm.py` defaults to `"Explain what is in this image"`

## Running the Project

### Start (interactive, with logs)
```bash
source venv/bin/activate
python main.py
```

### Start (background/silent)
```bash
./run_silent.sh
```
Note: `run_silent.sh` hardcodes an absolute path (`/Users/myu/Desktop/screenshot_syncronizer`). Update this path if cloned elsewhere.

### Stop all processes
```bash
./kill_script.sh
```
This uses `pkill -f` to kill processes by their `setproctitle` names (`SysAudioDaemon`, `SysInputHelper`) and `main.py`.

### Access the UI
- **Same network (Wi-Fi):** `http://<mac-ip>:5050` — find your IP with `ipconfig getifaddr en0`
- **iPhone hotspot:** `http://<mac-hostname>:5050` — find hostname in System Settings → Sharing

## Inter-Process Communication

```
client.py  ──(Socket.IO emit: broadcast_event)──▶  server.py  ──(Socket.IO emit: update_content)──▶  browser
```

- `client.py` acts as a Socket.IO **client** connecting to the local server on port 5050
- `server.py` relays the event to all **browser** clients connected to the same Socket.IO namespace
- The server does not process or transform the data; it is a pure relay

## Screenshot Storage

- Screenshots are stored in `resources/` as `screenshot_YYYYMMDD_HHMMSS.png`
- The `resources/` directory is auto-created by both `server.py` and `client.py` on startup
- PNG files are gitignored (`.gitignore` contains `*.png`)
- Old screenshots are never automatically deleted; manual cleanup is required

## Key Conventions

- **No requirements.txt** — dependencies are managed manually with a local `venv/`; the `venv/` directory is gitignored
- **Comments are in Chinese** — the codebase uses Chinese for inline comments and print statements; maintain this style when modifying existing files
- **No test suite** — there are no automated tests; `llm.py` has a manual `if __name__ == "__main__"` test block
- **No configuration file** — all configuration is via `.env` and hardcoded constants within each file (e.g., `SERVER_URL = 'http://localhost:5050'`, `port=5050`)
- **Process naming** — `server.py` and `client.py` use `setproctitle` to disguise themselves; `kill_script.sh` relies on these names to terminate processes
- **Single namespace Socket.IO** — both `broadcast_event` and `update_content` are on the default namespace

## Important Constraints

- **macOS only** — `client.py` calls `screencapture`, a macOS-exclusive command; the project will not work on Linux or Windows without modification
- **`run_silent.sh` contains a hardcoded path** — must be updated if the project is moved or cloned to a different location
- **Port 5050 is hardcoded** — in `server.py` (`socketio.run(..., port=5050)`) and `client.py` (`SERVER_URL = 'http://localhost:5050'`); change both if the port needs to be different
- **No authentication** — the web server has no authentication; anyone on the local network can view screenshots and AI analysis
- **`allow_unsafe_werkzeug=True`** — `server.py` sets this flag to allow the development Werkzeug server to run in a threaded/production-like mode; this is not suitable for internet-facing deployment
