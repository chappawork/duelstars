from flask import Flask, render_template, request, redirect, url_for
import random
import os

app = Flask(__name__)

players = {}
waiting_player = None

CHOICES = {
    "rock": "🪨 Камень",
    "paper": "📄 Бумага",
    "scissors": "✂️ Ножницы"
}

def determine_winner(choice1, choice2):
    if choice1 == choice2:
        return 0
    wins = {
        "rock": "scissors",
        "scissors": "paper",
        "paper": "rock"
    }
    return 1 if wins[choice1] == choice2 else 2

@app.route("/", methods=["GET", "POST"])
def index():
    global waiting_player

    if request.method == "POST":
        user_id = request.form["user_id"]

        if not waiting_player:
            waiting_player = user_id
            players[user_id] = {"opponent": None, "choice": None}
            return render_template("game.html", user_id=user_id, status="waiting")

        opponent_id = waiting_player
        if opponent_id == user_id:
            return render_template("index.html", error="Подождите другого игрока.")

        players[user_id] = {"opponent": opponent_id, "choice": None}
        players[opponent_id]["opponent"] = user_id
        waiting_player = None

        return render_template("game.html", user_id=user_id, status="ready")

    return render_template("index.html")

@app.route("/play", methods=["POST"])
def play():
    user_id = request.form["user_id"]
    choice = request.form["choice"]

    players[user_id]["choice"] = choice
    opponent_id = players[user_id]["opponent"]

    if not players[opponent_id]["choice"]:
        return render_template("game.html", user_id=user_id, status="waiting_choice")

    user_choice = players[user_id]["choice"]
    opponent_choice = players[opponent_id]["choice"]

    result = determine_winner(user_choice, opponent_choice)
    result_text = ""

    if result == 0:
        result_text = "🤝 Ничья!"
    elif (result == 1 and players[user_id]["opponent"] == opponent_id) or (result == 2 and players[user_id]["opponent"] != opponent_id):
        result_text = "🏆 Вы победили!"
    else:
        result_text = "💥 Вы проиграли!"

    choice_text = f"""
    <b>Ваш выбор:</b> {CHOICES[user_choice]}<br>
    <b>Выбор соперника:</b> {CHOICES[opponent_choice]}<br><br>
    <b>{result_text}</b>
    """

    del players[user_id]
    del players[opponent_id]

    return render_template("result.html", result=choice_text)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
