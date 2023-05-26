from flask import Flask, render_template, request, url_for, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.sqlite3"
app.config["SECRET_KEY"] = "secret"
db = SQLAlchemy(app)


class User_Class(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    u_id = db.Column(db.String(20))
    u_pw = db.Column(db.String(20))
    u_name = db.Column(db.String(20))
    u_cash = db.Column(db.String(50))
    u_coin = db.Column(db.String(50))

    def __init__(self, id, pw, nm, cash, coin):
        self.u_id = id
        self.u_pw = pw
        self.u_name = nm
        self.u_cash = cash
        self.u_coin = coin


class Market_Class(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    m_name = db.Column(db.String(50))
    m_price = db.Column(db.Float)
    m_coin = db.Column(db.Float)

    def __init__(self, name, price, many):
        self.m_name = name
        self.m_price = price
        self.m_coin = many


# 로그인에서 이용할 수 있는 기능과 아닌 기능으로 나뉘어져 있으므로
@app.route("/", methods=["GET", "POST"])
def main():
    if request.method == "POST":
        return redirect(url_for("search", word=request.form["search"]))
    else:
        if "username" in session:
            username = session["username"]

            product_query = Market_Class.query.all()
            user_query = User_Class.query.all()

            return render_template(
                "main2.html",
                username=username,
                product_query=product_query,
                user_query=user_query,
            )
        else:
            product_query = Market_Class.query.all()
            return render_template("main.html", product_query=product_query)


@app.route("/sign", methods=["GET", "POST"])
def sign():
    if request.method == "POST":
        if not request.form["id"] or not request.form["pw"] or not request.form["nm"]:
            flash("Please enter all the fields", "error")
        else:
            user = User_Class(
                request.form["id"],
                request.form["pw"],
                request.form["nm"],
                request.form["cash"],
                request.form["coin"],
            )

            coin = Market_Class(
                request.form["name"],
                request.form["price"],
                request.form["many"],
            )

            db.session.add(user)
            db.session.add(coin)

            db.session.commit()
            return redirect(url_for("login"))
    return render_template("sign.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if not request.form["id"] or not request.form["pw"]:
            flash("Please enter all the fields", "error")
        else:
            inputId = request.form["id"]
            inputPw = request.form["pw"]
            data = User_Class.query.filter_by(u_id=inputId, u_pw=inputPw).first()

            if data is not None:
                session["username"] = inputId

                return redirect(url_for("main"))
            else:
                return render_template("login.html")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("main"))


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        if (
            not request.form["name"]
            or not request.form["price"]
            or not request.form["coin"]
        ):
            flash("Please enter all the fields", "error")
        else:
            coin = Market_Class(
                request.form["name"],
                request.form["price"],
                request.form["coin"],
            )

            db.session.add(coin)
            db.session.commit()
            return redirect(url_for("main"))
    return render_template("upload.html", username=session["username"])


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5050)
