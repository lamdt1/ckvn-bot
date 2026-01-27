# Plan: Vietnam Stock Alert Bot (Modular Implementation)

## Overview
Rebuilding the current monolithic stock bot into a modular, maintainable, and robust personal alert system. This architecture separates concerns into data retrieval, technical analysis, portfolio management, and notification services.

**Project Type:** BACKEND (Python)

---

## Success Criteria
- [ ] Successfully fetch real-time and historical data from `vnstock`.
- [ ] Accurately calculate RSI (14) and MA20.
- [ ] Correct calculation of Profit/Loss (PnL) based on `portfolio.json`.
- [ ] Reliable Telegram notifications during trading hours (09:00-11:30, 13:00-15:00).
- [ ] Error handling for network/API failures.

---

## Tech Stack
- **Language:** Python 3.10+
- **Data Source:** `vnstock`
- **Configuration:** `pydantic-settings` (Type-safe env management)
- **Scheduling:** `apscheduler` (Better control over trading hours than `time.sleep`)
- **Notifications:** `httpx` or `python-telegram-bot`
- **Data Analysis:** `pandas` (built-in with vnstock)

---

## File Structure
```text
ckbot/
├── .env
├── .gitignore
├── portfolio.json
├── requirements.txt
├── main.py
└── src/
    ├── __init__.py
    ├── config.py
    ├── data_loader.py
    ├── engines.py
    ├── notifier.py
    └── portfolio.py
```

---

## Task Breakdown

### Phase 1: Foundation
- [x] **Task 1: Project Initialization**
  - Create directory structure, `.gitignore`, and `requirements.txt`.
  - Agent: `backend-specialist`
- [x] **Task 2: Type-safe Configuration**
  - Implement `src/config.py` using `Pydantic Settings`.
  - Agent: `backend-specialist`
- [x] **Task 3: Portfolio Data Model**
  - Implement `src/portfolio.py` to load/save `portfolio.json`.
  - Agent: `backend-specialist`

### Phase 2: Core Engineering
- [x] **Task 4: Data Loader Module**
  - Implement `src/data_loader.py` to interface with `vnstock`.
  - Agent: `backend-specialist`
- [x] **Task 5: Analysis Engine**
  - Implement `src/engines.py` for RSI, MA20, and PnL logic.
  - Agent: `backend-specialist`

### Phase 3: Integration & UX
- [x] **Task 6: Telegram Notifier**
  - Implement `src/notifier.py` with Markdown & Emoji support.
  - Agent: `backend-specialist`
- [x] **Task 7: Main Loop & Scheduler**
  - Implement `main.py` using `APScheduler` with trading hour constraints.
  - Agent: `backend-specialist`

### Phase 4: Final Polish
- [x] **Task 8: Robust Error Handling**
  - Wrap API calls and file I/O in try-except blocks with logging.
  - Agent: `backend-specialist`

---

## Phase X: Verification Checklist
- [ ] No hardcoded secrets (using `.env`).
- [ ] RSI/MA20 values verified against manual calculation.
- [ ] Trading hour logic tested (skipping weekend/night).
- [ ] Bot message formatting looks Premium in Telegram.
