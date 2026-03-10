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
