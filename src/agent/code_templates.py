"""
Code Templates
==============
Static source-code templates for auto-generated projects.

No LLM calls here — these are plain string constants.
Templates are intentionally minimal so they run without extra
configuration and can be extended by the developer afterward.

Available templates
-------------------
  express_server  — Node.js / Express server (port 3000, one GET route)
  react_app       — React App.jsx functional component (Vite-compatible)
  package_json    — Minimal package.json for a Node project
  gitignore       — Standard .gitignore for Node / React projects
"""

from src.core.logger import setup_logger

logger = setup_logger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# EXPRESS SERVER TEMPLATE
# ─────────────────────────────────────────────────────────────────────────────

EXPRESS_SERVER_TEMPLATE = '''\
const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// ── Routes ────────────────────────────────────────────────────────────────────

app.get('/', (req, res) => {
  res.json({
    message: 'Server is running!',
    status:  'ok',
    port:    PORT,
  });
});

// ── Start server ──────────────────────────────────────────────────────────────

app.listen(PORT, () => {
  console.log(`✅  Express server started on http://localhost:${PORT}`);
});
'''

# ─────────────────────────────────────────────────────────────────────────────
# REACT APP TEMPLATE  (Vite default structure)
# ─────────────────────────────────────────────────────────────────────────────

REACT_APP_TEMPLATE = '''\
import { useState } from 'react'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="App">
      <header className="App-header">
        <h1>🚀 Voice Assistant Project</h1>
        <p>Your React app is live and running!</p>
        <div className="card">
          <button onClick={() => setCount(count + 1)}>
            Clicked {count} time{count !== 1 ? 's' : ''}
          </button>
        </div>
        <p className="hint">
          Edit <code>src/App.jsx</code> and save to reload.
        </p>
      </header>
    </div>
  )
}

export default App
'''

# ─────────────────────────────────────────────────────────────────────────────
# MINIMAL package.json TEMPLATE  (Node projects without npm init -y)
# ─────────────────────────────────────────────────────────────────────────────

PACKAGE_JSON_TEMPLATE = '''\
{{
  "name": "{name}",
  "version": "1.0.0",
  "description": "Auto-generated Node.js project",
  "main": "server.js",
  "scripts": {{
    "start": "node server.js",
    "dev":   "nodemon server.js"
  }},
  "keywords": [],
  "author": "",
  "license": "ISC"
}}
'''

# ─────────────────────────────────────────────────────────────────────────────
# .gitignore TEMPLATE
# ─────────────────────────────────────────────────────────────────────────────

GITIGNORE_TEMPLATE = '''\
# Dependencies
node_modules/
.pnp
.pnp.js

# Build output
dist/
build/

# Environment files
.env
.env.local
.env.*.local

# Logs
*.log
npm-debug.log*

# OS files
.DS_Store
Thumbs.db
'''

# ─────────────────────────────────────────────────────────────────────────────
# Registry — maps template name → template string
# ─────────────────────────────────────────────────────────────────────────────

_REGISTRY: dict[str, str] = {
    'express_server': EXPRESS_SERVER_TEMPLATE,
    'react_app':      REACT_APP_TEMPLATE,
    'package_json':   PACKAGE_JSON_TEMPLATE,
    'gitignore':      GITIGNORE_TEMPLATE,
}


def get_template(name: str, **kwargs) -> str:
    """
    Return the requested template string.

    Args:
        name (str): Template key, e.g. 'express_server', 'react_app'.
        **kwargs:   Optional format variables (e.g. name='my-app' for
                    package_json which contains a {name} placeholder).

    Returns:
        str: Template content, with any kwargs substituted.

    Raises:
        KeyError: If the template name is not found in the registry.

    Example
    -------
        code = get_template('express_server')
        pkg  = get_template('package_json', name='my-node-app')
    """
    try:
        template = _REGISTRY[name]
        if kwargs:
            template = template.format(**kwargs)
        logger.debug(f"Template '{name}' retrieved (kwargs={list(kwargs.keys())})")
        return template
    except KeyError:
        available = ', '.join(_REGISTRY.keys())
        logger.error(f"Template '{name}' not found. Available: {available}")
        raise KeyError(
            f"Template '{name}' not found. "
            f"Available templates: {available}"
        )
    except Exception as exc:
        logger.error(f"Error retrieving template '{name}': {exc}")
        raise


def list_templates() -> list[str]:
    """Return all registered template names."""
    return list(_REGISTRY.keys())
