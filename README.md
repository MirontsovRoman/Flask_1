# Flask1 12022024

### Установка CLI клиента для `sqlite3`
```bash
sudo apt install sqlite3
```
### Создание БД и загрузка данных в терминале
```bash
sqlite3 quotes.db ".read sqlite3_examples/quotes_db.sql"
```  

### Создание БД с помощью `SQLAlchemy` в `ipython`
```python
from app import app, db, QuoteModel
app.app_context().push()
db.create_all()
```

## Students repos
 - [one](https://github.com/coalesca/Flask1_12022024.git)  
 - [two](https://github.com/ReQuest2024/Flask1.git)  
 - [three](https://github.com/NikolayMakovetsky/flask_restapi.git)  

### URLs
URL |  Methods Allowed | Methods Not Allowed
----|------|-----
/quotes | GET, POST, DELETE | PUT
/quotes/id | GET, PUT, DELETE | POST

### Установка `ipython` в качестве интерпретатора для `flask shell`
```bash
pip install flask-shell-ipython
```

#### Запуск `ipython` в контексте `flask` приложения
```
flask shell
```