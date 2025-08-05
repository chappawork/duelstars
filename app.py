from flask import Flask, render_template, request, redirect, url_for
import random
import os

app = Flask(__name__)

lobby = []
games = {}

choices = ["rock", "paper", "scissors"]
choice_names = {
    "rock": "🪨 Камень",
    "paper": "📄 Бумага",
    "scissors": "✂️ Ножницы"
}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        player_id = request.form["player_id"]
        if player_id not in lobby:
            lobby.append(player_id)
        if len(lobby) >= 2:
            p1 = lobby.pop(0)
            p2 = lobby.pop(0)
            game_id = f"{p1}_{p2}"
            games[game_id] = {
                "players": {p1: None, p2: None}
            }
            return redirect(url_for("game", game_id=game_id, player_id=player_id))
        else:
            return render_template("index.html", waiting=True, player_id=player_id)
    return render_template("index.html")

@app.route("/game/<game_id>/<player_id>", methods=["GET", "POST"])
def game(game_id, player_id):
    game = games.get(game_id)
    if not game or player_id not in game["players"]:
        return "Ошибка: игра не найдена", 404

    if request.method == "POST":
        choice = request.form["choice"]
        game["players"][player_id] = choice

    p1, p2 = game["players"].keys()
    c1 = game["players"][p1]
    c2 = game["players"][p2]

    if c1 and c2:
        return redirect(url_for("result", game_id=game_id, player_id=player_id))

    return render_template("game.html", game_id=game_id, player_id=player_id)

@app.route("/result/<game_id>/<player_id>")
def result(game_id, player_id):
    game = games.get(game_id)
    if not game or player_id not in game["players"]:
        return "Ошибка: игра не найдена", 404

    p1, p2 = list(game["players"].keys())
    c1 = game["players"][p1]
    c2 = game["players"][p2]

    def winner(c1, c2):
        if c1 == c2:
            return "draw"
        elif (c1 == "rock" and c2 == "scissors") or \
             (c1 == "paper" and c2 == "rock") or \
             (c1 == "scissors" and c2 == "paper"):
            return "p1"
        else:
            return "p2"

    result = winner(c1, c2)
    if result == "draw":
        winner_text = "🤝 Ничья!"
    elif (result == "p1" and player_id == p1) or (result == "p2" and player_id == p2):
        winner_text = "🎉 Вы победили!"
    else:
        winner_text = "😢 Вы проиграли."

    return render_template("result.html",
                           your_choice=choice_names[game["players"][player_id]],
                           opponent_choice=choice_names[game["players"][p2 if player_id == p1 else p1]],
                           result_text=winner_text)

# 🛠️ Важно: именно это нужно для работы на Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

