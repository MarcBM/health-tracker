## Prompt

> Familiarise yourself with the state of the application.
>
> We have now gotten the dashboard displays all functional, now we need data input to be functional as well, and the MVP of the app will be ready to deploy.
>
> Currently we are populating the database with dummy generated data, but in production there should be a form that allows me to provide all the data for the dailyData model.
>
> I would prefer to use a JS powered post request instead of a classic form, since I will want to prepopulate much of the data as well as provide client-side data validation.
>
> One of the main features I would like is to be able to either create a new database record or update an old one on the same form. The idea would be that I could always edit a previous day's data, even if some or all of it was filled in, or I could create a new day's entry.
>
> The regular flow would be to click the 'add data' link in the navbar. This would take me to yesterday's data. If yesterday's data does not exist, it sets the date field to that and populates the form based on it being 'yesterday's' data. If it does exist, then it simply populates the fields with the current data from yesterday and allows me to continue filling it out.
>
> This is because I will be normally entering the 'complete' day of data all at once the next morning. I will be keeping notes or collecting the data elsewhere, this is just a place for my own long term record keeping and accountability.
>
> However, when opening the data entry page, I would like the option to provide a date as an argument, allowing me to do the same with that date as opposed to 'yesterday'. That way, I can fill in missed days data, allowing me to make use of the notifications system. I would also like to be able to provide a 'section' (calroies, steps, cardio, etc) as an argument, which would then focus the first field of that section on load.
>
> Provide me a plan for how you would implement this.

## Plan: JS-powered data entry (create/update) for `DailyData`

- **Context confirmed**
  - Backend: FastAPI + SQLAlchemy (SQLite).
  - Frontend: Jinja2 templates + Bootstrap 5 + vanilla JS.
  - Model: `app/database/dailyData.py` (`DailyData`).
  - Dashboard APIs exist; `/data-entry` is currently a placeholder.
  - Notifications link to `/data-entry?date=...&focus=...` already.

### Backend: API contracts

- **Schemas** (`app/schemas/daily_data.py`)
  - `DailyDataIn`: fields for all `DailyData` columns; `date` required; others optional.
  - `DailyDataOut`: mirrors DB fields.

- **Endpoints** (add to `app/routers/data.py`)
  - `GET /api/daily-data?date=YYYY-MM-DD`
    - Returns the row for `date` if it exists; otherwise `{date, ...nulls}`.
    - Optionally include `last_known` (carry-forward of stable goals: calorie goals, `steps_goal`) using the most recent values before `date`.
  - `POST /api/daily-data` (upsert)
    - Body: `DailyDataIn` JSON. If row exists for `date` → update; else create.
    - Normalize empty strings to `null`; validate types; reject future dates; clamp negatives to 0 where appropriate (or 422).
    - Return `{ updated: boolean, data: DailyDataOut }`.

- **Permissions**
  - Reuse auth middleware; `POST` requires `user.can_edit == True` else 403.

### Frontend: data entry page and JS

- **Template** (`app/templates/data_entry/data_entry.html`)
  - Extends `base.html`.
  - Sections with anchors/ids: `calories`, `steps`, `cardio`, `strength`, `physio`, `weight`.
  - Controls: date picker, Save button, optional “Prev/Next day” buttons.
  - Include `{% block extra_js %}<script src="{{ url_for('static', path='/js/data-entry.js') }}"></script>{% endblock %}`.

- **Controller JS** (`static/js/data-entry.js`)
  - On load: parse `date` and `focus` from query params; default `date` to “yesterday” in Australia/Sydney.
  - Fetch `GET /api/daily-data?date=...`.
    - If exists: populate all fields.
    - If not: set date; prefill goals from `last_known` if provided; leave others blank.
  - Client-side validation: numeric coercion (ints for calories/steps/cardio, float for weight), non-negative; booleans for physio; inline errors; disable Save if invalid.
  - Save: build JSON payload (empty → null), `POST /api/daily-data`.
    - On success: show success notification; update URL to keep `date`.
    - On failure: show error notification.
  - QoL: keyboard nav; “Prev/Next day” buttons adjust date and refetch; “Copy last known goals” action for new entries.
  - If `focus` present (`calories|steps|cardio|strength|physio|weight`), scroll and focus first field of that section.

- **Navbar**
  - Keep `href="/data-entry"`; page JS defaults to yesterday. Notifications already deep-link with `date`/`focus`.

### Data mapping (model ↔ form)

- Calories: `calories_green_goal`, `calories_green_actual`, `calories_yellow_*`, `calories_orange_*`.
- Steps: `steps_goal`, `steps_actual`.
- Cardio: `cardio_high_intensity_minutes`, `cardio_low_intensity_minutes`.
- Strength: `strength_workout_type` (select with `Core|Lower Body|Upper Body|Full Body`).
- Physio: `physio_active`, `physio_completed` (checkboxes).
- Weight: `weight_kg` (number with 1 decimal step).

### UX states & defaults

- Default `date`: yesterday.
- If record exists: load and allow edits.
- If absent: set `date`; prefill stable goals from last-known; leave others blank.
- Accept `?date=YYYY-MM-DD` and `?focus=<section>` to backfill/focus.

### Testing

- Create new day; update existing; invalid inputs; future date blocked; focus param scroll/focus; notifications deep-link open with correct state.
- Verify dashboard reflects changes after save/refresh.

### Files to add/edit

- Add `app/schemas/daily_data.py`.
- Edit `app/routers/data.py` (new API endpoints; point `/data-entry` to new template).
- Add `app/templates/data_entry/data_entry.html`.
- Add `static/js/data-entry.js`.

### Future enhancements (post-MVP)

- Autosave (debounced).
- “Save & go to next missing section/day” guided flow using `checkMissingData`.
- Server-side policy to auto carry-forward goals.

### API examples

```json
POST /api/daily-data
{
  "date": "2025-08-09",
  "calories_green_goal": 1000,
  "calories_green_actual": 950,
  "calories_yellow_goal": 1500,
  "calories_yellow_actual": 1600,
  "calories_orange_goal": 800,
  "calories_orange_actual": 700,
  "steps_goal": 8000,
  "steps_actual": 7650,
  "cardio_high_intensity_minutes": 15,
  "cardio_low_intensity_minutes": 30,
  "strength_workout_type": "Upper Body",
  "physio_active": true,
  "physio_completed": true,
  "weight_kg": 101.4
}
```

```json
200 OK
{
  "updated": true,
  "data": {
    "date": "2025-08-09",
    "calories_green_goal": 1000,
    "calories_green_actual": 950,
    "calories_yellow_goal": 1500,
    "calories_yellow_actual": 1600,
    "calories_orange_goal": 800,
    "calories_orange_actual": 700,
    "steps_goal": 8000,
    "steps_actual": 7650,
    "cardio_high_intensity_minutes": 15,
    "cardio_low_intensity_minutes": 30,
    "strength_workout_type": "Upper Body",
    "physio_active": true,
    "physio_completed": true,
    "weight_kg": 101.4
  }
}
```

### Routing and templates

- Update `/data-entry` route in `app/routers/data.py` to render `data_entry/data_entry.html`.
- Keep dashboard and existing endpoints unchanged.

### Edge cases

- Prevent saving future dates.
- Handle empty bodies (no-op or 422).
- Ensure booleans parse correctly from checkboxes.

### Deployment

- No DB migrations required.
- Add new JS/template files; redeploy app.

