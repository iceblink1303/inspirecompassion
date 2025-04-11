from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import os
import json

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "votre_cle_secrete_a_changer")

# Charger les pratiques depuis un fichier texte
with open("pratiques_autocompassion_par_niveaux.txt", "r", encoding="utf-8") as f:
    pratiques = [ligne.strip() for ligne in f.readlines() if ligne.strip()]

# Fichier JSON pour enregistrer les utilisateurs
UTILISATEURS_FILE = "utilisateurs.json"

# Charger ou initialiser les utilisateurs
if os.path.exists(UTILISATEURS_FILE):
    with open(UTILISATEURS_FILE, "r", encoding="utf-8") as f:
        utilisateurs = json.load(f)
else:
    utilisateurs = {}

def sauvegarder_utilisateurs():
    with open(UTILISATEURS_FILE, "w", encoding="utf-8") as f:
        json.dump(utilisateurs, f, indent=2, ensure_ascii=False)

@app.route("/", methods=["GET", "POST"])
def accueil():
    if request.method == "POST":
        surnom = request.form.get("username", "").strip().lower()
        est_revenu = request.form.get("visited") == "oui"
        jour_saisi = request.form.get("last_day")

        if surnom:
            if surnom not in utilisateurs:
                utilisateurs[surnom] = {
                    "dernier_jour": int(jour_saisi) if jour_saisi else 1,
                    "feedbacks": {}
                }
            else:
                if jour_saisi:
                    utilisateurs[surnom]["dernier_jour"] = int(jour_saisi)

            sauvegarder_utilisateurs()
            session["surnom"] = surnom
            return redirect(url_for("pratique"))

    return render_template("accueil.html")

@app.route("/pratique", methods=["GET", "POST"])
def pratique():
    surnom = session.get("surnom")
    if not surnom or surnom not in utilisateurs:
        return redirect(url_for("accueil"))

    utilisateur = utilisateurs[surnom]
    jour = utilisateur["dernier_jour"]
    pratique_du_jour = pratiques[jour - 1] if jour <= len(pratiques) else "Tu as complété toutes les pratiques !"

    if request.method == "POST":
        feedback = request.form.get("feedback", "").strip()
        horodatage = datetime.now().strftime("%Y-%m-%d %H:%M")
        if feedback:
            utilisateur["feedbacks"].setdefault(str(jour), []).append({
                "texte": feedback,
                "date": horodatage
            })
            sauvegarder_utilisateurs()
            utilisateur["dernier_jour"] = jour + 1 if jour < len(pratiques) else jour
            return redirect(url_for("pratique"))

    gamification = (jour == 7)
    feedbacks = utilisateur["feedbacks"].get(str(jour), [])

    return render_template("pratique.html", day=jour, practice=pratique_du_jour, gamification=gamification, feedbacks=feedbacks)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
