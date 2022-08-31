CREATE TABLE IF NOT EXISTS "user" (
  id SERIAL PRIMARY KEY,
  created TIMESTAMP NOT NULL DEFAULT now(),
  updated TIMESTAMP NOT NULL DEFAULT now(),
  deleted TIMESTAMP,
  type text,
  name text,
  email text
);
COMMIT;