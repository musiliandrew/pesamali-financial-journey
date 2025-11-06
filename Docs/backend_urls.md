# Backend URL Map and Implementation Status

This document tracks the backend endpoints per app, based on the Docs spec (README + Docs/about.txt + pesamali_rules.md), and their current implementation status.

Legend:
- [x] Implemented
- [ ] Not yet
- [~] Planned/placeholder (wired but needs full logic)

---

## Accounts App

Goals:
- Users CRUD-lite, points updates, profile access
- Friends invites/acceptance, list, streak sacrifice

Endpoints:
- [x] POST `/users` — Create user + profile (DB-backed)
- [x] GET `/users/<id>` — Get user by ID (DB-backed)
- [x] GET `/users/me` — Authenticated current user (requires real auth integration later)
- [x] POST `/users/points` — Update PesaMali points (DB-backed)
- [x] GET `/users/` — List users (DB-backed)
- [x] GET `/users/mock` — Alias to list users for frontend compatibility (DB-backed)
- [x] GET `/friends` — List current user’s friends (DB-backed)
- [x] GET `/friends/<userId>` — List a user’s friends (DB-backed)
- [x] POST `/friends/invite` — Send friend invite (DB-backed)
- [x] POST `/friends/accept` — Accept friend invite (DB-backed)
- [~] POST `/friends/challenge` — Q/A challenge (placeholder; waits for QA app model)
- [x] POST `/friends/sacrifice` — Sacrifice points to save friend’s streak (DB-backed)

Gaps:
- Integrate real authentication (JWT/Clerk) for `/users/me` and friends endpoints.
- Add rate limiting and input validation schemas.

---

## Game App

Goals:
- Match lifecycle, turns, dice, moves, asset selection, authoritative state
- Real-time updates via WebSocket

Endpoints:
- [x] POST `/matches` — Create match (DB-backed: GameRooms)
- [x] POST `/matches/<matchId>/join` — Join match (DB-backed: GamePlayers)
- [x] POST `/matches/<matchId>/start` — Start match (DB-backed)
- [x] GET `/matches/<matchId>/state` — Current state snapshot (DB-backed)
- [x] POST `/matches/<matchId>/roll` — Roll dice (RNG; needs turn validation)
- [x] POST `/matches/<matchId>/move` — Move token (basic move; needs full rule engine)
- [x] POST `/matches/<matchId>/select-asset` — Select/purchase asset (stores asset ids)
- [~] WS `/matches/<matchId>/stream` — WebSocket stream (wired, placeholder; needs event broadcasting)

Rules to implement next (per docs):
- [ ] Turn/seat tracking and validation.
- [ ] Yellow-strip priority and −20 penalty on skip.
- [ ] Asset purchase constraints (no first asset in 1–10; second asset after window or 5 returns).
- [ ] Asset returns logic (next phase, odd tiles, max 5, one per landing).
- [ ] Win conditions (2 assets, savings ≥ 500, liabilities 0, all cards resolved, dream affordable).
- [ ] Events: dice_result, move_event, state_update, turn_change broadcast to WS subscribers.

---

## Cards App

Goals:
- Manage decks (playing/yellow-strip, savings, spending); card resolution and effects

Endpoints:
- [x] POST `/matches/<matchId>/cards/draw` — Draw playing card on yellow-strip, apply effect to Income/Liabilities.
- [x] POST `/matches/<matchId>/cards/savings` — Play a savings card (apply thresholds/bonuses, update savings).
- [x] POST `/matches/<matchId>/cards/spending` — Play a spending card (apply liabilities, update state).
- [x] GET `/decks` — Summaries for UI (optional; can be derived from DB).

Notes:
- Effects must reflect advanced rules (no movement effects at advanced level).
- Integrate with Game state updates and WS broadcasting.

---

## Dreams App

Goals:
- Dream catalog and purchase when conditions met

Endpoints:
- [x] GET `/dreams` — List available dreams.
- [x] POST `/matches/<matchId>/dreams/purchase` — Purchase dream (enforce assets-profit funding and win checks).

---

## Societies App

Goals:
- Manage societies, membership, leaderboards per society

Endpoints:
- [x] GET `/societies` — List societies / rankings.
- [x] POST `/societies` — Create society.
- [x] POST `/societies/<id>/join` — Join a society.
- [x] GET `/societies/<id>` — Society details and leaderboard.

---

## Leaderboard App

Goals:
- Global rankings, seasonal or profession-based

Endpoints:
- [x] GET `/leaderboard/global` — Global ranking.
- [x] GET `/leaderboard/profession/<profession>` — Profession-specific ranking.

---

## QA App (Challenges)

Goals:
- Q/A challenges for streak protection and learning mechanics

Endpoints:
- [x] POST `/qa/challenge` — Create/send challenge.
- [x] POST `/qa/answer` — Submit an answer.
- [x] GET `/qa/challenges` — List incoming challenges.

Notes:
- Accounts `/friends/challenge` should delegate to QA now that models and endpoints exist.

---

## Shop App (Cosmetics)

Goals:
- Cosmetic items purchasing with PesaMali points (and later real money)

Endpoints (to implement):
- [ ] GET `/shop/items` — List items (DB-backed).
- [ ] POST `/shop/purchase` — Purchase an item; record receipt.

---

## Cross-cutting

- Auth: JWT-based auth in Accounts
  - [x] POST `/auth/register` — Create user and return JWT
  - [x] POST `/auth/login` — Return JWT
  - Frontend uses `localStorage.jwt` and `useBackend()` attaches `Authorization: Bearer <token>`
  - `useAuth()` hook added for register/login/logout
- CORS: Configured for Vite dev origins.
- Telemetry/Analytics: (future) record events for dashboards.
- Performance: Add pagination to listing endpoints as needed.

---

## Current Implementation Summary

- Accounts: Users CRUD-lite + points [x], Friends core [x], Challenge placeholder [~]
- Game: Match lifecycle [x], State [x], Dice [x], Move [x] with yellow-strip penalty and returns, Asset select [x], WS stream [x] broadcasting
- Cards: [x]
- Dreams: [x]
- Societies: [x]
- Leaderboard: [x]
- QA: [ ]
- Shop: [ ]

---

## Next Suggested Milestones

1) Game rule engine (turns, yellow-strip, assets returns, win checks) + WS broadcasting [Game]
2) Card resolution endpoints [Cards] integrated into move flow
3) Dream purchase endpoint with win validation [Dreams]
4) QA challenges backing for `/friends/challenge` [QA]
5) Societies listing/join and basic leaderboards [Societies/Leaderboard]
