from random import choice
from flask import Flask, request

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
@app.route("/quotes/count")
def quotes_count():
    return {"count": len(quotes)}, 200


# dict -> json str
@app.route("/quotes/random", methods=['GET'])
def random_quote():
    return choice(quotes), 200



@app.route("/quotes", methods=['POST'])
def create_quote():
   data = request.json  # json -> dict
   print("data = ", data, type(data))
   return {}, 201



if __name__ == "__main__":
    app.run(debug=True)