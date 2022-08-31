CREATE TABLE IF NOT EXISTS "master_password" (
  id SERIAL PRIMARY KEY,
  created TIMESTAMP NOT NULL DEFAULT now(),
  updated TIMESTAMP NOT NULL DEFAULT now(),
  deleted TIMESTAMP,
  salt BYTEA,
  hash_key text
);

CREATE TABLE IF NOT EXISTS "password" (
  id SERIAL PRIMARY KEY,
  created TIMESTAMP NOT NULL DEFAULT now(),
  updated TIMESTAMP NOT NULL DEFAULT now(),
  deleted TIMESTAMP,
  password_name text,
  password_value text,
  description text
);
