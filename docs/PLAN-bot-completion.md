# Plan: Vietnam Stock Alert Bot - Completion & Hardening

## Overview
Hoàn thiện và tăng cường độ tin cậy cho Stock Alert Bot trước khi triển khai production. Tập trung vào error handling, logging, validation và testing để đảm bảo bot hoạt động ổn định 24/7.

**Project Type:** BACKEND (Python)

---

## Success Criteria
- [ ] Bot chạy ổn định trong 24h liên tục không crash.
- [ ] Xử lý gracefully tất cả các lỗi mạng, API, dữ liệu.
- [ ] Logging đầy đủ để debug khi có sự cố.
- [ ] Validation dữ liệu đầu vào (portfolio.json, .env).
- [ ] Unit tests cho các module quan trọng (engines, notifier).
- [ ] Documentation đầy đủ cho deployment.

---

## Tech Stack
- **Language:** Python 3.10+
- **Testing:** pytest
- **Logging:** Python logging module
- **Monitoring:** Health check endpoint (optional)

---

## File Structure (Current)
```text
ckbot/
├── .env
├── .gitignore
├── portfolio.json
├── requirements.txt
├── main.py
├── Dockerfile
├── docker-compose.yml
├── README.md
├── docs/
│   ├── srs.md
│   └── zalo-bot-doc.md
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

### Phase 1: Code Review & Validation
**Goal:** Phát hiện và sửa các lỗi tiềm ẩn trước khi chạy lần đầu.

#### Task 1.1: Review src/config.py
- **Agent:** `backend-specialist`
- **Skill:** `clean-code`, `python-patterns`
- **INPUT:** Current config.py
- **OUTPUT:** 
  - Validation logic cho các biến môi trường bắt buộc
  - Clear error messages khi thiếu config
- **VERIFY:** 
  ```bash
  # Test với .env thiếu token
  python -c "from src.config import settings; print(settings.TELEGRAM_BOT_TOKEN)"
  # Phải raise error rõ ràng
  ```

#### Task 1.2: Review src/portfolio.py
- **Agent:** `backend-specialist`
- **Skill:** `clean-code`, `python-patterns`
- **INPUT:** Current portfolio.py
- **OUTPUT:**
  - Validation schema cho portfolio.json (avg_price > 0, quantity > 0)
  - Handle corrupted JSON file
  - Backup mechanism trước khi save
- **VERIFY:**
  ```bash
  # Test với portfolio.json invalid
  echo '{"VNM": {"avg_price": -100}}' > portfolio.json
  python -c "from src.portfolio import get_portfolio_manager; mgr = mgr.load_portfolio()"
  # Phải reject hoặc warn
  ```

#### Task 1.3: Review src/data_loader.py
- **Agent:** `backend-specialist`
- **Skill:** `clean-code`, `python-patterns`
- **INPUT:** Current data_loader.py
- **OUTPUT:**
  - Retry logic cho API calls (vnstock có thể timeout)
  - Cache mechanism để tránh spam API
  - Validate DataFrame không rỗng trước khi return
- **VERIFY:**
  ```python
  # Test với mã CP không tồn tại
  df = DataLoader.get_historical_data("INVALID_SYMBOL")
  assert df.empty or df is None
  ```

#### Task 1.4: Review src/engines.py
- **Agent:** `backend-specialist`
- **Skill:** `clean-code`, `python-patterns`
- **INPUT:** Current engines.py
- **OUTPUT:**
  - Handle edge cases (DataFrame rỗng, NaN values)
  - Validate RSI/MA calculations
  - Add bounds checking (RSI phải 0-100)
- **VERIFY:**
  ```python
  # Test với dữ liệu thiếu
  import pandas as pd
  df = pd.DataFrame()
  rsi = AnalysisEngine.calculate_rsi(df)
  assert 0 <= rsi <= 100
  ```

#### Task 1.5: Review src/notifier.py
- **Agent:** `backend-specialist`
- **Skill:** `clean-code`, `python-patterns`
- **INPUT:** Current notifier.py
- **OUTPUT:**
  - Retry logic cho failed messages (3 lần, exponential backoff)
  - Validate config trước khi gửi
  - Fallback mechanism (nếu Telegram fail, thử Zalo)
- **VERIFY:**
  ```python
  # Test với token invalid
  notifier = TelegramNotifier()
  result = notifier.send_message("Test")
  # Phải return False và log error
  ```

#### Task 1.6: Review main.py
- **Agent:** `backend-specialist`
- **Skill:** `clean-code`, `python-patterns`
- **INPUT:** Current main.py
- **OUTPUT:**
  - Graceful shutdown handler (SIGTERM, SIGINT)
  - Global exception handler để tránh crash
  - Healthcheck mechanism (log heartbeat mỗi 15 phút)
- **VERIFY:**
  ```bash
  # Test Ctrl+C
  python main.py
  # Phải cleanup gracefully
  ```

---

### Phase 2: Error Handling & Logging
**Goal:** Đảm bảo bot không crash và có đủ thông tin để debug.

#### Task 2.1: Implement Centralized Logging
- **Agent:** `backend-specialist`
- **Skill:** `python-patterns`
- **INPUT:** All modules
- **OUTPUT:**
  - File `src/logger.py` với configured logger
  - Log levels: DEBUG (development), INFO (production)
  - Rotate logs (max 10MB, keep 5 files)
- **VERIFY:**
  ```bash
  # Chạy bot 1 phút
  python main.py
  # Check log file tồn tại và có nội dung
  cat logs/stock-bot.log
  ```

#### Task 2.2: Add Retry Logic for Network Calls
- **Agent:** `backend-specialist`
- **Skill:** `python-patterns`
- **INPUT:** data_loader.py, notifier.py
- **OUTPUT:**
  - Decorator `@retry(max_attempts=3, backoff=2)`
  - Apply cho tất cả HTTP calls
- **VERIFY:**
  ```python
  # Mock network failure
  # Verify retry 3 lần trước khi fail
  ```

#### Task 2.3: Implement Circuit Breaker for API
- **Agent:** `backend-specialist`
- **Skill:** `python-patterns`
- **INPUT:** data_loader.py
- **OUTPUT:**
  - Circuit breaker pattern cho vnstock API
  - Nếu fail 5 lần liên tiếp, dừng call 5 phút
- **VERIFY:**
  ```python
  # Simulate 5 consecutive failures
  # Verify circuit opens và không call thêm
  ```

---

### Phase 3: Testing
**Goal:** Đảm bảo các module core hoạt động đúng.

#### Task 3.1: Unit Tests for AnalysisEngine
- **Agent:** `backend-specialist`
- **Skill:** `testing-patterns`, `tdd-workflow`
- **INPUT:** src/engines.py
- **OUTPUT:**
  - File `tests/test_engines.py`
  - Test cases:
    - RSI calculation với dữ liệu mẫu
    - MA calculation
    - Signal logic (BUY, SELL, CUT_LOSS)
    - Edge cases (empty DataFrame, NaN)
- **VERIFY:**
  ```bash
  pytest tests/test_engines.py -v
  # Tất cả tests phải pass
  ```

#### Task 3.2: Integration Tests for Notifier
- **Agent:** `backend-specialist`
- **Skill:** `testing-patterns`
- **INPUT:** src/notifier.py
- **OUTPUT:**
  - File `tests/test_notifier.py`
  - Mock HTTP calls
  - Test format_message output
  - Test provider selection logic
- **VERIFY:**
  ```bash
  pytest tests/test_notifier.py -v
  ```

#### Task 3.3: End-to-End Smoke Test
- **Agent:** `backend-specialist`
- **Skill:** `testing-patterns`
- **INPUT:** main.py
- **OUTPUT:**
  - File `tests/test_e2e.py`
  - Test full flow với mock data
  - Verify không crash trong 1 chu kỳ
- **VERIFY:**
  ```bash
  pytest tests/test_e2e.py -v
  ```

---

### Phase 4: Documentation & Deployment Prep
**Goal:** Đảm bảo người dùng có thể deploy dễ dàng.

#### Task 4.1: Create Troubleshooting Guide
- **Agent:** `documentation-writer`
- **INPUT:** Common errors từ review
- **OUTPUT:**
  - File `docs/TROUBLESHOOTING.md`
  - Các lỗi thường gặp và cách fix
- **VERIFY:** Manual review

#### Task 4.2: Update requirements.txt
- **Agent:** `backend-specialist`
- **INPUT:** Current requirements.txt
- **OUTPUT:**
  - Thêm pytest, pytest-mock
  - Pin versions để tránh breaking changes
- **VERIFY:**
  ```bash
  pip install -r requirements.txt
  # Không có conflict
  ```

#### Task 4.3: Create Health Check Script
- **Agent:** `backend-specialist`
- **Skill:** `bash-linux`
- **INPUT:** None
- **OUTPUT:**
  - File `scripts/health_check.sh`
  - Check bot process running
  - Check log file có update gần đây
- **VERIFY:**
  ```bash
  bash scripts/health_check.sh
  # Exit code 0 nếu healthy
  ```

---

### Phase 5: Pre-Production Checklist
**Goal:** Đảm bảo mọi thứ sẵn sàng trước khi chạy production.

#### Task 5.1: Security Audit
- **Agent:** `security-auditor`
- **Skill:** `vulnerability-scanner`
- **INPUT:** All source files
- **OUTPUT:**
  - Scan secrets in code
  - Check .env.example không chứa real tokens
  - Verify .gitignore đầy đủ
- **VERIFY:**
  ```bash
  python .agent/skills/vulnerability-scanner/scripts/security_scan.py .
  ```

#### Task 5.2: Dependency Audit
- **Agent:** `security-auditor`
- **Skill:** `vulnerability-scanner`
- **INPUT:** requirements.txt
- **OUTPUT:**
  - Check known vulnerabilities
  - Suggest updates nếu cần
- **VERIFY:**
  ```bash
  python .agent/skills/vulnerability-scanner/scripts/dependency_analyzer.py .
  ```

#### Task 5.3: Docker Build Test
- **Agent:** `devops-engineer`
- **INPUT:** Dockerfile, docker-compose.yml
- **OUTPUT:**
  - Build image thành công
  - Container start và stop gracefully
- **VERIFY:**
  ```bash
  docker-compose build
  docker-compose up -d
  docker-compose logs -f
  docker-compose down
  ```

#### Task 5.4: Dry Run Test
- **Agent:** `backend-specialist`
- **INPUT:** Complete system
- **OUTPUT:**
  - Chạy bot với mock data trong 1 giờ
  - Verify không crash
  - Verify logs clean
- **VERIFY:**
  ```bash
  # Set test mode in .env
  python main.py
  # Monitor 1 hour
  ```

---

## Phase X: Final Verification Checklist

### Code Quality
- [ ] All modules có proper error handling
- [ ] Logging implemented ở tất cả critical paths
- [ ] No hardcoded secrets
- [ ] Type hints đầy đủ

### Testing
- [ ] Unit tests pass: `pytest tests/ -v`
- [ ] Code coverage >= 70%: `pytest --cov=src tests/`
- [ ] No critical security issues: `python .agent/skills/vulnerability-scanner/scripts/security_scan.py .`

### Documentation
- [ ] README.md updated
- [ ] TROUBLESHOOTING.md created
- [ ] .env.example complete

### Deployment
- [ ] Docker build success
- [ ] Health check script works
- [ ] Dry run 1 hour success

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| vnstock API down | Implement circuit breaker, cache last known prices |
| Network timeout | Retry logic với exponential backoff |
| Invalid portfolio.json | Validation + backup mechanism |
| Bot crash overnight | Docker restart policy + health monitoring |
| Missing .env variables | Validation at startup với clear error messages |

---

## Estimated Timeline
- Phase 1 (Review): 2-3 hours
- Phase 2 (Error Handling): 2 hours
- Phase 3 (Testing): 3 hours
- Phase 4 (Documentation): 1 hour
- Phase 5 (Pre-Production): 1 hour

**Total:** ~9-10 hours

---

## Next Steps After Completion
1. Deploy to production (Docker)
2. Monitor logs for 24h
3. Collect feedback
4. Plan Phase 2 features (backtesting, more indicators)
