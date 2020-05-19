-- Initialize the database.
-- Drop any existing data and create empty tables and view.

DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS stock;
DROP TRIGGER IF EXISTS add_seq;
DROP TRIGGER IF EXISTS reorder;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE stock (
  user_id INTEGER NOT NULL,
  idx TEXT NOT NULL,
  code TEXT NOT NULL,
  seq INTEGER DEFAULT 0,
  FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TRIGGER add_seq AFTER INSERT ON stock
BEGIN
    UPDATE stock SET seq = (SELECT MAX(seq) + 1 FROM stock WHERE user_id = new.user_id)
    WHERE user_id = new.user_id AND idx = new.idx AND code = new.code;
END;

CREATE TRIGGER reorder AFTER DELETE ON stock
BEGIN
    UPDATE stock SET seq = seq - 1
    WHERE user_id = old.user_id AND seq > old.seq;
END;

INSERT INTO user
  (id, username, password)
VALUES
  (0, 'guest', ''),
  (1, 'sunshine', '123456');

INSERT INTO stock
  (user_id, idx, code)
VALUES
  (0, 'SSE', '000001'),
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
