# Multi-user, Data Entry, and User Settings — Phase 1

## Intent
Implement Phase 1 multi-user support with per-user settings and user-scoped dashboard/data entry. No permission enforcement on upserts and no server-side prefill yet.

## Database
- Add `user_id` (FK to `users.id`) to `DailyData` and enforce uniqueness on `(user_id, date)`
- Add `calories_total_goal` and `calories_total_actual` to `DailyData`
- Create `UserSettings` with: `user_id` (PK/FK), `default_view_user_id`, `advanced_calorie_mode`, module toggles (`track_calories`, `track_steps`, `track_cardio`, `track_strength`, `track_physio`, `track_weight`), cardio goals (`cardio_daily_minutes_goal`, `cardio_weekly_low_minutes_goal`, `cardio_weekly_high_minutes_goal`), `strength_weekly_workouts_goal`, `show_missing_data_notifications`
- Reset DB (drop dummy data and recreate tables)

## APIs
- `/api/users` (GET): list users for navbar selector
- `/api/settings` (GET for current or `?user_id`, POST): read/upsert settings
- `/api/daily-data` (GET `?date=YYYY-MM-DD&user_id=<int>`, POST): read/upsert daily data (Phase 1: no permissions)
- Thread `user_id` through dashboard and missing-data endpoints so reads are user-scoped

## Frontend/UI
- Navbar: add user selector (from `/api/users`) and persist `user_id` in localStorage; add Settings link to `/settings`
- Settings page `/settings`: viewer default and notifications; editor toggles, goals, advanced-calorie mode
- Dashboard JS: include `user_id` in requests; read goals from settings; calories basic mode (single blue) when `advanced_calorie_mode=false`; hide disabled modules
- Data entry (scaffold): `/data-entry?date=...&user_id=...`; include `user_id` on fetch/save; no prefill or permissions

## Seeding
- Create two users (editor, viewer)
- Update `generate_dummy_data.py` to seed for each `user_id` across a date range

## Phase 1 Constraints
- No permission enforcement on POST upserts
- No server-side prefill for data entry

## Verification
- Switching navbar `user_id` updates dashboard data
- Calories chart mode toggles correctly (basic vs advanced)
- Disabled modules don’t render
- Cardio/strength goals come from settings

## Step-by-step Implementation
1. Add `user_id` FK and unique `(user_id,date)` to `DailyData`.
2. Add `calories_total_goal` and `calories_total_actual` to `DailyData`.
3. Create `UserSettings` model with fields listed above.
4. Reset DB schema (drop dummy data; recreate tables).
5. Add `/api/users` GET endpoint and include router.
6. Add `/api/settings` GET/POST endpoints and include router.
7. Add `/api/daily-data` GET/POST with `user_id` in params/body.
8. Thread `user_id` through dashboard and missing-data endpoints.
9. Add navbar user selector and persist `user_id` in localStorage.
10. Add Settings link to navbar and build `/settings` page + JS.
11. Update dashboard JS to include `user_id` and use settings for goals/modules.
12. Scaffold `/data-entry` template + JS; include `user_id` on fetch/save.
13. Seed two users; update dummy-data generator to seed per `user_id`.
