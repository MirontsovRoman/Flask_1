from random import choice
import sqlite3
from flask import Flask, abort, request, jsonify, g
from pathlib import Path
from werkzeug.exceptions import HTTPException


BASE_DIR = Path(__file__).parent
DATABASE = BASE_DIR / "quotes.db"  # <- тут путь к БД

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# Обработка ошибок и возврат сообщения в виде JSON
@app.errorhandler(HTTPException)
def handle_exception(e):
    return jsonify({"message": e.description}), e.code



@app.route("/")
def hello_world():
    return "Hello, World!"


@app.route("/about")
def about():
    about_me = {
   "name": "Вадим",
   "surname": "Шиховцов",
   "email": "vshihovcov@specialist.ru"
    }
    return jsonify(about_me)


# /quotes
@app.route("/quotes")
def get_quotes():
    # Получение данных из БД
    select_quotes = "SELECT * from quotes"
    cursor = get_db().cursor()
    cursor.execute(select_quotes)
    quotes_db = cursor.fetchall()  # get list[tuple]

    # Подготовка данных для возврата 
    # Необходимо выполнить преобразование:
    # list[tuple] -> list[dict]
    keys = ["id", "author", "text", "rating"]
    quotes = []
    for quote_db in quotes_db:
        quote = dict(zip(keys, quote_db))
        quotes.append(quote)

    return jsonify(quotes)


# /quotes/3
# /quotes/5
# /quotes/6
# /quotes/8
@app.route("/quotes/<int:quote_id>")
def get_quote_by_id(quote_id):
    """ Function returns the quote by id. 
        Type of the quote is dict -> json str """
    # Получение данных из БД
    select_quotes = "SELECT * FROM quotes WHERE id = ?"
    cursor = get_db().cursor()
    cursor.execute(select_quotes, (quote_id,))  # Второй аргумент - последовательность!!!
    quote_db = cursor.fetchone() # quote as tuple
    if quote_db:
        keys = ["id", "author", "text", "rating"]
        quote = dict(zip(keys, quote_db))
        return jsonify(quote), 200
    abort(404, f"Quote with id={quote_id} not found")


# dict -> json str
@app.get("/quotes/count")
def quotes_count():
    select_str = "SELECT count(*) as count FROM quotes"
    cursor = get_db().cursor()
    cursor.execute(select_str)  
    count = cursor.fetchone() 
    if count:
        return jsonify(count=count[0]), 200
    abort(503)


# dict -> json str
@app.route("/quotes/random", methods=['GET'])
def random_quote():
    select_quotes = "SELECT * FROM quotes ORDER BY RANDOM() LIMIT 1"
    cursor = get_db().cursor()
    cursor.execute(select_quotes)  
    quote_db = cursor.fetchone() # quote as tuple
    if quote_db:
        keys = ["id", "author", "text", "rating"]
        quote = dict(zip(keys, quote_db))
        return jsonify(quote), 200
    abort(503)


@app.route("/quotes", methods=['POST'])
def create_quote():
    data = request.json
    attributes = list({"author", "text", "rating"} & set(data.keys()))
    if "rating" in attributes and data["rating"] not in range(1, 6):
    # Валидируем новое значение рейтинга, в случае успеха обновляем
        data["rating"] = 1
    columns = ', '.join(attributes)
    insert_quotes = f"INSERT INTO quotes({columns}) VALUES ({', '.join('?' * len(attributes))})"
    params = tuple(data.get(attr) for attr in attributes)
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute(insert_quotes, params)
    new_id = cursor.lastrowid
    connection.commit() # Фиксируем транзакцию
    cursor.close()
    # Возвращаем созданную цитату по new_id, переиспользуем функцию для get
    response, code = get_quote_by_id(new_id)
    if code == 200:
        return response, code
    abort(507)


@app.route("/quotes/<int:quote_id>", methods=['PUT'])
def edit_quote(quote_id):
    new_data = request.json
    attributes: set = {"author", "text", "rating"} & set(new_data.keys())
    if "rating" in attributes and new_data["rating"] not in range(1, 6):
    # Валидируем новое значение рейтинга, в случае успеха обновляем
        attributes.remove("rating")
    update_quotes = f"UPDATE quotes SET {', '.join(attr + '=?' for attr in attributes)} WHERE id = ?"
    params = tuple(new_data.get(attr) for attr in attributes) + (quote_id,)

    connection = get_db()
    cursor = connection.cursor()
    cursor.execute(update_quotes, params)  
    rows = cursor.rowcount
    if rows:
        connection.commit()
        cursor.close()         
        # Возвращаем обновлённую цитату по quote_id, переиспользуем функцию для get
        response, code = get_quote_by_id(quote_id)
        if code == 200:
            return response, code
    connection.rollback()
    abort(404, f"Цитата c id={quote_id} не найдена")


@app.delete("/quotes/<int:quote_id>")  # @app.route("/quotes/<int:quote_id>", methods=["DELETE"])
def delete_quote(quote_id):
   delete_sql = f"DELETE FROM quotes WHERE id = ?"
   params = (quote_id,)
   connection = get_db()
   cursor = connection.cursor()
   cursor.execute(delete_sql, params)  
   rows = cursor.rowcount  # Кол-во измененных строк
   if rows:
      connection.commit()
      cursor.close()         
      return jsonify({"message": f"Quote with id {quote_id} has deleted."}), 200
   connection.rollback()
   abort(404, f"Quote with id={quote_id} not found")


if __name__ == "__main__":
    app.run(debug=True)