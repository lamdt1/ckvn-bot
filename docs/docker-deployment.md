# Plan: Dockerization for Vietnam Stock Alert Bot

## Overview
Containerizing the Modular Stock Alert Bot to ensure environmental consistency and ease of deployment. Use Docker Compose for volume management and auto-restart capabilities.

**Project Type:** DEVOPS / BACKEND

---

## Success Criteria
- [ ] Lightweight Docker image created.
- [ ] `docker-compose up` starts the bot successfully.
- [ ] Data persistence: `portfolio.json` edits on host reflect inside container.
- [ ] Environment variables correctly passed from `.env` to container.

---

## Task Breakdown

### Phase 5: Dockerization
- [ ] **Task 1: Dockerfile Creation**
  - Use `python:3.10-slim` for a small footprint.
  - Agent: `devops-engineer`
- [ ] **Task 2: Docker Compose Setup**
  - Define service, volumes, and restart policy.
  - Agent: `devops-engineer`
- [ ] **Task 3: Docker Ignore Optimization**
  - Prevent unnecessary files from bloating the image.
  - Agent: `devops-engineer`

---

## Docker Commands Cheat Sheet
- Build & Run: `docker-compose up -d --build`
- Stop: `docker-compose down`
- View Logs: `docker logs -f stock-alert-bot`
