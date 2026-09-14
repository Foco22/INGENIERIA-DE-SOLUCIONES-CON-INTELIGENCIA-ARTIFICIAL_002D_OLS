-- Schema del Job Match Agent. Tablas y columnas en ingles.

CREATE TABLE IF NOT EXISTS jobs (
  id            TEXT PRIMARY KEY,           -- hash estable de job_url
  site          TEXT,
  title         TEXT NOT NULL,
  company       TEXT,
  location      TEXT,
  date_posted   TEXT,
  job_url       TEXT UNIQUE NOT NULL,
  description   TEXT,
  is_remote     INTEGER,
  min_amount    REAL,
  max_amount    REAL,
  currency      TEXT,
  raw_json      TEXT,                       -- fila original de JobSpy
  status        TEXT NOT NULL DEFAULT 'pending',   -- pending | evaluated | error
  ingested_at   TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);

CREATE TABLE IF NOT EXISTS evaluations (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  job_id          TEXT NOT NULL REFERENCES jobs(id),
  run_id          TEXT NOT NULL,
  score           INTEGER NOT NULL CHECK (score BETWEEN 1 AND 10),
  band            TEXT NOT NULL,            -- pessimistic | neutral | optimistic
  review          TEXT NOT NULL,            -- el comentario, en espanol
  strengths_json  TEXT,
  gaps_json       TEXT,
  deal_breaker    TEXT,
  model           TEXT,
  prompt_version  TEXT,
  tokens          INTEGER,
  created_at      TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (job_id, run_id)
);

CREATE INDEX IF NOT EXISTS idx_evaluations_run ON evaluations(run_id);

CREATE TABLE IF NOT EXISTS runs (
  run_id          TEXT PRIMARY KEY,
  started_at      TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  finished_at     TEXT,
  n_jobs          INTEGER,
  profile_hash    TEXT,
  prompt_version  TEXT
);
