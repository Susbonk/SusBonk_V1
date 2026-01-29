# Test Feature Protocol - SusBonk API Backend

## Test Categories

### 1. Authentication Tests (`/auth`)

#### POST /auth/register
- [ ] **T001**: Register with valid credentials (201)
- [ ] **T002**: Register with duplicate email (409)
- [ ] **T003**: Register with invalid email format (422)
- [ ] **T004**: Register with missing required fields (422)
- [ ] **T005**: Register with weak password (should accept - no validation yet)
- [ ] **T006**: Verify JWT token is returned
- [ ] **T007**: Verify user is created in database
- [ ] **T008**: Database rollback on commit failure

#### POST /auth/login
- [ ] **T009**: Login with valid credentials (200)
- [ ] **T010**: Login with incorrect password (401)
- [ ] **T011**: Login with non-existent email (401)
- [ ] **T012**: Login with inactive user account (403)
- [ ] **T013**: Verify JWT token is returned
- [ ] **T014**: Verify token contains correct user ID

#### GET /auth/me
- [ ] **T015**: Get current user with valid token (200)
- [ ] **T016**: Get current user without token (401)
- [ ] **T017**: Get current user with invalid token (401)
- [ ] **T018**: Get current user with expired token (401)
- [ ] **T019**: Verify returned user data matches authenticated user

---

### 2. System Prompts Tests (`/prompts`)

#### GET /prompts
- [ ] **T020**: List prompts with default pagination (200)
- [ ] **T021**: List prompts with custom page size (200)
- [ ] **T022**: List prompts with page > total pages (200, empty items)
- [ ] **T023**: List prompts with search filter (200)
- [ ] **T024**: List prompts with ordering by name asc (200)
- [ ] **T025**: List prompts with ordering by name desc (200)
- [ ] **T026**: List prompts with invalid order field (200, uses default)
- [ ] **T027**: List prompts without authentication (401)
- [ ] **T028**: Verify pagination metadata (total, page, page_size)
- [ ] **T029**: Verify only active prompts returned

#### GET /prompts/{id}
- [ ] **T030**: Get prompt with valid ID (200)
- [ ] **T031**: Get prompt with non-existent ID (404)
- [ ] **T032**: Get prompt with invalid UUID format (422)
- [ ] **T033**: Get inactive prompt (404)
- [ ] **T034**: Get prompt without authentication (401)

---

### 3. Custom Prompts Tests (`/prompts/custom`)

#### GET /prompts/custom
- [ ] **T035**: List custom prompts for authenticated user (200)
- [ ] **T036**: List custom prompts with pagination (200)
- [ ] **T037**: List custom prompts with ordering (200)
- [ ] **T038**: Verify only user's own prompts returned
- [ ] **T039**: Verify other users' prompts not visible
- [ ] **T040**: List custom prompts without authentication (401)

#### GET /prompts/custom/{id}
- [ ] **T041**: Get own custom prompt (200)
- [ ] **T042**: Get another user's custom prompt (404)
- [ ] **T043**: Get non-existent custom prompt (404)
- [ ] **T044**: Get inactive custom prompt (404)
- [ ] **T045**: Get custom prompt without authentication (401)

#### POST /prompts/custom
- [ ] **T046**: Create custom prompt with valid data (201)
- [ ] **T047**: Create custom prompt with missing name (422)
- [ ] **T048**: Create custom prompt with missing prompt_text (422)
- [ ] **T049**: Create custom prompt without authentication (401)
- [ ] **T050**: Verify created prompt belongs to authenticated user
- [ ] **T051**: Verify created prompt is active by default
- [ ] **T052**: Database rollback on commit failure

#### PATCH /prompts/custom/{id}
- [ ] **T053**: Update own custom prompt name (200)
- [ ] **T054**: Update own custom prompt text (200)
- [ ] **T055**: Update own custom prompt both fields (200)
- [ ] **T056**: Update with empty patch (200, no changes)
- [ ] **T057**: Update another user's custom prompt (404)
- [ ] **T058**: Update non-existent custom prompt (404)
- [ ] **T059**: Update without authentication (401)
- [ ] **T060**: Database rollback on commit failure

#### DELETE /prompts/custom/{id}
- [ ] **T061**: Delete own custom prompt (204)
- [ ] **T062**: Delete another user's custom prompt (404)
- [ ] **T063**: Delete non-existent custom prompt (404)
- [ ] **T064**: Delete already deleted prompt (404)
- [ ] **T065**: Delete without authentication (401)
- [ ] **T066**: Verify soft delete (is_active=false)
- [ ] **T067**: Verify deleted prompt not in list
- [ ] **T068**: Database rollback on commit failure

---

### 4. Chat Tests (`/chats`)

#### GET /chats
- [ ] **T069**: List chats for authenticated user (200)
- [ ] **T070**: List chats with pagination (200)
- [ ] **T071**: List chats with ordering (200)
- [ ] **T072**: Verify only user's own chats returned
- [ ] **T073**: Verify other users' chats not visible
- [ ] **T074**: List chats without authentication (401)

#### GET /chats/{id}
- [ ] **T075**: Get own chat (200)
- [ ] **T076**: Get another user's chat (404)
- [ ] **T077**: Get non-existent chat (404)
- [ ] **T078**: Get inactive chat (404)
- [ ] **T079**: Get chat without authentication (401)

#### PATCH /chats/{id}
- [ ] **T080**: Update chat enable_ai_check (200)
- [ ] **T081**: Update chat prompts_threshold (200)
- [ ] **T082**: Update chat custom_prompt_threshold (200)
- [ ] **T083**: Update chat cleanup_mentions (200)
- [ ] **T084**: Update chat cleanup_emojis (200)
- [ ] **T085**: Update chat cleanup_links (200)
- [ ] **T086**: Update chat allowed_link_domains (200)
- [ ] **T087**: Update multiple fields at once (200)
- [ ] **T088**: Update with empty patch (200, no changes)
- [ ] **T089**: Update another user's chat (404)
- [ ] **T090**: Update non-existent chat (404)
- [ ] **T091**: Update with invalid threshold value (422)
- [ ] **T092**: Update without authentication (401)
- [ ] **T093**: Database rollback on commit failure

---

### 5. User State Tests (`/chats/{chat_id}/user-states`)

#### GET /chats/{chat_id}/user-states
- [ ] **T094**: List user states for own chat (200)
- [ ] **T095**: List user states with pagination (200)
- [ ] **T096**: List user states with ordering (200)
- [ ] **T097**: Verify pagination metadata includes total
- [ ] **T098**: List user states for another user's chat (404)
- [ ] **T099**: List user states for non-existent chat (404)
- [ ] **T100**: List user states without authentication (401)

#### PATCH /chats/{chat_id}/user-states/{state_id}
- [ ] **T101**: Update user state trusted to true (200)
- [ ] **T102**: Update user state trusted to false (200)
- [ ] **T103**: Update user state in own chat (200)
- [ ] **T104**: Update user state in another user's chat (404)
- [ ] **T105**: Update non-existent user state (404)
- [ ] **T106**: Update user state without authentication (401)
- [ ] **T107**: Database rollback on commit failure

#### POST /chats/{chat_id}/user-states/{state_id}/make-untrusted
- [ ] **T108**: Reset user to untrusted (200)
- [ ] **T109**: Verify trusted set to false (200)
- [ ] **T110**: Verify valid_messages reset to 0 (200)
- [ ] **T111**: Reset user in own chat (200)
- [ ] **T112**: Reset user in another user's chat (404)
- [ ] **T113**: Reset non-existent user state (404)
- [ ] **T114**: Reset without authentication (401)
- [ ] **T115**: Database rollback on commit failure

---

### 6. Route Conflict Tests

#### Route Priority
- [ ] **T116**: GET /prompts/custom returns custom prompts list (not 404)
- [ ] **T117**: GET /prompts/{valid_uuid} returns system prompt
- [ ] **T118**: GET /prompts/custom/{valid_uuid} returns custom prompt
- [ ] **T119**: Verify "custom" not interpreted as UUID

---

### 7. Database Tests

#### Connection Pool
- [ ] **T120**: Verify connection pool size is 10
- [ ] **T121**: Verify max overflow is 20
- [ ] **T122**: Verify pool timeout is 30 seconds
- [ ] **T123**: Verify pool recycle is 3600 seconds
- [ ] **T124**: Test connection pool under load (30+ concurrent requests)

#### Transactions
- [ ] **T125**: Verify rollback on registration failure
- [ ] **T126**: Verify rollback on custom prompt creation failure
- [ ] **T127**: Verify rollback on custom prompt update failure
- [ ] **T128**: Verify rollback on custom prompt deletion failure
- [ ] **T129**: Verify rollback on chat update failure
- [ ] **T130**: Verify rollback on user state update failure
- [ ] **T131**: Verify rollback on make-untrusted failure

#### Relationships
- [ ] **T132**: Verify User.chats relationship works
- [ ] **T133**: Verify User.custom_prompts relationship works
- [ ] **T134**: Verify Chat.user relationship works
- [ ] **T135**: Verify Chat.user_states relationship works
- [ ] **T136**: Verify CustomPrompt.user relationship works
- [ ] **T137**: Verify UserState.chat relationship works
- [ ] **T138**: Verify cascade delete on user deletion

---

### 8. Security Tests

#### JWT Token
- [ ] **T139**: Verify JWT_SECRET is required (app fails without it)
- [ ] **T140**: Verify token expiry after 7 days
- [ ] **T141**: Verify token contains correct user ID
- [ ] **T142**: Verify token signature validation
- [ ] **T143**: Verify tampered token rejected (401)

#### Password Security
- [ ] **T144**: Verify password is hashed (not stored plain)
- [ ] **T145**: Verify bcrypt is used for hashing
- [ ] **T146**: Verify password not returned in responses

#### Ownership Validation
- [ ] **T147**: User cannot access another user's custom prompts
- [ ] **T148**: User cannot access another user's chats
- [ ] **T149**: User cannot modify another user's chat settings
- [ ] **T150**: User cannot modify another user's user states

---

### 9. CORS Tests

#### CORS Headers
- [ ] **T151**: Verify CORS allows all origins (*)
- [ ] **T152**: Verify CORS allows credentials
- [ ] **T153**: Verify CORS allows all methods
- [ ] **T154**: Verify CORS allows all headers
- [ ] **T155**: Verify preflight OPTIONS requests work

---

### 10. OpenAPI Documentation Tests

#### Swagger UI
- [ ] **T156**: Verify /docs endpoint accessible
- [ ] **T157**: Verify all endpoints documented
- [ ] **T158**: Verify request schemas documented
- [ ] **T159**: Verify response schemas documented
- [ ] **T160**: Verify tags present (auth, prompts, chats, user_states)

#### ReDoc
- [ ] **T161**: Verify /redoc endpoint accessible
- [ ] **T162**: Verify API description present

---

### 11. Health Check Tests

#### Health Endpoint
- [ ] **T163**: GET /health returns 200
- [ ] **T164**: GET /health returns correct JSON structure
- [ ] **T165**: GET /health accessible without authentication

---

### 12. Error Handling Tests

#### HTTP Status Codes
- [ ] **T166**: Verify 201 on successful creation
- [ ] **T167**: Verify 204 on successful deletion
- [ ] **T168**: Verify 401 on missing authentication
- [ ] **T169**: Verify 403 on inactive user login
- [ ] **T170**: Verify 404 on not found
- [ ] **T171**: Verify 409 on duplicate email
- [ ] **T172**: Verify 422 on validation error
- [ ] **T173**: Verify 500 on database error

#### Error Messages
- [ ] **T174**: Verify error messages are descriptive
- [ ] **T175**: Verify error messages don't leak sensitive info
- [ ] **T176**: Verify validation errors include field names

---

### 13. Logging Tests

#### Structured Logging
- [ ] **T177**: Verify logs are JSON formatted
- [ ] **T178**: Verify user registration logged
- [ ] **T179**: Verify user login logged
- [ ] **T180**: Verify custom prompt operations logged
- [ ] **T181**: Verify chat updates logged
- [ ] **T182**: Verify user state changes logged
- [ ] **T183**: Verify errors logged with details

---

### 14. Performance Tests

#### Response Time
- [ ] **T184**: List endpoints respond < 500ms
- [ ] **T185**: Get endpoints respond < 200ms
- [ ] **T186**: Create endpoints respond < 500ms
- [ ] **T187**: Update endpoints respond < 500ms

#### Pagination
- [ ] **T188**: Large result sets paginate correctly
- [ ] **T189**: Page size limit enforced (max 100)
- [ ] **T190**: Total count accurate for filtered results

---

### 15. Integration Tests

#### End-to-End Flows
- [ ] **T191**: Register → Login → Get Profile
- [ ] **T192**: Register → Create Custom Prompt → List → Update → Delete
- [ ] **T193**: Register → List Chats → Update Chat → Get Chat
- [ ] **T194**: Register → List User States → Update Trust → Reset
- [ ] **T195**: Multiple users with isolated data

---

## Test Execution Priority

### P0 - Critical (Must Pass)
- All authentication tests (T001-T019)
- Route conflict tests (T116-T119)
- Security tests (T139-T150)
- Database transaction tests (T125-T131)

### P1 - High (Should Pass)
- All CRUD operation tests (T020-T115)
- Error handling tests (T166-T176)
- Ownership validation tests (T147-T150)

### P2 - Medium (Nice to Have)
- Performance tests (T184-T190)
- Integration tests (T191-T195)
- Logging tests (T177-T183)

### P3 - Low (Optional)
- CORS tests (T151-T155)
- Documentation tests (T156-T162)
- Connection pool tests (T120-T124)

---

## Test Statistics

**Total Tests**: 195
- Authentication: 19 tests
- System Prompts: 10 tests
- Custom Prompts: 34 tests
- Chats: 25 tests
- User States: 22 tests
- Route Conflicts: 4 tests
- Database: 19 tests
- Security: 12 tests
- CORS: 5 tests
- OpenAPI: 7 tests
- Health: 3 tests
- Error Handling: 11 tests
- Logging: 7 tests
- Performance: 7 tests
- Integration: 5 tests

**Coverage Target**: 80%+ code coverage
**Estimated Execution Time**: ~15-20 minutes for full suite
