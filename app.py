from flask import Flask, render_template, request, redirect, url_for
import os
import datetime
import json

app = Flask(__name__)
DATA_FILE = "utilisateurs.json"

def charger_utilisateurs():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def sauvegarder_utilisateurs(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_pratiques():
    pratiques = []
    with open("pratiques_autocompassion_par_niveaux.txt", encoding="utf-8") as f:
        for line in f:
            if "||" in line:
                intro, pratique = line.strip().split("||")
                pratiques.append((intro.replace("\\n", "\n"), pratique))
    return pratiques

def load_recompenses():
    recompenses = {}
    if os.path.exists("recompenses.txt"):
        with open("recompenses.txt", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split("||")
                if len(parts) == 3:
                    jour, texte, lien = parts
                    recompenses[int(jour)] = {"texte": texte, "lien": lien}
    return recompenses

pratiques = load_pratiques()
recompenses = load_recompenses()

@app.route('/', methods=['GET', 'POST'])
def accueil():
    if request.method == 'POST':
        username = request.form['username']
        already_visited = request.form.get('already_visited') == 'yes'
        current_day = int(request.form.get('current_day', 1)) if already_visited else 1

        # Enregistre le nouvel utilisateur avec ce jour
        save_user_data(username, current_day)

        return redirect(url_for('pratique', username=username))
    return render_template('accueil.html')

@app.route("/pratique/<pseudo>", methods=["GET", "POST"])
def pratique(pseudo):
    data = charger_utilisateurs()
    if pseudo not in data:
        return redirect(url_for("accueil"))
    utilisateur = data[pseudo]
    today = datetime.date.today().isoformat()

    jour = utilisateur["jour"]
    intro, pratique = pratiques[min(jour, len(pratiques)-1)]
    recompense = recompenses.get(jour + 1, None)

    if request.method == "POST":
        feedback = request.form.get("feedback", "").strip()
        if feedback:
            utilisateur["feedbacks"].append((today, feedback))
        if utilisateur["last_date"] != today:
            utilisateur["jour"] += 1
            utilisateur["last_date"] = today
        data[pseudo] = utilisateur
        sauvegarder_utilisateurs(data)
        return redirect(url_for("pratique", pseudo=pseudo))

    return render_template("pratique.html", jour=jour+1, intro=intro, pratique=pratique, recompense=recompense)
