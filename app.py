import os
from flask import Flask, render_template, request, redirect
from datetime import datetime


app = Flask(__name__)

# Charger les pratiques
with open("pratiques.txt", "r", encoding="utf-8") as f:
    pratiques = [p.strip() for p in f.readlines() if p.strip()]

# Lire ou initialiser le jour
def get_jour():
    if os.path.exists("jour_en_cours.txt"):
        with open("jour_en_cours.txt", "r") as f:
            return int(f.read().strip())
    else:
        return 1

# Sauver le jour suivant
def save_jour(jour):
    with open("jour_en_cours.txt", "w") as f:
        f.write(str(jour))

# Sauver le feedback
def save_feedback(jour, feedback):
    date = datetime.now().strftime("%Y-%m-%d")
    with open("feedbacks.txt", "a", encoding="utf-8") as f:
        f.write(f"{date} - Jour {jour} : {feedback}\n")

def get_last_access_date():
    if os.path.exists("dernier_acces.txt"):
        with open("dernier_acces.txt", "r") as f:
            return f.read().strip()
    return None

def set_last_access_date(date_str):
    with open("dernier_acces.txt", "w") as f:
        f.write(date_str)


@app.route("/", methods=["GET", "POST"])
def index():
    aujourd_hui = datetime.now().strftime("%Y-%m-%d")
    dernier_acces = get_last_access_date()
    jour = get_jour()

    # Si on est encore le même jour, ne pas avancer
    if dernier_acces == aujourd_hui:
        pratique = pratiques[jour - 1] if jour <= len(pratiques) else "Toutes les pratiques ont été faites 🌟"
        deja_fait = True
    else:
        pratique = pratiques[jour - 1] if jour <= len(pratiques) else "Toutes les pratiques ont été faites 🌟"
        deja_fait = False

    if request.method == "POST" and not deja_fait:
        feedback = request.form.get("feedback")
        if feedback:
            save_feedback(jour, feedback)
            save_jour(jour + 1)
            set_last_access_date(aujourd_hui)
        return redirect("/")

    return render_template("index.html", jour=jour, pratique=pratique, deja_fait=deja_fait)

if __name__ == '__main__':
    app.run(debug=True)
