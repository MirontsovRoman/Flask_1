PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;
CREATE TABLE quotes (
id INTEGER PRIMARY KEY AUTOINCREMENT,
author TEXT NOT NULL,
text TEXT NOT NULL,
rating INTEGER
);
INSERT INTO quotes VALUES(1,'Rick Cook','Программирование сегодня — это гонка разработчиков программ...', 2);
INSERT INTO quotes VALUES(2,'Waldi Ravens','Программирование на С похоже на быстрые танцы на только...', 1);
INSERT INTO quotes VALUES(3,'Yoggi Berra','В теории, теория и практика неразделимы. На практике это не так.', 3);
COMMIT;
