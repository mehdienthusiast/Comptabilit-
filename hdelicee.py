import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk  # Pour gérer les images des logos

# Initialisation des variables globales
recette_jour = 0
recette_semaine = 0
recette_mois = 0
depense_jour = 0
depense_semaine = 0
depense_mois = 0

# Connexion à la base de données
conn = sqlite3.connect('hdelice.db')
c = conn.cursor()

# Création des tables si elles n'existent pas
c.execute('''CREATE TABLE IF NOT EXISTS recettes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE,
    montant REAL
)''')

c.execute('''CREATE TABLE IF NOT EXISTS depenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE,
    montant REAL
)''')

c.execute('''CREATE TABLE IF NOT EXISTS employes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT,
    horaire TEXT
)''')

conn.commit()
conn.close()

# Fonction pour initialiser les variables globales à partir de la base de données
def initialiser_variables():
    global recette_jour, recette_semaine, recette_mois, depense_jour, depense_semaine, depense_mois
    today = datetime.date.today()
    start_of_week = today - datetime.timedelta(days=today.weekday())
    start_of_month = today.replace(day=1)

    # Calculer les recettes
    conn = sqlite3.connect('hdelice.db')
    c = conn.cursor()
    c.execute("SELECT SUM(montant) FROM recettes WHERE date = ?", (today,))
    recette_jour = c.fetchone()[0] or 0
    c.execute("SELECT SUM(montant) FROM recettes WHERE date >= ?", (start_of_week,))
    recette_semaine = c.fetchone()[0] or 0
    c.execute("SELECT SUM(montant) FROM recettes WHERE date >= ?", (start_of_month,))
    recette_mois = c.fetchone()[0] or 0

    # Calculer les dépenses
    c.execute("SELECT SUM(montant) FROM depenses WHERE date = ?", (today,))
    depense_jour = c.fetchone()[0] or 0
    c.execute("SELECT SUM(montant) FROM depenses WHERE date >= ?", (start_of_week,))
    depense_semaine = c.fetchone()[0] or 0
    c.execute("SELECT SUM(montant) FROM depenses WHERE date >= ?", (start_of_month,))
    depense_mois = c.fetchone()[0] or 0

    conn.close()

# Fonction de mise à jour de l'affichage
def update_display():
    global recette_jour, recette_semaine, recette_mois, depense_jour, depense_semaine, depense_mois
    # Mise à jour des labels
    recette_du_jour_label.config(text=f"Recette du jour: {recette_jour:.2f} €")
    recette_semaine_label.config(text=f"Recette de la semaine: {recette_semaine:.2f} €")
    recette_mois_label.config(text=f"Recette du mois: {recette_mois:.2f} €")
    depense_du_jour_label.config(text=f"Dépense du jour: {depense_jour:.2f} €")
    depense_semaine_label.config(text=f"Dépense de la semaine: {depense_semaine:.2f} €")
    depense_mois_label.config(text=f"Dépense du mois: {depense_mois:.2f} €")
    # Calcul du bénéfice net
    benefice_net = recette_jour - depense_jour
    benefice_net_label.config(text=f"Bénéfice net: {benefice_net:.2f} €")
    # Mise à jour de la date du jour
    today = datetime.date.today()
    date_label.config(text=f"Date du jour: {today}")
    # Mise à jour du graphique
    update_graph()

# Fonction pour ajouter une recette
def ajouter_recette():
    global recette_jour, recette_semaine, recette_mois
    try:
        montant = float(recette_entry.get())  # Essayer de convertir l'entrée en float
        today = datetime.date.today()
        conn = sqlite3.connect('hdelice.db')
        c = conn.cursor()
        c.execute("INSERT INTO recettes (date, montant) VALUES (?, ?)", (today, montant))
        conn.commit()
        conn.close()
        recette_jour += montant
        recette_semaine += montant
        recette_mois += montant
        update_display()
    except ValueError:
        messagebox.showerror("Erreur", "Veuillez entrer un montant valide.")

# Fonction pour ajouter une dépense
def ajouter_depense():
    global depense_jour, depense_semaine, depense_mois
    try:
        montant = float(depense_entry.get())  # Essayer de convertir l'entrée en float
        today = datetime.date.today()
        conn = sqlite3.connect('hdelice.db')
        c = conn.cursor()
        c.execute("INSERT INTO depenses (date, montant) VALUES (?, ?)", (today, montant))
        conn.commit()
        conn.close()
        depense_jour += montant
        depense_semaine += montant
        depense_mois += montant
        update_display()
    except ValueError:
        messagebox.showerror("Erreur", "Veuillez entrer un montant valide.")

# Fonction pour réinitialiser la base de données
def reset_db():
    try:
        conn = sqlite3.connect('hdelice.db')
        c = conn.cursor()
        c.execute("DELETE FROM recettes")
        c.execute("DELETE FROM depenses")
        c.execute("DELETE FROM employes")  # Réinitialiser aussi la table des employés
        conn.commit()
        conn.close()
        messagebox.showinfo("Réinitialisation", "La base de données a été réinitialisée avec succès.")
        # Réinitialisation des variables globales
        global recette_jour, recette_semaine, recette_mois, depense_jour, depense_semaine, depense_mois
        recette_jour = 0
        recette_semaine = 0
        recette_mois = 0
        depense_jour = 0
        depense_semaine = 0
        depense_mois = 0
        # Mise à jour de l'affichage
        update_display()
    except sqlite3.Error as e:
        messagebox.showerror("Erreur", f"Erreur lors de la réinitialisation de la base de données: {e}")

# Fonction pour afficher le graphique
def update_graph():
    # Création du graphique
    fig, ax = plt.subplots(figsize=(4, 3))  # Taille réduite du graphique
    ax.bar(['Recette', 'Dépense'], [recette_mois, depense_mois], color=['green', 'red'])
    ax.set_title('Bénéfice net du mois en cours')
    ax.set_ylabel('Montant (€)')
    ax.set_ylim(0, max(recette_mois, depense_mois) * 1.2)
    # Ajout du montant à gauche
    ax.text(0, recette_mois + 10, f"{recette_mois:.2f} €", ha='center', va='bottom', fontsize=10, color='green')
    ax.text(1, depense_mois + 10, f"{depense_mois:.2f} €", ha='center', va='bottom', fontsize=10, color='red')
    # Ajout de la date en bas du graphique
    today = datetime.date.today()
    ax.text(0.5, -0.15, f"Date: {today}", ha='center', va='top', transform=ax.transAxes, fontsize=8)
    # Affichage dans l'interface tkinter
    for widget in graph_frame.winfo_children():
        widget.destroy()
    canvas = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

# Fonction pour enregistrer les horaires des employés
def enregistrer_horaires():
    try:
        conn = sqlite3.connect('hdelice.db')
        c = conn.cursor()
        # Supprimer les anciens horaires
        c.execute("DELETE FROM employes")
        # Enregistrer les nouveaux horaires
        for employe, horaire in employes_horaires.items():
            c.execute("INSERT INTO employes (nom, horaire) VALUES (?, ?)", (employe, horaire.get()))
        conn.commit()
        conn.close()
        messagebox.showinfo("Succès", "Les horaires ont été enregistrés avec succès.")
    except sqlite3.Error as e:
        messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement des horaires: {e}")

# Fonction pour charger les horaires des employés
def charger_horaires():
    try:
        conn = sqlite3.connect('hdelice.db')
        c = conn.cursor()
        # Charger les horaires depuis la base de données
        c.execute("SELECT nom, horaire FROM employes")
        rows = c.fetchall()
        for row in rows:
            nom, horaire = row
            if nom in employes_horaires:
                employes_horaires[nom].delete(0, tk.END)  # Effacer la valeur actuelle
                employes_horaires[nom].insert(0, horaire)  # Insérer la nouvelle valeur
        conn.close()
    except sqlite3.Error as e:
        messagebox.showerror("Erreur", f"Erreur lors du chargement des horaires: {e}")

# Fonction pour calculer le salaire
def calculer_salaire():
    try:
        taux_horaire = float(taux_horaire_entry.get())
        heures_travaillees = float(heures_travaillees_entry.get())
        heures_sup = float(heures_sup_entry.get())
        
        # Assuming regular hours are paid at the regular rate and overtime is paid at 1.5 times the regular rate
        salaire_total = (taux_horaire * heures_travaillees) + (1.5 * taux_horaire * heures_sup)
        
        salaire_label.config(text=f"Salaire total: {salaire_total:.2f} €")
    except ValueError:
        messagebox.showerror("Erreur", "Veuillez entrer des valeurs numériques valides.")

# Initialisation de la fenêtre Tkinter
root = tk.Tk()
root.title("Gestion H'Delice")
root.geometry("1920x1080")  # Résolution 1920x1080
root.configure(bg="#f0f0f0")

# Ajout du label "Crée par Mehdi pour H'Délice" en haut au milieu
credits_label = tk.Label(root, text="Crée par Mehdi pour H'Délice", bg="#f0f0f0", font=("Arial", 14))
credits_label.place(relx=0.5, rely=0.02, anchor=tk.CENTER)

# Chargement des logos
try:
    logo1_image = Image.open("logo1.png")
    logo1_image = logo1_image.resize((150, 150), Image.Resampling.LANCZOS)
    logo1_photo = ImageTk.PhotoImage(logo1_image)
except FileNotFoundError:
    logo1_photo = None

try:
    logo2_image = Image.open("logo2.png")
    logo2_image = logo2_image.resize((150, 150), Image.Resampling.LANCZOS)
    logo2_photo = ImageTk.PhotoImage(logo2_image)
except FileNotFoundError:
    logo2_photo = None

try:
    logo3_image = Image.open("logo3.png")
    logo3_image = logo3_image.resize((150, 150), Image.Resampling.LANCZOS)
    logo3_photo = ImageTk.PhotoImage(logo3_image)
except FileNotFoundError:
    logo3_photo = None

# Création d'un cadre pour les logos à gauche
logos_frame = tk.Frame(root, bg="#f0f0f0")
logos_frame.pack(side=tk.LEFT, padx=20, pady=20, fill="y")

# Ajout des logos
if logo1_photo:
    logo1_label = tk.Label(logos_frame, image=logo1_photo, bg="#f0f0f0")
    logo1_label.pack(pady=10)

if logo2_photo:
    logo2_label = tk.Label(logos_frame, image=logo2_photo, bg="#f0f0f0")
    logo2_label.pack(pady=10)

if logo3_photo:
    logo3_label = tk.Label(logos_frame, image=logo3_photo, bg="#f0f0f0")
    logo3_label.pack(pady=10)

# Création d'un cadre pour le logo principal et la date
header_frame = tk.Frame(root, bg="#f0f0f0")
header_frame.pack(pady=10, fill="x")

# Ajout du logo principal
try:
    logo_image = Image.open("logo_hdelice.png")
    logo_image = logo_image.resize((150, 150), Image.Resampling.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_image)
except FileNotFoundError:
    logo_photo = None

if logo_photo:
    logo_label = tk.Label(header_frame, image=logo_photo, bg="#f0f0f0")
    logo_label.grid(row=0, column=0, padx=10, pady=10)
else:
    logo_label = tk.Label(header_frame, text="Logo non trouvé", bg="#f0f0f0", font=("Arial", 14))
    logo_label.grid(row=0, column=0, padx=10, pady=10)

# Ajout de la date du jour
today = datetime.date.today()
date_label = tk.Label(header_frame, text=f"Date du jour: {today}", bg="#f0f0f0", font=("Arial", 14))
date_label.grid(row=0, column=1, padx=10, pady=10)

# Bouton pour réinitialiser la base de données
reset_button = tk.Button(header_frame, text="Réinitialiser", font=("Arial", 14), command=reset_db, bg="#FF6347", fg="white")
reset_button.grid(row=0, column=2, padx=10, pady=10)

# Création des cadres pour chaque fonctionnalité
main_frame = tk.Frame(root, bg="#f0f0f0")
main_frame.pack(pady=20, padx=20, fill="both", expand=True)

# Section bas : Calcul du salaire
salaire_frame = tk.Frame(main_frame, bg="#f0f0f0")
salaire_frame.grid(row=0, column=0, columnspan=2, pady=20)

taux_horaire_label = tk.Label(salaire_frame, text="Taux horaire (€):", bg="#f0f0f0", font=("Arial", 14))
taux_horaire_label.grid(row=0, column=0, pady=10)

taux_horaire_entry = tk.Entry(salaire_frame, font=("Arial", 14))
taux_horaire_entry.grid(row=0, column=1, pady=10)

heures_travaillees_label = tk.Label(salaire_frame, text="Nombre d'heures travaillées:", bg="#f0f0f0", font=("Arial", 14))
heures_travaillees_label.grid(row=1, column=0, pady=10)

heures_travaillees_entry = tk.Entry(salaire_frame, font=("Arial", 14))
heures_travaillees_entry.grid(row=1, column=1, pady=10)

heures_sup_label = tk.Label(salaire_frame, text="Heures supplémentaires:", bg="#f0f0f0", font=("Arial", 14))
heures_sup_label.grid(row=2, column=0, pady=10)

heures_sup_entry = tk.Entry(salaire_frame, font=("Arial", 14))
heures_sup_entry.grid(row=2, column=1, pady=10)

salaire_label = tk.Label(salaire_frame, text="Salaire total: 0 €", bg="#f0f0f0", font=("Arial", 14))
salaire_label.grid(row=3, column=0, columnspan=2, pady=10)

calculer_salaire_button = tk.Button(salaire_frame, text="Calculer Salaire", font=("Arial", 14), command=calculer_salaire, bg="#32CD32", fg="white")
calculer_salaire_button.grid(row=4, column=0, columnspan=2, pady=10)

# Section gauche : Recettes
left_frame = tk.Frame(main_frame, bg="#f0f0f0")
left_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nw")

recette_du_jour_label = tk.Label(left_frame, text="Recette du jour: 0 €", bg="#87CEEB", font=("Arial", 14))
recette_du_jour_label.grid(row=0, column=0, pady=10)

recette_semaine_label = tk.Label(left_frame, text="Recette de la semaine: 0 €", bg="#87CEEB", font=("Arial", 14))
recette_semaine_label.grid(row=1, column=0, pady=10)

recette_mois_label = tk.Label(left_frame, text="Recette du mois: 0 €", bg="#87CEEB", font=("Arial", 14))
recette_mois_label.grid(row=2, column=0, pady=10)

recette_entry = tk.Entry(left_frame, font=("Arial", 14))
recette_entry.grid(row=3, column=0, pady=10)

ajouter_recette_button = tk.Button(left_frame, text="Ajouter Recette", font=("Arial", 14), command=ajouter_recette, bg="#32CD32", fg="white")
ajouter_recette_button.grid(row=4, column=0, pady=10)

# Section droite : Dépenses et Graphique
right_frame = tk.Frame(main_frame, bg="#f0f0f0")
right_frame.grid(row=1, column=1, padx=20, pady=20, sticky="ne")

depense_du_jour_label = tk.Label(right_frame, text="Dépense du jour: 0 €", bg="#FF6347", font=("Arial", 14))
depense_du_jour_label.grid(row=0, column=0, pady=10)

depense_semaine_label = tk.Label(right_frame, text="Dépense de la semaine: 0 €", bg="#FF6347", font=("Arial", 14))
depense_semaine_label.grid(row=1, column=0, pady=10)

depense_mois_label = tk.Label(right_frame, text="Dépense du mois: 0 €", bg="#FF6347", font=("Arial", 14))
depense_mois_label.grid(row=2, column=0, pady=10)

depense_entry = tk.Entry(right_frame, font=("Arial", 14))
depense_entry.grid(row=3, column=0, pady=10)

ajouter_depense_button = tk.Button(right_frame, text="Ajouter Dépense", font=("Arial", 14), command=ajouter_depense, bg="#DC143C", fg="white")
ajouter_depense_button.grid(row=4, column=0, pady=10)

# Bénéfice net
benefice_net_label = tk.Label(right_frame, text="Bénéfice net: 0 €", bg="#87CEEB", font=("Arial", 14))
benefice_net_label.grid(row=5, column=0, pady=10)

# Graphique pour le bénéfice net
graph_frame = tk.Frame(right_frame, bg="#f0f0f0")
graph_frame.grid(row=0, column=1, rowspan=6, padx=20, pady=20, sticky="nsew")

# Section pour la gestion des employés
employes_frame = tk.Frame(main_frame, bg="#f0f0f0")
employes_frame.grid(row=1, column=2, padx=20, pady=20, sticky="ne")

# Liste des employés
employes = ["Mehdi", "Rani", "Nabil", "Islem", "Ilyes", "Chawki", "Alternant 3"]
employes_horaires = {}

# Création des champs pour les horaires des employés
for i, employe in enumerate(employes):
    label = tk.Label(employes_frame, text=f"{employe}:", bg="#f0f0f0", font=("Arial", 14))
    label.grid(row=i, column=0, pady=5, sticky="w")
    horaire_entry = tk.Entry(employes_frame, font=("Arial", 14))
    horaire_entry.grid(row=i, column=1, pady=5)
    employes_horaires[employe] = horaire_entry

# Bouton pour enregistrer les horaires
enregistrer_horaires_button = tk.Button(employes_frame, text="Enregistrer Horaires", font=("Arial", 14), command=enregistrer_horaires, bg="#4CAF50", fg="white")
enregistrer_horaires_button.grid(row=len(employes), column=0, columnspan=2, pady=10)

# Initialiser les variables globales
initialiser_variables()

# Charger les horaires au démarrage
charger_horaires()

# Mise à jour de l'affichage initial
update_display()

# Lancement de la fenêtre
root.mainloop()