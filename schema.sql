-- Initialize the database.
-- Drop any existing data and create empty tables and view.

DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS stock;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE stock
(
  user_id INTEGER NOT NULL,
  idx TEXT NOT NULL,
  code TEXT NOT NULL,
  FOREIGN KEY (user_id) REFERENCES user (id)
);

INSERT INTO user
  (id, username, password)
VALUES
  (0, 'guest', ''),
  (1, 'sunshine', '123456');

INSERT INTO stock
  (user_id, idx, code)
VALUES
  (0, 'SZSE', '399001'),
  (0, 'SZSE', '399106'),
  (0, 'SZSE', '399005'),
  (0, 'SZSE', '399006'),
  (1, 'SZSE', '002142'),
  (1, 'SSE', '601288'),
  (1, 'SSE', '600309'),
  (1, 'SSE', '510050'),
  (1, 'SSE', '513100'),
  (1, 'SSE', '513500'),
  (1, 'SSE', '518880');