CREATE TABLE IF NOT EXISTS "master_password" (
  id SERIAL PRIMARY KEY,
  created TIMESTAMP NOT NULL DEFAULT now(),
  updated TIMESTAMP NOT NULL DEFAULT now(),
  deleted TIMESTAMP,
  salt BYTEA,
  hash_key text
);

CREATE TABLE IF NOT EXISTS "passwords" (
  id SERIAL PRIMARY KEY,
  created TIMESTAMP NOT NULL DEFAULT now(),
  updated TIMESTAMP NOT NULL DEFAULT now(),
  deleted TIMESTAMP,
  password_name text UNIQUE NOT NULL,
  password_value BYTEA NOT NULL,
  description text,
  backed_up BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS "settings" (
  id SERIAL PRIMARY KEY,
  created TIMESTAMP NOT NULL DEFAULT now(),
  updated TIMESTAMP NOT NULL DEFAULT now(),
  inactivity_ms INTEGER NOT NULL DEFAULT 120000,
  warn_before_ms INTEGER NOT NULL DEFAULT 60000,
  hidden_ms INTEGER NOT NULL DEFAULT 60000,
  debounce_ms INTEGER NOT NULL DEFAULT 1000,
  clipboard_clear_ms INTEGER NOT NULL DEFAULT 30000
);
