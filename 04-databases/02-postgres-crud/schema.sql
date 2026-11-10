-- Minimal relational schema. One table.
--
-- Notes:
--   SERIAL         → auto-incrementing integer (1, 2, 3, ...)
--   PRIMARY KEY    → unique, not null, identifies the row
--   NOT NULL       → the column must have a value
--   UNIQUE         → no two rows can share this value
--
-- The schema is the contract. Every other database in this section
-- (MySQL, MongoDB, DynamoDB) stores the same three fields — but only
-- the relational ones let you *enforce* the shape at the database level.

CREATE TABLE IF NOT EXISTS users (
    id    SERIAL PRIMARY KEY,
    name  TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
);