from flask import Flask, render_template, request, redirect, url_for
import os
import datetime
import json

app = Flask(__name__)
DATA_FILE = "utilisateurs.json"
PRATIQUES_FILE = "pratiques.txt"
RECOMPENSES_FILE = "recompenses.txt"

def charger_utilisateurs():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def sauvegarder_utilisateurs(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def charger_pratique(jour):
    try:
        with open(PRATIQUES_FILE, "r", encoding="utf-8") as f:
            blocs = f.read().split("------")
        if jour <= len(blocs):
            sections = blocs[jour - 1].strip().split("---")
            titre = sections[0].strip() if len(sections) > 0 else "Sans titre"
            intro = sections[1].strip() if len(sections) > 1 else ""
            pratique = sections[2].strip() if len(sections) > 2 else ""
            return titre, intro, pratique
        else:
            return "Félicitations 🎉", "Tu as terminé toutes les pratiques !", ""
    except Exception as e:
        print(f"Erreur dans charger_pratique : {e}")
        return "Erreur", "Impossible de charger la pratique.", ""

def load_recompenses():
    recompenses = {}
    if os.path.exists(RECOMPENSES_FILE):
        with open(RECOMPENSES_FILE, encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split("||")
                if len(parts) == 3:
                    jour, texte, lien = parts
                    recompenses[int(jour)] = {"texte": texte, "lien": lien}
    return recompenses

recompenses = load_recompenses()

@app.route("/", methods=["GET", "POST"])
def accueil():
    if request.method == "POST":
        pseudo = request.form["pseudo"]
        data = charger_utilisateurs()
        if pseudo not in data:
            data[pseudo] = {"jour": 0, "last_date": None, "feedbacks": []}
            sauvegarder_utilisateurs(data)
        return redirect(url_for("pratique", pseudo=pseudo))
    return render_template("accueil.html")

@app.route("/pratique/<pseudo>", methods=["GET", "POST"])
def pratique(pseudo):
    data = charger_utilisateurs()
    if pseudo not in data:
        return redirect(url_for("accueil"))

    utilisateur = data[pseudo]
    today = datetime.date.today().isoformat()
    jour = utilisateur["jour"]

    titre, intro, contenu_pratique = charger_pratique(jour + 1)
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

    return render_template("pratique.html", jour=jour + 1, titre=titre, intro=intro, pratique=contenu_pratique, recompense=recompense, pseudo=pseudo)

if __name__ == "__main__":
    app.run(debug=True)
