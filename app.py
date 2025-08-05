from flask import Flask, render_template, request, redirect, url_for, session
import random
import uuid

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Хранилище активных игр
games = {}

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
    if request.method == "POST":
        player_id = request.form.get("player_id")
        if not player_id:
            return "❌ Не передан player_id", 400

        # Создаём новую игру или присоединяемся к существующей
        for game_id, game in games.items():
            if len(game["players"]) < 2:
                game["players"].append(player_id)
                session["game_id"] = game_id
                session["player_id"] = player_id
                return redirect(url_for("game"))

        # Создать новую игру
        game_id = str(uuid.uuid4())
        games[game_id] = {
            "players": [player_id],
            "moves": {}
        }
        session["game_id"] = game_id
        session["player_id"] = player_id
        return redirect(url_for("game"))

    return render_template("index.html")

@app.route("/game", methods=["GET", "POST"])
def game():
    game_id = session.get("game_id")
    player_id = session.get("player_id")

    if not game_id or not player_id or game_id not in games:
        return redirect(url_for("index"))

    game = games[game_id]

    if request.method == "POST":
        move = request.form.get("move")
        if move not in CHOICES:
            return "❌ Неверный ход", 400
        game["moves"][player_id] = move

        # Если оба игрока сходили — показываем результат
        if len(game["moves"]) == 2:
            return redirect(url_for("result"))

    opponent_connected = len(game["players"]) == 2
    already_moved = player_id in game["moves"]
    return render_template("game.html", choices=CHOICES, opponent_connected=opponent_connected, already_moved=already_moved)

@app.route("/result")
def result():
    game_id = session.get("game_id")
    player_id = session.get("player_id")

    if not game_id or not player_id or game_id not in games:
        return redirect(url_for("index"))

    game = games[game_id]
    if len(game["players"]) < 2 or len(game["moves"]) < 2:
        return redirect(url_for("game"))

    p1, p2 = game["players"]
    move1 = game["moves"][p1]
    move2 = game["moves"][p2]
    winner = determine_winner(move1, move2)

    if winner == 0:
        result_text = "🤝 Ничья!"
    elif (winner == 1 and player_id == p1) or (winner == 2 and player_id == p2):
        result_text = "🏆 Вы победили!"
    else:
        result_text = "💀 Вы проиграли."

    # Очистить игру
    del games[game_id]

    return render_template("result.html", result=result_text, move1=CHOICES[move1], move2=CHOICES[move2])

if __name__ == "__main__":
    app.run(debug=True)

