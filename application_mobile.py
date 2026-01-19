import json
import random
import time
import os
from datetime import datetime
from faker import Faker

fake = Faker('fr_FR')

# Créer le répertoire de destination s'il n'existe pas
output_dir = "./data/sources/application_mobile"
os.makedirs(output_dir, exist_ok=True)

# Liste de produits possibles (mêmes que les autres canaux)
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

statuts = ["confirmée", "confirmée", "confirmée", "confirmée", "annulée"]  # 80% confirmée, 20% annulée

# Types d'appareils mobiles
appareils_mobiles = [
    "Android",
    "iPhone",
    "iPad",
    "Tablette Android"
]

# Versions d'application possibles
versions_app = [
    "3.2.1",
    "3.1.5",
    "3.0.9",
    "2.8.4"
]

compteur = 0

print(f"📱 Démarrage du simulateur APPLICATION MOBILE...")
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

        # Options de livraison spécifiques au mobile
        options_livraison = random.choice([
            "standard",  # 48h
            "express",  # 24h
            "point_relais"  # Retrait en point relais
        ])

        # Générer une adresse de livraison (comme le web)
        adresse_livraison = {
            "rue": fake.street_address(),
            "ville": fake.city(),
            "code_postal": fake.postcode(),
            "pays": "Maroc"
        }

        # Certaines commandes mobile peuvent utiliser le click & collect
        if random.random() > 0.7:  # 30% des commandes en click & collect
            options_livraison = "click_collect"
            adresse_livraison = None
            boutiques = ["Khouribga Centre", "Casablanca Marina", "Rabat Agdal", "Marrakech Gueliz"]
            boutique_collect = random.choice(boutiques)
        else:
            boutique_collect = None

        commande = {
            "id_commande": f"MOB-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}",
            "canal": "application_mobile",
            "date_commande": datetime.now().isoformat(),
            "client": {
                "nom": fake.name(),
                "email": fake.email(),
                "telephone": fake.phone_number(),
                "compte_client": f"C{random.randint(10000, 99999)}"  # Compte client spécifique à l'app
            },
            "appareil": {
                "type": random.choice(appareils_mobiles),
                "version_app": random.choice(versions_app),
                "os_version": f"{random.randint(10, 17)}.{random.randint(0, 9)}"
            },
            "adresse_livraison": adresse_livraison,
            "boutique_collect": boutique_collect,
            "produits": produits_commande,
            "montant_total": round(total, 2),
            "statut": random.choice(statuts),
            "mode_paiement": random.choice(["carte_bancaire", "mobile_paiement", "wallet_app", "carte_bancaire"]),
            "option_livraison": options_livraison,
            "frais_livraison": round(random.choice([0.0, 19.99, 29.99, 9.99]), 2) if adresse_livraison else 0.0,
            "notification_push": random.choice([True, False]),
            "promo_code": f"PROMO{random.randint(100, 999)}" if random.random() > 0.6 else None  # 40% avec code promo
        }

        # Sauvegarder dans un fichier JSON
        filename = f"{output_dir}/commande_{commande['id_commande']}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(commande, f, ensure_ascii=False, indent=2)

        compteur += 1
        print(
            f"✅ [{compteur}/500] Commande mobile générée: {commande['id_commande']} - Montant: {commande['montant_total']} MAD - Livraison: {commande['option_livraison']}")

        # Attendre entre 2 et 5 secondes
        time.sleep(random.uniform(2, 5))

except KeyboardInterrupt:
    print(f"\n⚠️  Arrêt du simulateur. {compteur} commandes générées.")
except Exception as e:
    print(f"\n❌ Erreur: {e}")

print(f"\n✅ Simulation terminée! {compteur} commandes générées dans {output_dir}")