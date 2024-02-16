from flask import Flask, jsonify, abort, request
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path
from werkzeug.exceptions import HTTPException
from flask_migrate import Migrate


BASE_DIR = Path(__file__).parent

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{BASE_DIR / 'main.db'}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Для вывода содержимого SQL запросов
# app.config["SQLALCHEMY_ECHO"] = True

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class QuoteModel(db.Model):
    __tablename__ = "quotes"
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(32), unique=False, nullable=False)
    text = db.Column(db.String(255), unique=False, nullable=False)

    def __init__(self, author, text):
        self.author = author
        self.text  = text

    def __repr__(self):
        return f'Quote({self.author}, {self.text})'
    
    @staticmethod
    def validate(in_data):
        return set(in_data.keys()) == set(("author", "text"))
    
    def to_dict(self):
        return {
            "id": self.id,
            "author": self.author,
            "text": self.text
        }


# Обработка ошибок и возврат сообщения в виде JSON
@app.errorhandler(HTTPException)
def handle_exception(e):
    return jsonify({"message": e.description}), e.code



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
    if QuoteModel.validate(data):
        new_quote = QuoteModel(**data)

        db.session.add(new_quote)
        try:
            db.session.commit()
            return jsonify(new_quote.to_dict()), 200
        except:       
            abort(400, "NOT NULL constraint failed")
    else:
        abort(400, "Bad data")


if __name__ == "__main__":
    app.run(debug=True)