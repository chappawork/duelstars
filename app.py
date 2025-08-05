from flask import Flask, render_template, request, redirect, url_for
import random

app = Flask(__name__)

CHOICES = ["rock", "paper", "scissors"]
games = {}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        player_id = request.form["player_id"]
        if "join" in request.form:
            for gid, players in games.items():
                if len(players) == 1:
                    players[player_id] = None
                    return redirect(url_for("game", game_id=gid, player_id=player_id))
            gid = str(random.randint(1000, 9999))
            games[gid] = {player_id: None}
            return redirect(url_for("game", game_id=gid, player_id=player_id))
    return render_template("index.html")

@app.route("/game/<game_id>/<player_id>", methods=["GET", "POST"])
def game(game_id, player_id):
    if game_id not in games or player_id not in games[game_id]:
        return "Invalid game or player."

    if request.method == "POST":
        choice = request.form["choice"]
        games[game_id][player_id] = choice

    players = list(games[game_id].keys())
    choices = list(games[game_id].values())

    if len(players) == 2 and all(c is not None for c in choices):
        p1, p2 = players
        c1, c2 = choices
        result = determine_winner(c1, c2)
        outcome = {
            "tie": "🤝 Ничья!",
            "p1": f"🏆 Победил {p1}!",
            "p2": f"🏆 Победил {p2}!"
        }[result]
        game_result = {
            "p1": c1, "p2": c2, "outcome": outcome
        }
        del games[game_id]
        return render_template("result.html", result=game_result, p1=p1, p2=p2)

    return render_template("game.html", player_id=player_id, game_id=game_id, players=games[game_id])

def determine_winner(c1, c2):
    if c1 == c2:
        return "tie"
    wins = {"rock": "scissors", "scissors": "paper", "paper": "rock"}
    return "p1" if wins[c1] == c2 else "p2"

if __name__ == "__main__":
    app.run(debug=True)