DROP TABLE IF EXISTS daily_data;
DROP TABLE IF EXISTS settings;
DROP TABLE IF EXISTS view_permissions;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL UNIQUE,
  hashed_password TEXT NOT NULL,
  display_name TEXT,
  is_author BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE daily_data (
  date DATE NOT NULL,
  author_id INTEGER NOT NULL,
  day_of_week TEXT NOT NULL,
  calories_green_goal INTEGER,
  calories_green_actual INTEGER,
  calories_yellow_goal INTEGER,
  calories_yellow_actual INTEGER,
  calories_orange_goal INTEGER,
  calories_orange_actual INTEGER,
  steps_goal INTEGER,
  steps_actual INTEGER,
  cardio_high_intensity_minutes INTEGER,
  cardio_low_intensity_minutes INTEGER,
  strength_workout_type TEXT,
  physio_active BOOLEAN,
  physio_completed BOOLEAN,
  weight_kg FLOAT,
  PRIMARY KEY (date, author_id),
  FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE settings (
  owner_id INTEGER PRIMARY KEY,
  view_on_load_user_id INTEGER,
  show_missing_data_notifications BOOLEAN NOT NULL DEFAULT TRUE,
  track_calories BOOLEAN NOT NULL DEFAULT TRUE,
  track_steps BOOLEAN NOT NULL DEFAULT TRUE,
  track_cardio BOOLEAN NOT NULL DEFAULT TRUE,
  track_strength BOOLEAN NOT NULL DEFAULT TRUE,
  track_physio BOOLEAN NOT NULL DEFAULT TRUE,
  track_weight BOOLEAN NOT NULL DEFAULT TRUE,
  calories_advanced_mode BOOLEAN NOT NULL DEFAULT FALSE,
  steps_automate_goal BOOLEAN NOT NULL DEFAULT TRUE,
  steps_min_goal INTEGER NOT NULL DEFAULT 2000,
  steps_max_goal INTEGER NOT NULL DEFAULT 10000,
  steps_increment_value INTEGER NOT NULL DEFAULT 500,
  steps_increment_period INTEGER NOT NULL DEFAULT 3,
  cardio_daily_minutes_goal INTEGER NOT NULL DEFAULT 15,
  cardio_weekly_low_minutes_goal INTEGER NOT NULL DEFAULT 120,
  cardio_weekly_high_minutes_goal INTEGER NOT NULL DEFAULT 30,
  strength_weekly_workouts_goal INTEGER NOT NULL DEFAULT 5,
  FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE, 
  FOREIGN KEY (view_on_load_user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE view_permissions (
  viewer_id INTEGER NOT NULL,
  can_view_id INTEGER NOT NULL,
  PRIMARY KEY (viewer_id, can_view_id),
  FOREIGN KEY (viewer_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (can_view_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_daily_data_author_date ON daily_data(author_id, date);