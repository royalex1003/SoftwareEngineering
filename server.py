from flask import (
    Flask,
    render_template,
    request,
    url_for,
    redirect,
    flash,
    session,
)
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.sqlite3"
app.config["SECRET_KEY"] = "secret"
db = SQLAlchemy(app)


class User_Class(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    u_id = db.Column(db.String(20))
    u_pw = db.Column(db.String(20))
    u_name = db.Column(db.String(20))
    u_cash = db.Column(db.Integer)
    u_coin = db.Column(db.Integer)
    u_value = []

    def __init__(self, id, pw, nm, cash, coin):
        self.u_id = id
        self.u_pw = pw
        self.u_name = nm
        self.u_cash = cash
        self.u_coin = coin

    def AddUserValue(self, id):
        self.u_value.append(id)


class Market_Class(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    m_price = db.Column(db.Integer)
    m_coin = db.Column(db.Integer)
    m_seller = db.Column(db.String(50))

    def __init__(self, price, many, seller):
        self.m_price = price
        self.m_coin = many
        self.m_seller = seller


class Transaction_Class(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    price = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime)

    def __init__(self, price, timestamp):
        self.price = price
        self.timestamp = timestamp

    def to_dict(self):
        return {
            "id": self.id,
            "price": self.price,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        }


@app.before_request
def perform_initial_setup():
    with app.app_context():
        # 초기 설정 데이터를 추가합니다.
        if not Market_Class.query.first() and not Transaction_Class.query.first():
            # 시장 기본 설정코인
            seller = "Market"
            price = 100
            many = 100

            model = Market_Class(price=price, many=many, seller=seller)
            db.session.add(model)
            db.session.commit()

        if not User_Class.query.first():
            id = "Market"
            pw = "asdfzcvx"
            nm = "시장"
            cash = 0
            coin = 0

            mode1 = User_Class(id=id, pw=pw, nm=nm, cash=cash, coin=coin)
            db.session.add(mode1)
            db.session.commit()


# 로그인에서 이용할 수 있는 기능과 아닌 기능으로 나뉘어져 있으므로
@app.route("/", methods=["GET", "POST"])
def main():
    if request.method == "POST":
        return redirect(url_for("search", word=request.form["search"]))
    else:
        if "username" in session:
            username = session["username"]

            product_query = Market_Class.query.all()
            user_query = User_Class.query.filter_by(u_id=username).all()
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

            db.session.add(user)
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
            not request.form["price"]
            or not request.form["coin"]
        ):
            flash("Please enter all the fields", "error")
        else:
            username = session["username"]
            user = User_Class.query.filter_by(u_id=username).first()
            upload_coin = int(request.form["coin"])

            if upload_coin <= user.u_coin:
                coin = Market_Class(
                    request.form["price"],
                    request.form["coin"],
                    session["username"],
                )

                db.session.add(coin)

                user.u_coin -= upload_coin
                db.session.commit()
                return redirect(url_for("main"))
            else:
                flash("You don't have enough coins to upload", "error")
                return render_template("upload.html", username=session["username"])

    return render_template("upload.html", username=session["username"])


@app.route("/cancel_sale/<int:id>", methods=["POST"])
def cancel_sale(id):
    username = session["username"]
    canceled_coin = Market_Class.query.filter_by(id=id).first()
    if username == canceled_coin.m_seller:
        seller = User_Class.query.filter_by(u_id=username).first()
        seller.u_coin += canceled_coin.m_coin

        db.session.delete(canceled_coin)
        db.session.commit()

    return redirect(url_for("main"))


@app.route("/purchase/<int:id>/<m_seller>", methods=["GET", "POST"])
def purchase(id, m_seller):
    if request.method == "POST":
        return redirect(url_for("search", word=request.form["search"]))
    else:
        result = Market_Class.query.filter_by(id=id).first()

        seller = User_Class.query.filter_by(u_id=m_seller).first()

        if "username" in session:
            username = session["username"]
            buyer = User_Class.query.filter_by(u_id=session["username"]).first()

            if buyer.u_id != seller.u_id:
                if buyer.u_cash >= result.m_price * result.m_coin:
                    buyer.u_cash -= result.m_price * result.m_coin
                    seller.u_cash += result.m_price * result.m_coin
                    buyer.u_coin += result.m_coin

                    transaction_price = result.m_price
                    result = Market_Class.query.filter_by(
                        m_price=result.m_price
                    ).delete()
                    db.session.commit()

                    transaction = Transaction_Class(
                        price=transaction_price, timestamp=datetime.now()
                    )
                    db.session.add(transaction)
                    db.session.commit()

                    return redirect(url_for("main"))
            else:
                return redirect(url_for("main"))

        return render_template("purchase.html", result=result, username=username)


@app.route("/update_cash_input")
def update_cash_input():
    user = User_Class.query.filter_by(u_id=session["username"]).first()
    return render_template("money_update.html", current_cash=user.u_cash)


@app.route("/update_cash", methods=["POST"])
def update_cash():
    if request.form["amount"] == "":
        flash("금액이 입력되지 않았습니다.", "error")
        return redirect(url_for("update_cash_input"))
    else:
        amount = int(request.form["amount"])  # 입력된 금액 값 가져오기
        action = request.form["action"]  # 버튼의 액션 값 가져오기
        if action == "deposit":
            # Deposit 버튼을 클릭한 경우
            if "username" in session:
                user = User_Class.query.filter_by(u_id=session["username"]).first()
                current_cash = int(user.u_cash)
                current_cash += amount
                user.u_cash = current_cash
                db.session.commit()
                flash("금액이 성공적으로 입금되었습니다.", "success")
                return redirect(url_for("main"))
            else:
                flash("로그인이 필요합니다.", "error")
                return redirect(url_for("login"))

        elif action == "withdraw":
            # Withdraw 버튼을 클릭한 경우
            if "username" in session:
                user = User_Class.query.filter_by(u_id=session["username"]).first()
                current_cash = int(user.u_cash)
                if current_cash >= amount:
                    current_cash = int(user.u_cash)
                    current_cash -= amount
                    user.u_cash = current_cash
                    db.session.commit()
                    flash("금액이 성공적으로 출금되었습니다.", "success")
                    return redirect(url_for("main"))
                else:
                    flash("보유 금액보다 출금 금액이 더 많습니다.", "error")
                    return redirect(url_for("main"))
            else:
                flash("로그인이 필요합니다.", "error")
                return redirect(url_for("login"))


@app.route("/coin_price_history", methods=["GET"])
def coin_price_history():
    data = Transaction_Class.query.all()
    data_dicts = [transaction.to_dict() for transaction in data]
    return render_template("coin_price_history.html", data=data_dicts)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5050)
