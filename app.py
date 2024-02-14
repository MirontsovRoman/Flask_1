from random import choice
from flask import Flask, request, jsonify

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


about_me = {
   "name": "Вадим",
   "surname": "Шиховцов",
   "email": "vshihovcov@specialist.ru"
}

quotes = [
   {
       "id": 3,
       "author": "Rick Cook",
       "text": "Программирование сегодня — это гонка разработчиков программ, стремящихся писать программы с большей и лучшей идиотоустойчивостью, и вселенной, которая пытается создать больше отборных идиотов. Пока вселенная побеждает."
   },
   {
       "id": 5,
       "author": "Waldi Ravens",
       "text": "Программирование на С похоже на быстрые танцы на только что отполированном полу людей с острыми бритвами в руках."
   },
   {
       "id": 6,
       "author": "Mosher’s Law of Software Engineering",
       "text": "Не волнуйтесь, если что-то не работает. Если бы всё работало, вас бы уволили."
   },
   {
       "id": 8,
       "author": "Yoggi Berra",
       "text": "В теории, теория и практика неразделимы. На практике это не так."
   },

]


@app.route("/")
def hello_world():
    return "Hello, World!"


@app.route("/about")
def about():
    return about_me


# /quotes
@app.route("/quotes")
def get_quotes():
    return quotes


# /quotes/3
# /quotes/5
# /quotes/6
# /quotes/8
@app.route("/quotes/<int:quote_id>")
def get_quote_by_id(quote_id):
    """ Function returns the quote by id. 
        Type of the quote is dict -> json str """
    for quote in quotes:
        if quote["id"] == quote_id:
            # dict -> json str
            return quote, 200
        
    return {"error": f"Quote with id={quote_id} not found"}, 404


# dict -> json str
@app.get("/quotes/count")
def quotes_count():
    return {"count": len(quotes)}, 200


# dict -> json str
@app.route("/quotes/random", methods=['GET'])
def random_quote():
    return choice(quotes), 200


@app.route("/quotes", methods=['POST'])
def create_quote():
    new_quote = request.json  # json -> dict
    last_quote = quotes[-1]
    new_id = last_quote['id'] + 1
    new_quote['id'] = new_id
    # Мы проверяем наличие ключа rating и диапазон значений, если он есть
    rating = new_quote.get("rating")
    if rating is None or rating not in range(1, 6):
        new_quote["rating"] = 1 
    quotes.append(new_quote)
    return jsonify(new_quote), 201


@app.route("/quotes/<int:quote_id>", methods=['PUT'])
def edit_quote(quote_id):
    new_data = request.json
    if not set(new_data.keys()) - set(('author', 'text', 'rating')):
        for quote in quotes:
            if quote["id"] == quote_id:          
                if "rating" in new_data and new_data["rating"] not in range(1, 6):
                # Валидируем новое значение рейтинга, в случае успеха обновляем
                    new_data.pop("rating")
                quote.update(new_data)
                return jsonify(quote), 200
    else:
        return {"error": f"Get bad data to update"}, 400
    return {"error": f"Цитата c id={quote_id} не найдена"}, 404


@app.delete("/quotes/<int:quote_id>")  # @app.route("/quotes/<int:quote_id>", methods=["DELETE"])
def delete_quote(quote_id):
    for quote in quotes:
        if quote["id"] == quote_id:
            quotes.remove(quote)
            return jsonify({"message": f'Quote with id={quote_id} has deleted'}), 200
    return {"error": f"Quote with id={quote_id} not found"}, 404




if __name__ == "__main__":
    app.run(debug=True)