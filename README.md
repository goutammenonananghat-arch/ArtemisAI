# Artemis AI

Artemis AI provides a lightweight framework for orchestrating skills, scheduling
jobs, persisting memories and integrating with Google's Gemini models.

## Key Modules
- **Orchestrator** (`src/orchestrator.py`): registers skills, confirms
  privileged actions and writes audit entries to `logs/security.log`.
- **Scheduler** (`src/scheduler.py`): queues jobs with APScheduler and persists
  them in `logs/jobs.sqlite` so tasks survive restarts.
- **Memory subsystem** (`src/memory.py`): combines a key/value store and vector
  search with time decay, storing data in `data/kv_store.json` and
  `data/vector_store.json`.
- **Gemini integration** (`src/models/gemini.py`): async helper for generating
  text via `google-generativeai` using an API key from the secrets manager.
- **Secrets manager** (`src/security/secrets_manager.py`): minimal XOR‑encrypted
  storage for credentials such as `GEMINI_API_KEY`.

## Installation
1. **Python**: requires version 3.10 or later.
2. **Dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install google-generativeai  # if not included above
   ```
3. **API key**: store your Gemini key using the secrets manager:
   ```python
   from security.secrets_manager import SecretsManager
   SecretsManager().store("GEMINI_API_KEY", "your-key")
   ```

## Usage
### Generate text with Gemini
```python
import asyncio
from models import gemini

async def main():
    print(await gemini.generate("Hello from Artemis"))

asyncio.run(main())
```

### Manage memory
```python
from memory import write_memory, retrieve_memory

write_memory("fact", "The sky is blue.")
print(retrieve_memory("fact"))
```

### Schedule tasks
```python
from datetime import datetime, timedelta
from scheduler import schedule

def alert(msg: str) -> None:
    print(msg)

schedule(alert, datetime.utcnow() + timedelta(seconds=30), "Wake up")
```

### Handle secrets
```python
from security.secrets_manager import SecretsManager

sm = SecretsManager()
sm.store("token", "abc123")
print(sm.retrieve("token"))
```

## Logs & Persistence
- Security events: `logs/security.log`
- Scheduled jobs: `logs/jobs.sqlite`
- Memory data: `data/kv_store.json`, `data/vector_store.json`

The `logs/` and `data/` directories are used for persistent storage across
runs.
