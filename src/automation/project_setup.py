"""
Project Setup Module
====================
Creates starter React and Flask projects from the config.json settings.

Supported workflows:
- React project: React frontend + Express backend
- Flask project: React frontend + Flask backend

The voice assistant asks for the project folder name, creates the project
under the configured Desktop base path, installs dependencies, starts the
servers, and returns the URLs so the main app can open them in the browser.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from textwrap import dedent
from urllib.error import URLError
from urllib.request import urlopen

from src.core.logger import setup_logger

logger = setup_logger(__name__)

_DEFAULT_DESKTOP_BASE = Path.home() / "Desktop"
_DEFAULT_FRONTEND_PORT = 5173
_DEFAULT_BACKEND_PORT = 5000


class ProjectSetup:
    """Create and launch starter project structures."""

    DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "config.json"

    def __init__(self, config_path=None):
        self.config_path = Path(config_path) if config_path else self.DEFAULT_CONFIG_PATH
        logger.info(f"ProjectSetup initialized (config: {self.config_path})")

    def setup_project(self, project_type, project_name):
        """
        Set up a project on the Desktop using the configured base folder.

        Args:
            project_type: 'react' or 'flask'
            project_name: Folder name to create under the Desktop base path

        Returns:
            dict with success, error, steps, project_path, urls
        """
        steps = []
        project_type = (project_type or "").strip().lower()
        sanitized_name = self._sanitize_folder_name(project_name)

        if not sanitized_name:
            return {
                "success": False,
                "error": "Project folder name cannot be empty",
                "steps": ["❌ Project folder name cannot be empty"],
            }

        config, error = self._load_config()
        if error:
            return {
                "success": False,
                "error": error,
                "steps": [f"❌ Config error: {error}"],
            }

        cfg = config.get("project_setup", {})
        desktop_base = Path(cfg.get("desktop_base_path", str(_DEFAULT_DESKTOP_BASE))).expanduser()
        frontend_port = self._safe_int(cfg.get("frontend_port", _DEFAULT_FRONTEND_PORT), _DEFAULT_FRONTEND_PORT)
        backend_port = self._safe_int(cfg.get("backend_port", _DEFAULT_BACKEND_PORT), _DEFAULT_BACKEND_PORT)

        if not desktop_base.exists():
            return {
                "success": False,
                "error": f"Desktop base path not found: {desktop_base}",
                "steps": [f"❌ Desktop base path not found: {desktop_base}"],
            }

        project_root = desktop_base / sanitized_name
        if project_root.exists() and any(project_root.iterdir()):
            return {
                "success": False,
                "error": f"Target folder already exists and is not empty: {project_root}",
                "steps": [f"❌ Target folder already exists and is not empty: {project_root}"],
            }

        project_root.mkdir(parents=True, exist_ok=True)
        steps.append(f"✅ Created project folder: {project_root}")

        print("\n" + "=" * 70)
        print(f"🛠️  STARTING {project_type.upper()} PROJECT SETUP")
        print("=" * 70)
        print(f"   📁 Base folder: {desktop_base}")
        print(f"   📂 Project folder: {project_root}")
        print(f"   🌐 Frontend port: {frontend_port}")
        print(f"   🔌 Backend port: {backend_port}")

        if project_type == "react":
            result = self._setup_react_project(project_root, frontend_port, backend_port)
        elif project_type == "flask":
            result = self._setup_flask_project(project_root, frontend_port, backend_port)
        else:
            return {
                "success": False,
                "error": f"Unsupported project type: {project_type}",
                "steps": [f"❌ Unsupported project type: {project_type}"],
            }

        result["steps"] = steps + result.get("steps", [])
        result["project_path"] = str(project_root)
        return result

    def validate_config(self):
        """Print the project_setup config block for debugging."""
        config, error = self._load_config()
        if error:
            print(f"[ERROR] {error}")
            return False

        cfg = config.get("project_setup", {})
        print("\n[CONFIG VALIDATION — project_setup]")
        print("-" * 60)
        for key in ("desktop_base_path", "frontend_port", "backend_port"):
            value = cfg.get(key, "")
            print(f"  {key:<20s}: {value if value else '(not configured)'}")
        print("-" * 60)
        return True

    def _setup_react_project(self, project_root, frontend_port, backend_port):
        steps = []
        frontend_dir = project_root / "frontend"
        backend_dir = project_root / "backend"

        if not self._command_exists("node") or not self._command_exists("npm"):
            return {
                "success": False,
                "error": "Node.js and npm are required for React project setup",
                "steps": ["❌ Node.js and npm are required for React project setup"],
            }

        self._create_directory(frontend_dir)
        self._create_directory(backend_dir)
        steps.append("✅ Created React frontend/backend folders")

        self._write_file(frontend_dir / "package.json", self._react_frontend_package_json(project_root.name, frontend_port, backend_port))
        self._write_file(frontend_dir / "vite.config.js", self._react_vite_config(frontend_port, backend_port))
        self._write_file(frontend_dir / "index.html", self._react_index_html(project_root.name))
        self._create_directory(frontend_dir / "src")
        self._write_file(frontend_dir / "src" / "main.jsx", self._react_frontend_main())
        self._write_file(frontend_dir / "src" / "App.jsx", self._react_frontend_app(project_root.name))
        self._write_file(frontend_dir / "src" / "index.css", self._react_frontend_css())
        steps.append("✅ Created React frontend files")

        self._write_file(backend_dir / "package.json", self._express_package_json())
        self._write_file(backend_dir / "server.js", self._express_server_js(backend_port))
        steps.append("✅ Created Express backend files")

        install_backend = self._run_command("npm install", backend_dir, "Installing Express backend dependencies")
        steps.append(install_backend)
        if not install_backend.startswith("✅"):
            return self._build_failure("Backend dependency installation failed", steps)

        install_frontend = self._run_command("npm install", frontend_dir, "Installing React frontend dependencies")
        steps.append(install_frontend)
        if not install_frontend.startswith("✅"):
            return self._build_failure("Frontend dependency installation failed", steps)

        backend_start = self._start_process("npm run dev", backend_dir, "Starting Express backend")
        steps.append(backend_start)
        if not backend_start.startswith("✅"):
            return self._build_failure("Could not start Express backend", steps)

        backend_url = f"http://127.0.0.1:{backend_port}/api/health"
        if not self._wait_for_url(backend_url, timeout=60):
            return self._build_failure("Express backend did not become ready in time", steps)
        steps.append(f"✅ Backend is responding at {backend_url}")

        frontend_start = self._start_process("npm run dev", frontend_dir, "Starting React frontend")
        steps.append(frontend_start)
        if not frontend_start.startswith("✅"):
            return self._build_failure("Could not start React frontend", steps)

        frontend_url = f"http://127.0.0.1:{frontend_port}"
        if not self._wait_for_url(frontend_url, timeout=90):
            return self._build_failure("React frontend did not become ready in time", steps)
        steps.append(f"✅ Frontend is responding at {frontend_url}")

        print("\n✅ React project setup complete")
        print("   Frontend URL:", frontend_url)
        print("   Backend URL:", backend_url)
        return {
            "success": True,
            "error": None,
            "steps": steps,
            "urls": {
                "frontend": frontend_url,
                "backend": backend_url,
            },
        }

    def _setup_flask_project(self, project_root, frontend_port, backend_port):
        steps = []
        frontend_dir = project_root / "frontend"
        backend_dir = project_root / "backend"

        python_executable = self._python_executable()
        if not python_executable:
            return {
                "success": False,
                "error": "Python is required for Flask project setup",
                "steps": ["❌ Python is required for Flask project setup"],
            }

        if not self._command_exists("node") or not self._command_exists("npm"):
            return {
                "success": False,
                "error": "Node.js and npm are required for the React frontend",
                "steps": ["❌ Node.js and npm are required for the React frontend"],
            }

        self._create_directory(frontend_dir)
        self._create_directory(backend_dir)
        steps.append("✅ Created Flask frontend/backend folders")

        self._write_file(frontend_dir / "package.json", self._react_frontend_package_json(project_root.name, frontend_port, backend_port))
        self._write_file(frontend_dir / "vite.config.js", self._react_vite_config(frontend_port, backend_port))
        self._write_file(frontend_dir / "index.html", self._react_index_html(project_root.name))
        self._create_directory(frontend_dir / "src")
        self._write_file(frontend_dir / "src" / "main.jsx", self._react_frontend_main())
        self._write_file(frontend_dir / "src" / "App.jsx", self._react_frontend_app(project_root.name, backend_label="Flask backend"))
        self._write_file(frontend_dir / "src" / "index.css", self._react_frontend_css())
        steps.append("✅ Created React frontend files")

        self._write_file(backend_dir / "requirements.txt", self._flask_requirements())
        self._write_file(backend_dir / "app.py", self._flask_app_py(backend_port, project_root.name))
        steps.append("✅ Created Flask backend files")

        install_backend = self._run_command(f'"{python_executable}" -m pip install -r requirements.txt', backend_dir, "Installing Flask backend dependencies")
        steps.append(install_backend)
        if not install_backend.startswith("✅"):
            return self._build_failure("Flask backend dependency installation failed", steps)

        install_frontend = self._run_command("npm install", frontend_dir, "Installing React frontend dependencies")
        steps.append(install_frontend)
        if not install_frontend.startswith("✅"):
            return self._build_failure("React frontend dependency installation failed", steps)

        backend_start = self._start_process(f'"{python_executable}" app.py', backend_dir, "Starting Flask backend")
        steps.append(backend_start)
        if not backend_start.startswith("✅"):
            return self._build_failure("Could not start Flask backend", steps)

        backend_url = f"http://127.0.0.1:{backend_port}/api/health"
        if not self._wait_for_url(backend_url, timeout=60):
            return self._build_failure("Flask backend did not become ready in time", steps)
        steps.append(f"✅ Backend is responding at {backend_url}")

        frontend_start = self._start_process("npm run dev", frontend_dir, "Starting React frontend")
        steps.append(frontend_start)
        if not frontend_start.startswith("✅"):
            return self._build_failure("Could not start React frontend", steps)

        frontend_url = f"http://127.0.0.1:{frontend_port}"
        if not self._wait_for_url(frontend_url, timeout=90):
            return self._build_failure("React frontend did not become ready in time", steps)
        steps.append(f"✅ Frontend is responding at {frontend_url}")

        print("\n✅ Flask project setup complete")
        print("   Frontend URL:", frontend_url)
        print("   Backend URL:", backend_url)
        return {
            "success": True,
            "error": None,
            "steps": steps,
            "urls": {
                "frontend": frontend_url,
                "backend": backend_url,
            },
        }

    def _build_failure(self, error, steps):
        logger.error(error)
        return {
            "success": False,
            "error": error,
            "steps": steps + [f"❌ {error}"],
        }

    def _load_config(self):
        if not self.config_path.exists():
            return {}, f"config.json not found at: {self.config_path}"
        try:
            with open(self.config_path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            return data, None
        except json.JSONDecodeError as exc:
            return {}, f"Invalid JSON in config.json — {exc}"
        except Exception as exc:
            return {}, f"Could not read config.json: {exc}"

    def _command_exists(self, command_name):
        return shutil.which(command_name) is not None

    def _python_executable(self):
        if sys.executable and Path(sys.executable).exists():
            return sys.executable
        python_cmd = shutil.which("python") or shutil.which("py")
        return python_cmd

    def _safe_int(self, value, default_value):
        try:
            return int(value)
        except Exception:
            return default_value

    def _sanitize_folder_name(self, name):
        if not name:
            return ""
        cleaned = re.sub(r'[<>:"/\\|?*]+', "_", str(name).strip())
        cleaned = re.sub(r"\s+", " ", cleaned)
        cleaned = cleaned.rstrip(". ")
        return cleaned

    def _npm_package_name(self, name):
        cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip().lower())
        cleaned = cleaned.strip("-")
        return cleaned or "project"

    def _create_directory(self, path):
        path.mkdir(parents=True, exist_ok=True)

    def _write_file(self, path, content):
        self._create_directory(path.parent)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(content)

    def _run_command(self, command, cwd, label):
        try:
            result = subprocess.run(
                command,
                cwd=str(cwd),
                shell=True,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                logger.info(f"{label} succeeded")
                return f"✅ {label}"

            stderr = (result.stderr or result.stdout or "").strip()
            logger.error(f"{label} failed: {stderr}")
            return f"❌ {label} failed: {stderr[:200]}"
        except Exception as exc:
            logger.error(f"{label} error: {exc}")
            return f"❌ {label} error: {exc}"

    def _start_process(self, command, cwd, label):
        try:
            creationflags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)
            subprocess.Popen(
                command,
                cwd=str(cwd),
                shell=True,
                creationflags=creationflags,
            )
            logger.info(f"{label} started: {command}")
            return f"✅ {label} started"
        except Exception as exc:
            logger.error(f"{label} failed to start: {exc}")
            return f"❌ {label} failed to start: {exc}"

    def _wait_for_url(self, url, timeout=60):
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                with urlopen(url, timeout=5) as response:
                    if 200 <= getattr(response, "status", 200) < 500:
                        return True
            except URLError:
                time.sleep(2)
            except Exception:
                time.sleep(2)
        return False

    def _react_frontend_package_json(self, project_name, frontend_port, backend_port):
        package_name = self._npm_package_name(project_name) + "-frontend"
        return dedent(f'''
        {{
          "name": "{package_name}",
          "private": true,
          "version": "0.0.0",
          "type": "module",
          "scripts": {{
            "dev": "vite --host 127.0.0.1 --port {frontend_port}",
            "build": "vite build",
            "preview": "vite preview --host 127.0.0.1 --port {frontend_port}"
          }},
          "dependencies": {{
            "react": "^18.3.1",
            "react-dom": "^18.3.1"
          }},
          "devDependencies": {{
            "@vitejs/plugin-react": "^4.3.1",
            "vite": "^5.4.0"
          }}
        }}
        ''').strip() + "\n"

    def _react_vite_config(self, frontend_port, backend_port):
        return dedent(f'''
        import {{ defineConfig }} from 'vite'
        import react from '@vitejs/plugin-react'

        export default defineConfig({{
          plugins: [react()],
          server: {{
            host: '127.0.0.1',
            port: {frontend_port},
            proxy: {{
              '/api': {{
                target: 'http://127.0.0.1:{backend_port}',
                changeOrigin: true,
                secure: false,
              }},
            }},
          }},
        }})
        ''').strip() + "\n"

    def _react_index_html(self, project_name):
        display_name = project_name.replace("_", " ").strip() or "Project"
        return dedent(f'''
        <!doctype html>
        <html lang="en">
          <head>
            <meta charset="UTF-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0" />
            <title>{display_name}</title>
          </head>
          <body>
            <div id="root"></div>
            <script type="module" src="/src/main.jsx"></script>
          </body>
        </html>
        ''').strip() + "\n"

    def _react_frontend_main(self):
        return dedent('''
        import React from 'react'
        import ReactDOM from 'react-dom/client'
        import App from './App'
        import './index.css'

        ReactDOM.createRoot(document.getElementById('root')).render(
          <React.StrictMode>
            <App />
          </React.StrictMode>,
        )
        ''').strip() + "\n"

    def _react_frontend_app(self, project_name, backend_label="Express backend"):
        display_name = project_name.replace("_", " ").strip() or "Project"
        return dedent(f'''
        import {{ useEffect, useState }} from 'react'

        export default function App() {{
          const [backendStatus, setBackendStatus] = useState('Checking backend...')

          useEffect(() => {{
            fetch('/api/health')
              .then((response) => response.json())
              .then((data) => setBackendStatus(data.message || 'Backend is running'))
              .catch(() => setBackendStatus('Backend is starting or unreachable right now'))
          }}, [])

          return (
            <main className="app-shell">
              <div className="card">
                <p className="eyebrow">Project setup complete</p>
                <h1>{display_name}</h1>
                <p className="lead">
                  Your React frontend is live and the {backend_label.lower()} is available.
                </p>
                <div className="status-panel">
                  <span className="status-label">Backend status</span>
                  <strong>{{backendStatus}}</strong>
                </div>
              </div>
            </main>
          )
        }}
        ''').strip() + "\n"

    def _react_frontend_css(self):
        return dedent('''
        :root {
          font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
          color: #f3f4f6;
          background: #0f172a;
        }

        * {
          box-sizing: border-box;
        }

        body {
          margin: 0;
          min-height: 100vh;
          background: radial-gradient(circle at top, #1e293b 0%, #0f172a 60%, #020617 100%);
        }

        .app-shell {
          min-height: 100vh;
          display: grid;
          place-items: center;
          padding: 24px;
        }

        .card {
          width: min(760px, 100%);
          padding: 40px;
          border: 1px solid rgba(148, 163, 184, 0.2);
          border-radius: 28px;
          background: rgba(15, 23, 42, 0.8);
          box-shadow: 0 24px 80px rgba(0, 0, 0, 0.35);
          backdrop-filter: blur(20px);
        }

        .eyebrow {
          margin: 0 0 12px;
          text-transform: uppercase;
          letter-spacing: 0.2em;
          color: #38bdf8;
          font-size: 0.78rem;
        }

        h1 {
          margin: 0;
          font-size: clamp(2rem, 4vw, 4rem);
        }

        .lead {
          max-width: 60ch;
          color: #cbd5e1;
          line-height: 1.7;
          font-size: 1.05rem;
        }

        .status-panel {
          margin-top: 28px;
          padding: 20px;
          border-radius: 20px;
          background: rgba(30, 41, 59, 0.85);
          border: 1px solid rgba(148, 163, 184, 0.16);
        }

        .status-label {
          display: block;
          margin-bottom: 8px;
          color: #94a3b8;
          font-size: 0.82rem;
          text-transform: uppercase;
          letter-spacing: 0.08em;
        }
        ''').strip() + "\n"

    def _express_package_json(self):
        return dedent('''
        {
          "name": "backend",
          "version": "1.0.0",
          "description": "Express backend for the voice assistant project setup",
          "main": "server.js",
          "scripts": {
            "start": "node server.js",
            "dev": "nodemon server.js"
          },
          "dependencies": {
            "cors": "^2.8.5",
            "express": "^4.19.2"
          },
          "devDependencies": {
            "nodemon": "^3.1.4"
          }
        }
        ''').strip() + "\n"

    def _express_server_js(self, backend_port):
        return dedent(f'''
        const express = require('express');
        const cors = require('cors');

        const app = express();
        const port = process.env.PORT || {backend_port};

        app.use(cors());
        app.use(express.json());

        app.get('/api/health', (req, res) => {{
          res.json({{
            status: 'ok',
            message: 'Express backend is running',
            port
          }});
        }});

        app.get('/', (req, res) => {{
          res.send(`
            <html>
              <body style="font-family: Arial, sans-serif; padding: 32px; background: #0f172a; color: white;">
                <h1>Express backend is running</h1>
                <p>Health check: <a href="/api/health" style="color: #38bdf8;">/api/health</a></p>
              </body>
            </html>
          `);
        }});

        app.listen(port, '127.0.0.1', () => {{
          console.log(`Express backend running at http://127.0.0.1:${{port}}`);
        }});
        ''').strip() + "\n"

    def _flask_requirements(self):
        return dedent('''
        Flask==3.0.3
        Flask-Cors==4.0.1
        ''').strip() + "\n"

    def _flask_app_py(self, backend_port, project_name):
        display_name = project_name.replace("_", " ").strip() or "Project"
        return dedent(f'''
        from flask import Flask, jsonify
        from flask_cors import CORS

        app = Flask(__name__)
        CORS(app)

        @app.get('/')
        def index():
            return """
            <html>
              <body style="font-family: Arial, sans-serif; padding: 32px; background: #0f172a; color: white;">
                <h1>Flask backend is running</h1>
                <p>{display_name}</p>
                <p>Health check: <a href="/api/health" style="color: #38bdf8;">/api/health</a></p>
              </body>
            </html>
            """

        @app.get('/api/health')
        def health():
            return jsonify(status='ok', message='Flask backend is running', port={backend_port})

        if __name__ == '__main__':
            app.run(host='127.0.0.1', port={backend_port}, debug=True)
        ''').strip() + "\n"
