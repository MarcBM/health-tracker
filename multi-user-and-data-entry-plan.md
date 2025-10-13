# Multi-user, Data Entry, and User Settings

## Overview
Add multi-user support with (user_id, date) uniqueness for `daily_data`, per-user `UserSettings`, and UI controls to select the viewed user. Phase 1 defers permissions and prefill; focus on schema, settings, APIs, dashboard/UI wiring, and seeding two users.

## Phase 1 scope (no permissions, no prefill)
- No permission enforcement on POST upserts yet; ownership checks come in Phase 2
- No server-side prefill; data entry will not prefill yet

## Database changes
- `app/database/dailyData.py`
  - Add `user_id` (FK to `users.id`), add unique constraint `(user_id, date)`
  - Add basic-calorie fields: `calories_total_goal`, `calories_total_actual`
- `app/database/user_settings.py` (new)
  - `user_id` (PK/FK)
  - Viewer default: `default_view_user_id`
  - Calories mode: `advanced_calorie_mode` (boolean; true = advanced 3-color mode, false = basic single total)
  - Module toggles: `track_calories`, `track_steps`, `track_cardio`, `track_strength`, `track_physio`, `track_weight` (all default true)
  - Goals: `cardio_daily_minutes_goal`, `cardio_weekly_low_minutes_goal`, `cardio_weekly_high_minutes_goal`, `strength_weekly_workouts_goal`
  - Notifications: `show_missing_data_notifications`
- Reset DB: drop dummy data and recreate tables

## APIs
- Settings router (`/api/settings`)
  - GET `/api/settings?user_id=<int>`: return settings for that user (viewers can read fields needed for dashboard)
  - GET `/api/settings`: shorthand for current user
  - POST `/api/settings`: upsert current user’s settings
- Users router
  - GET `/api/users`: list users for navbar selector
- Daily data router
  - GET `/api/daily-data?date=YYYY-MM-DD&user_id=<int>`: return row or nulls (no prefill in Phase 1)
  - POST `/api/daily-data`: upsert body including `user_id` (Phase 1: no permission enforcement)
- Dashboard/missing-data
  - Thread `user_id` through existing endpoints so UI fetches are user-scoped

## Frontend/UI
- Navbar (`app/templates/includes/navbar.html`)
  - Add user selector (populated from `/api/users`), persist `user_id` in localStorage
  - Add Settings link to `/settings`
- Settings page `/settings`
  - Viewer: `default_view_user_id`, notifications toggle
  - Editor: `advanced_calorie_mode`, module toggles, cardio/strength goals, viewer default, notifications
- Dashboard JS
  - Include `user_id` in requests
  - Cardio goals: replace hard-coded 150/120/30 with values from settings
  - Strength overlay threshold: replace hard-coded 5 with `strength_weekly_workouts_goal`
  - Calories chart: when `advanced_calorie_mode` is false, render a single blue line/area; when true, keep 3-color scheme
  - Hide disabled modules based on settings module toggles
- Data entry (scaffold only in Phase 1)
  - Route `/data-entry?date=...&user_id=...`; include `user_id` when fetching/saving
  - No prefill, no permission gating yet

## Seeding
- Create two users (editor, viewer) via `init_db.py` or `create_user.py`
- Update `generate_dummy_data.py` to seed per `user_id` across a date range; run after schema reset

## Testing notes
- Verify dashboard switches when changing navbar `user_id`
- Verify calories chart mode toggles (3-color vs single blue)
- Verify disabled modules don’t render in dashboard
- Verify cardio/strength goals read from settings

## To-dos
- [ ] DB: Add `user_id` unique `(user_id,date)` to `DailyData`
- [ ] DB: Add `calories_total_goal` and `calories_total_actual` to `DailyData`
- [ ] DB: Create `UserSettings` model (advanced_calorie_mode, module toggles, cardio/strength goals, default_view_user_id, notifications)
- [ ] DB: Reset schema and remove dummy data
- [ ] Seeding: Create two users (editor, viewer)
- [ ] Seeding: Generate per-user dummy data across date range
- [ ] API: GET `/api/users` for selector
- [ ] API: `/api/settings` (GET ?user_id, POST current user)
- [ ] API: `/api/daily-data` GET/POST with `user_id` (no permissions/prefill in Phase 1)
- [ ] API: Thread `user_id` through dashboard and missing-data endpoints
- [ ] UI: Navbar user selector and Settings link to `/settings`
- [ ] UI: Build `/settings` page and JS
- [ ] UI: Update dashboard JS (cardio goals 150/120/30 → settings; strength weekly 5 → settings; calories basic = blue; hide disabled modules)
- [ ] UI: Scaffold data entry page/JS with `user_id`
