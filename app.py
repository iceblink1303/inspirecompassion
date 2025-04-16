from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "ta_cle_secrete"

def lire_ligne_fichier(nom_fichier, index):
    try:
        with open(nom_fichier, 'r', encoding='utf-8') as f:
            lignes = f.readlines()
            if 0 <= index < len(lignes):
                return lignes[index].strip()
    except Exception as e:
        print(f"Erreur lecture fichier {nom_fichier} : {e}")
    return "Contenu non disponible."

def lire_recompense(jour):
    try:
        with open('recompenses.txt', 'r', encoding='utf-8') as f:
            for ligne in f:
                if ligne.startswith(f"{jour}||"):
                    return ligne.strip().split("||", 1)[1]
    except:
        pass
    return None

@app.route('/', methods=['GET', 'POST'])
def accueil():
    if request.method == 'POST':
        session['surnom'] = request.form['surnom']
        session['deja_venu'] = request.form.get('deja_venu', 'non')
        session['jour_arret'] = int(request.form.get('jour_arret') or 1)
        return redirect(url_for('pratique'))
    return render_template('accueil.html')

@app.route('/pratique', methods=['GET', 'POST'])
def pratique():
    surnom = session.get('surnom', 'ami')
    jour = session.get('jour_arret', 1)

    texte = lire_ligne_fichier('textes.txt', jour - 1)
    pratique = lire_ligne_fichier('pratiques.txt', jour - 1)
    recompense = lire_recompense(jour)

    if request.method == 'POST':
        feedback = request.form.get('feedback', '').strip()
        if feedback:
            with open('feedback.txt', 'a', encoding='utf-8') as f:
                f.write(f"{datetime.now()} | {surnom} | Jour {jour} | {feedback}\n")
        session['jour_arret'] = jour + 1
        return redirect(url_for('pratique'))

    return render_template('pratique.html', jour=jour, texte=texte, pratique=pratique, recompense=recompense)

@app.route('/voir-feedbacks')
def voir_feedbacks():
    try:
        with open('feedback.txt', 'r', encoding='utf-8') as f:
            lignes = f.readlines()
        return "<br>".join(lignes)
    except Exception as e:
        return f"Erreur : {e}"

if __name__ == '__main__':
    app.run(debug=True)
