-- Drop any existing data.

DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS stock;
DROP TRIGGER IF EXISTS add_seq;
DROP TRIGGER IF EXISTS reorder;
