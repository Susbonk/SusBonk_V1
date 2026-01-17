# Quick Test Checklist - Critical Tests Only

## 🔴 P0 - MUST PASS (50 tests)

### Authentication (19)
- [ ] T001-T008: Registration (valid, duplicate, validation, rollback)
- [ ] T009-T014: Login (valid, invalid, inactive user)
- [ ] T015-T019: Get profile (with/without token, expired)

### Route Conflicts (4)
- [ ] T116: /prompts/custom works (not 404)
- [ ] T117: /prompts/{uuid} works
- [ ] T118: /prompts/custom/{uuid} works
- [ ] T119: "custom" not treated as UUID

### Security (12)
- [ ] T139: JWT_SECRET required
- [ ] T140-T143: Token validation (expiry, signature, tampering)
- [ ] T144-T146: Password security (hashing, not returned)
- [ ] T147-T150: Ownership validation (isolation between users)

### Database Transactions (7)
- [ ] T125: Rollback on registration failure
- [ ] T126-T128: Rollback on custom prompt operations
- [ ] T129: Rollback on chat update
- [ ] T130-T131: Rollback on user state operations

### Critical CRUD (8)
- [ ] T046: Create custom prompt
- [ ] T053: Update custom prompt
- [ ] T061: Delete custom prompt
- [ ] T080: Update chat settings
- [ ] T101: Update user state trust
- [ ] T108: Reset user to untrusted
- [ ] T020: List system prompts
- [ ] T069: List user chats

---

## ⚠️ P1 - SHOULD PASS (80 tests)

### Custom Prompts Full CRUD (26)
- [ ] T035-T040: List custom prompts (pagination, ownership)
- [ ] T041-T045: Get custom prompt (ownership, not found)
- [ ] T047-T052: Create validation and ownership
- [ ] T054-T060: Update validation and ownership
- [ ] T062-T068: Delete validation and ownership

### Chats Management (17)
- [ ] T070-T074: List chats (pagination, ownership)
- [ ] T075-T079: Get chat (ownership, not found)
- [ ] T081-T093: Update all chat fields (validation, ownership)

### User States (15)
- [ ] T094-T100: List user states (pagination, ownership)
- [ ] T102-T107: Update user state (validation, ownership)
- [ ] T109-T115: Reset user (validation, ownership)

### System Prompts (8)
- [ ] T021-T029: List with pagination, search, ordering
- [ ] T030-T034: Get prompt (not found, inactive)

### Error Handling (11)
- [ ] T166-T173: HTTP status codes (201, 204, 401, 403, 404, 409, 422, 500)
- [ ] T174-T176: Error messages

### Ownership Validation (3)
- [ ] T038-T039: Custom prompts isolation
- [ ] T072-T073: Chats isolation

---

## 📊 P2 - NICE TO HAVE (45 tests)

### Performance (7)
- [ ] T184-T190: Response times and pagination limits

### Integration (5)
- [ ] T191-T195: End-to-end user flows

### Logging (7)
- [ ] T177-T183: Structured logging for all operations

### Database Relationships (7)
- [ ] T132-T138: SQLAlchemy relationships and cascades

### Connection Pool (5)
- [ ] T120-T124: Pool configuration and load testing

### OpenAPI (7)
- [ ] T156-T162: Swagger and ReDoc documentation

### CORS (5)
- [ ] T151-T155: CORS headers and preflight

### Health (2)
- [ ] T163-T165: Health check endpoint

---

## 🎯 Test Execution Strategy

### Phase 1: Smoke Test (10 min)
Run P0 tests (50 tests) - Must all pass before proceeding

### Phase 2: Functional Test (20 min)
Run P1 tests (80 tests) - Should have >95% pass rate

### Phase 3: Full Suite (30 min)
Run all tests (195 tests) - Target 80%+ overall pass rate

---

## 📝 Quick Test Commands

```bash
# Run all tests
pytest tests/ -v

# Run by priority
pytest tests/ -v -m "priority_p0"
pytest tests/ -v -m "priority_p1"
pytest tests/ -v -m "priority_p2"

# Run by category
pytest tests/test_auth.py -v
pytest tests/test_prompts.py -v
pytest tests/test_chats.py -v
pytest tests/test_user_states.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test
pytest tests/test_auth.py::test_register_valid_credentials -v
```

---

## ✅ Success Criteria

- **P0 Tests**: 100% pass rate (50/50)
- **P1 Tests**: 95%+ pass rate (76+/80)
- **P2 Tests**: 80%+ pass rate (36+/45)
- **Overall**: 80%+ pass rate (156+/195)
- **Code Coverage**: 80%+ line coverage

---

## 🚨 Failure Protocol

If any P0 test fails:
1. Stop testing immediately
2. Fix the failing test
3. Re-run full P0 suite
4. Only proceed to P1 when P0 is 100% green

If P1 pass rate < 95%:
1. Review and fix critical failures
2. Document known issues
3. Decide if blocking for deployment

If P2 pass rate < 80%:
1. Document as technical debt
2. Non-blocking for deployment
3. Schedule fixes in next sprint
