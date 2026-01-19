import json
import random
import time
import os
from datetime import datetime
from faker import Faker

fake = Faker('fr_FR')

# Créer le répertoire de destination s'il n'existe pas
output_dir = "./data/sources/boutique_physique"
os.makedirs(output_dir, exist_ok=True)

# Liste de produits possibles
produits = [
    {"nom": "Laptop Dell XPS", "prix": 1200.00},
    {"nom": "iPhone 15 Pro", "prix": 1100.00},
    {"nom": "Samsung Galaxy S24", "prix": 950.00},
    {"nom": "iPad Air", "prix": 650.00},
    {"nom": "Écouteurs Sony WH-1000XM5", "prix": 350.00},
    {"nom": "Montre Apple Watch Series 9", "prix": 450.00},
    {"nom": "Clavier Mécanique Logitech", "prix": 120.00},
    {"nom": "Souris Gaming Razer", "prix": 80.00},
    {"nom": "Webcam Logitech 4K", "prix": 150.00},
    {"nom": "Disque dur externe 2TB", "prix": 85.00},
    {"nom": "Chargeur sans fil", "prix": 35.00},
    {"nom": "Câble USB-C", "prix": 15.00},
    {"nom": "Adaptateur HDMI", "prix": 25.00},
    {"nom": "Support laptop", "prix": 40.00},
    {"nom": "Sac à dos ordinateur", "prix": 60.00}
]

statuts = ["confirmée", "confirmée", "confirmée", "confirmée", "annulée"]  # 80% confirmée

# Boutiques possibles
boutiques = [
    "Khouribga Centre",
    "Khouribga Mall",
    "Casablanca Marina",
    "Rabat Agdal",
    "Marrakech Gueliz"
]

compteur = 0

print(f"🏪 Démarrage du simulateur BOUTIQUE PHYSIQUE...")
print(f"📁 Répertoire de sortie: {output_dir}")
print(f"⏱️  Génération d'une commande toutes les 2-5 secondes\n")

try:
    while compteur < 500:
        # Générer une commande
        nb_produits = random.randint(1, 4)
        produits_commande = []
        total = 0

        for _ in range(nb_produits):
            produit = random.choice(produits)
            quantite = random.randint(1, 3)
            prix_total = produit["prix"] * quantite
            total += prix_total

            produits_commande.append({
                "nom_produit": produit["nom"],
                "quantite": quantite,
                "prix_unitaire": produit["prix"],
                "prix_total": round(prix_total, 2)
            })

        commande = {
            "id_commande": f"BOU-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}",
            "canal": "boutique_physique",
            "date_commande": datetime.now().isoformat(),
            "client": {
                "nom": fake.name(),
                "email": fake.email() if random.random() > 0.3 else None,  # 70% ont un email
                "telephone": fake.phone_number() if random.random() > 0.2 else None  # 80% ont un téléphone
            },
            "boutique": random.choice(boutiques),
            "produits": produits_commande,
            "montant_total": round(total, 2),
            "statut": random.choice(statuts),
            "mode_paiement": random.choice(["especes", "carte_bancaire", "carte_bancaire"]),
            # Plus d'espèces en boutique
            "vendeur_id": f"V{random.randint(100, 999)}"
        }

        # Sauvegarder dans un fichier JSON
        filename = f"{output_dir}/commande_{commande['id_commande']}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(commande, f, ensure_ascii=False, indent=2)

        compteur += 1
        print(
            f"✅ [{compteur}/500] Commande générée: {commande['id_commande']} - Montant: {commande['montant_total']} MAD")

        # Attendre entre 2 et 5 secondes
        time.sleep(random.uniform(2, 5))

except KeyboardInterrupt:
    print(f"\n⚠️  Arrêt du simulateur. {compteur} commandes générées.")
except Exception as e:
    print(f"\n❌ Erreur: {e}")

print(f"\n✅ Simulation terminée! {compteur} commandes générées dans {output_dir}")