# GameHub — Microservices Capstone

> EPITA · Microservices with Python · 30h intensive

You are going to build a real distributed system from scratch — one service at a time.

By the end of this course, you will have a running gamer social platform where:
- A user signs up, manages their profile, and tracks their game library
- Activity events flow asynchronously via RabbitMQ to a GDPR-compliant logging service
- Notifications are sent asynchronously via RabbitMQ
- Every request is authenticated and traceable across services
- The whole thing runs in Docker with a single command

---

## How this course works

**10 modules. 9 lessons of 2 hours each. One branch per module.**

Each module lives in `modules/module-XX/`. Open `exercise.md` to get started, and `REFLECTION.md` to see what you need to submit.

You write your services in the `services/` folder and the API gateway in `gateway/`. Both are empty on purpose — that's your work.

```
modules/
├── module-01/
│   ├── exercise.md      ← what to do in class
│   └── REFLECTION.md    ← what to submit before the next lesson
├── module-02/
│   └── ...
├── ...
├── module-08/
├── module-09/
│   └── exercise.md      ← optional exploration guide (observability)
├── module-10/
│   └── exercise.md      ← optional exploration guide (resilience)
└── module-09-10/
    └── ORAL_PRESENTATION.md   ← final assessment guide

gateway/     ← you build this in Module 3
services/    ← you build these from Module 2 onward
```

---

## Assessment

| Submission | What | Deadline |
|---|---|---|
| `module-01/<team-name>` | Design + REFLECTION.md | Before Module 2 lesson |
| `module-02/<team-name>` | Code + REFLECTION.md | Before Module 3 lesson |
| `module-03/<team-name>` | Code + REFLECTION.md | Before Module 4 lesson |
| `module-04/<team-name>` | Code + REFLECTION.md | Before Module 5 lesson |
| `module-05/<team-name>` | Code + REFLECTION.md | Before Module 6 lesson |
| `module-06/<team-name>` | Code + REFLECTION.md | Before Module 7 lesson |
| `module-07/<team-name>` | Code + REFLECTION.md | Before Module 8 lesson |
| `module-08/<team-name>` | Code + REFLECTION.md | Before final session |
| Oral presentation | 15 min/group, live | Final session |

### Branch naming

```bash
git checkout -b module-01/your-team-name
```

One branch per module. Each branch includes the code produced during that lesson **and** a completed `REFLECTION.md`.

### The REFLECTION.md

Every `REFLECTION.md` has the same three questions:
1. **The "why"** — why does this module's concept exist in this architecture?
2. **Your choice** — one decision made during the lesson; explain it to someone who wasn't in the room
3. **The tradeoff** — what does this approach cost?

These are your personal notes. You will use them during the oral presentation. A few honest sentences beat a long generic answer — and they are much harder to fake without having actually done the work.

### Oral presentation

15 minutes per group. No slides required. See `modules/module-09-10/ORAL_PRESENTATION.md` for the full structure.

---

## Prerequisites

- Python 3.12+
- Node.js 20 (for notification-service only)
- Docker + Docker Compose (from Module 4 onward)
- A working terminal

---

## Running the system

### Modules 1–3 — local only, no Docker

```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cd services/user-service
alembic upgrade head
uvicorn app.main:app --reload --port 8001
```

Each service runs on its own port with SQLite — no database server needed.

### Module 4+ — infrastructure via Docker

```bash
docker compose -f docker-compose.infra.yml up -d
```

### Module 8+ — services containerised

```bash
docker compose \
  -f docker-compose.infra.yml \
  -f modules/module-08/docker-compose.override.yml \
  up --build
```

---

## System map

> Databases shown are the Module 8+ production state. Modules 1–7 use SQLite locally.

```
                    ┌─────────────────────┐
    HTTP ──────────▶│  gateway (FastAPI)  │  port 8000 — single entry point
                    │  JWT validation     │  built in Module 3, grows to M10
                    │  version routing    │
                    │  circuit breakers   │
                    └──────────┬──────────┘
                               │
          ┌────────────────────┼──────────────────────┐
          ▼                    ▼                       ▼
   ┌────────────┐     ┌────────────┐     ┌────────────────┐
   │user-service│     │game-service│     │activity-service│
   │ PostgreSQL │     │ PostgreSQL │     │ PostgreSQL     │
   └────────────┘     │ + Redis    │     └───────┬────────┘
                      └────────────┘              RabbitMQ
                                        ┌────────────┴─────────────┐
                                        ▼                           ▼
                       ┌─────────────────────┐    ┌──────────────────────┐
                       │notification-service │    │  logging-service     │
                       │ Node.js + SQLite    │    │  PostgreSQL          │
                       │ RabbitMQ consumer   │    │  RabbitMQ consumer   │
                       │ (always local)      │    │  GDPR consent        │
                       └─────────────────────┘    └──────────────────────┘

   auth-service (port 8005) — issues and validates JWT tokens
   ↑ used by gateway for token verification (shared SECRET_KEY)
```

---

## Access points

| Service | URL | Notes |
|---|---|---|
| **Gateway** | http://localhost:8000 | Single entry point — use this for all requests |
| Auth Service | http://localhost:8005/docs | Issues JWT tokens |
| User Service | http://localhost:8001/docs | Debug only — never call directly from a client |
| Game Service | http://localhost:8002/docs | Debug only |
| Activity Service | http://localhost:8003/docs | Debug only |
| Notification Service | http://localhost:8004 | Always local (Node.js) |
| Logging Service | http://localhost:8006 | Debug only |
| RabbitMQ UI | http://localhost:15672 | guest / guest |
| Grafana | http://localhost:3000 | admin / admin |
| Jaeger | http://localhost:16686 | |

---

## Port reference

| Port | Service |
|---|---|
| 8000 | gateway |
| 8001 | user-service |
| 8002 | game-service |
| 8003 | activity-service |
| 8004 | notification-service |
| 8005 | auth-service |
| 8006 | logging-service |

---

## Languages

This is a Python-first course. The language breakdown GitHub shows includes:

- **Python** — all microservices and the gateway
- **JavaScript / Node.js** — notification-service only
- **Go Template** — Helm chart templates used in the Module 8 instructor demo (Kubernetes walkthrough). Helm uses Go's templating syntax; there is no Go code in this project.
