-- Initialize the database.

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL DEFAULT '123456'
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
  (0, 'guest', '');

INSERT INTO stock
  (user_id, idx, code)
VALUES
  (0, 'SSE', '000001'),
  (0, 'SZSE', '399001'),
  (0, 'SZSE', '399106'),
  (0, 'SZSE', '399005'),
  (0, 'SZSE', '399006');
