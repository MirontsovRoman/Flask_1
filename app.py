from flask import Flask, jsonify, abort, request
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path
from werkzeug.exceptions import HTTPException
from flask_migrate import Migrate


BASE_DIR = Path(__file__).parent

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{BASE_DIR / 'quotes.db'}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Для вывода содержимого SQL запросов
# app.config["SQLALCHEMY_ECHO"] = True

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class AuthorModel(db.Model):
    __tablename__ = "authors"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True, nullable=False)
    quotes = db.relationship('QuoteModel', backref='author', lazy='dynamic', cascade="all, delete-orphan")

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'Author({self.name})'
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }


class QuoteModel(db.Model):
    __tablename__ = "quotes"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey(AuthorModel.id), nullable=False)
    text = db.Column(db.String(255), unique=False, nullable=False)
    rating = db.Column(db.Integer, unique=False, nullable=False, default="1", server_default="3")

    def __init__(self, author, text, rating):
        self.author_id = author.id
        self.text  = text
        self.rating = rating

    def __repr__(self):
        return f'Quote({self.text})'
       
    def to_dict(self):
        return {
            "id": self.id,
            "author": self.author_id,
            "text": self.text,
            "rating": self.rating
        }


def validate(in_data: dict, method="post") -> dict:
    rating = in_data.setdefault("rating", 1)
    if rating not in range(1, 6) and method == "post":
        in_data["rating"] = 1
    elif rating not in range(1, 6) and method == "put":
        in_data.pop("rating")
    in_data.setdefault("text", "text")
    return in_data


# Обработка ошибок и возврат сообщения в виде JSON
@app.errorhandler(HTTPException)
def handle_exception(e):
    return jsonify({"message": e.description}), e.code


@app.route("/authors", methods=["GET", "POST"])
def handle_authors():
    if request.method == "GET":
        authors = AuthorModel.query.all()
        authors_dict = []
        for author in authors:
            authors_dict.append(author.to_dict())
        return jsonify(authors_dict), 200 
      
    if request.method == "POST":
        author_data = request.json
        author = AuthorModel(author_data.get("name", "Ivan"))
        db.session.add(author)
        try:
            db.session.commit()
            return jsonify(author.to_dict()), 201
        except:       
            abort(400, "UNIQUE constraint failed")


@app.get("/authors/<int:author_id>")
def get_author(author_id):
    author = AuthorModel.query.get(author_id)
    if author:
        return jsonify(author.to_dict()), 200
    abort(404, f"Author with id = {author_id} not found")


# GET на url: /authors/<int:id>/quotes      # получить все цитаты автора с quote_id = <int:quote_id>
@app.get("/authors/<int:author_id>/quotes")
def get_quote_by_author(author_id):
    quotes_lst = db.session.query(QuoteModel).filter_by(author_id=author_id)   
    quotes_lst_dct = []
    for quote in quotes_lst:
        quotes_lst_dct.append(quote.to_dict())
    return jsonify(quotes_lst_dct), 200


@app.put("/authors/<int:author_id>")
def edit_author(author_id):
    new_data = request.json
    author = AuthorModel.query.get(author_id)
    if not author:
        abort(404, f"Author with id = {author_id} not found")

    # Универсальный случай
    for key, value in new_data.items():
        setattr(author, key, value)
    try:
        db.session.commit()
        return jsonify(author.to_dict()), 200
    except:
        abort(400, f"Database commit operation failed.")


@app.delete("/authors/<int:author_id>")
def delete_author(author_id):
    author = AuthorModel.query.get(author_id)
    if not author:
        abort(404, f"Author with id = {author_id} not found")
    db.session.delete(author)
    try:
        db.session.commit()
        return jsonify(message=f"Author with id={author_id} deleted successfully"), 200
    except:
        abort(400, f"Database commit operation failed.")


@app.route("/authors/<int:author_id>/quotes", methods=["POST"])
def create_quote_to_author(author_id):
    """ function to create new quote to author"""
    author = AuthorModel.query.get(author_id)
    data = request.json
    # Валидация данных
    data = validate(data)

    # После валидации создаем новую цитату
    new_quote = QuoteModel(author, **data)
    db.session.add(new_quote)
    try:
        db.session.commit()
        return new_quote.to_dict(), 201
    except:
        abort(400, f"Database commit operation failed.")


@app.route("/quotes")
def get_quotes():
    """ Сериализация: list[quotes] -> list[dict] -> str(JSON) """
    quotes_db = QuoteModel.query.all()
    quotes = []
    for quote_db in quotes_db:
        quotes.append(quote_db.to_dict())
    
    return jsonify(quotes), 200


@app.get("/quotes/<int:quote_id>")
def get_quote_by_id(quote_id):
    quote = QuoteModel.query.get(quote_id)
    if quote:
        return jsonify(quote.to_dict()), 200
    abort(404, f"Quote with id={quote_id} not found")


@app.post("/quotes")
def create_quote():
    data = request.json

    new_quote = QuoteModel(**data)

    db.session.add(new_quote)
    try:
        db.session.commit()
        return jsonify(new_quote.to_dict()), 200
    except:       
        abort(400, "NOT NULL constraint failed")



@app.delete("/quotes/<int:quote_id>")
def delete(quote_id):
    quote = db.session.get(QuoteModel, quote_id)
    if quote is not None:
        db.session.delete(quote)
        db.session.commit()
        return jsonify(message=f"Row with id={quote_id} deleted."), 200
    abort(404, f"Quote id = {quote_id} not found")


@app.put("/quotes/<int:quote_id>")
def edit_quote(quote_id):
    data = request.json
    quote = QuoteModel.query.get(quote_id)
    if not quote:
        abort(404, f"Quote id = {quote_id} not found")

    # Валидация данных
    data = validate(data, "put")
        
    # Универсальный случай
    for key, value in data.items():
        setattr(quote, key, value)

    try:
        db.session.commit()
        return jsonify(quote.to_dict()), 200
    except:
        abort(500)


@app.route("/quotes/filter")
def get_quotes_by_filter():
    kwargs = request.args

    # Универсальное решение  
    quotes_db = QuoteModel.query.filter_by(**kwargs).all()

    if quotes_db:
        quotes = []
        for quote in quotes_db:
            quotes.append(quote.to_dict())      
        return jsonify(quotes), 200
    return jsonify([]), 200


if __name__ == "__main__":
    app.run(debug=True)