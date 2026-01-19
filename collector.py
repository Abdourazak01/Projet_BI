import os
import json
import time
import shutil
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

# Configuration MongoDB
MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "multi_market"
COLLECTION_NAME = "commandes"

# Répertoires à surveiller
SOURCE_DIRS = [
    "./data/sources/site_web",
    "./data/sources/application_mobile",
    "./data/sources/boutique_physique"
]

ARCHIVE_DIR = "./data/archive"

# Créer le répertoire d'archive s'il n'existe pas
os.makedirs(ARCHIVE_DIR, exist_ok=True)

# Statistiques
stats = {
    "total_traite": 0,
    "succes": 0,
    "erreurs": 0,
    "doublons": 0,
    "par_canal": {"site_web": 0, "application_mobile": 0, "boutique_physique": 0}
}


def connect_mongodb():
    """Établir la connexion à MongoDB"""
    try:
        client = MongoClient(MONGO_URI)
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]

        # Créer un index unique sur id_commande pour éviter les doublons
        collection.create_index("id_commande", unique=True)

        print("✅ Connexion à MongoDB établie")
        print(f"   Base de données: {DATABASE_NAME}")
        print(f"   Collection: {COLLECTION_NAME}\n")

        return collection
    except Exception as e:
        print(f"❌ Erreur de connexion à MongoDB: {e}")
        return None


def standardize_commande(data, canal):
    """Standardiser la structure de la commande pour MongoDB"""

    # Structure commune à tous les canaux
    commande_standard = {
        "id_commande": data.get("id_commande", ""),
        "canal": canal,
        "date_commande": data.get("date_commande", datetime.now().isoformat()),
        "client": data.get("client", {}),
        "produits": data.get("produits", []),
        "montant_total": data.get("montant_total", 0.0),
        "statut": data.get("statut", "inconnu"),
        "date_import": datetime.now().isoformat()
    }

    # Ajouter les champs spécifiques à chaque canal
    if canal == "site_web":
        commande_standard.update({
            "adresse_livraison": data.get("adresse_livraison", {}),
            "mode_paiement": data.get("mode_paiement", "inconnu")
        })

    elif canal == "application_mobile":
        commande_standard.update({
            "appareil": data.get("appareil", {}),
            "adresse_livraison": data.get("adresse_livraison"),
            "boutique_collect": data.get("boutique_collect"),
            "mode_paiement": data.get("mode_paiement", "inconnu"),
            "option_livraison": data.get("option_livraison", "standard"),
            "frais_livraison": data.get("frais_livraison", 0.0),
            "notification_push": data.get("notification_push", False),
            "promo_code": data.get("promo_code")
        })

    elif canal == "boutique_physique":
        commande_standard.update({
            "boutique": data.get("boutique", "inconnue"),
            "mode_paiement": data.get("mode_paiement", "inconnu"),
            "vendeur_id": data.get("vendeur_id", "inconnu")
        })

    return commande_standard


def validate_json(data, canal):
    """Valider la structure d'une commande selon son canal"""

    # Champs obligatoires pour tous les canaux
    required_fields_commun = ["id_commande", "client", "produits", "montant_total", "statut"]

    # Vérification des champs communs
    for field in required_fields_commun:
        if field not in data:
            return False, f"Champ commun manquant: {field}"

    # Validation des champs obligatoires selon le canal
    if canal == "site_web":
        if "mode_paiement" not in data:
            return False, "Champ 'mode_paiement' manquant pour site web"
        if "adresse_livraison" not in data:
            return False, "Champ 'adresse_livraison' manquant pour site web"

    elif canal == "application_mobile":
        if "mode_paiement" not in data:
            return False, "Champ 'mode_paiement' manquant pour application mobile"
        if "option_livraison" not in data:
            return False, "Champ 'option_livraison' manquant pour application mobile"

    elif canal == "boutique_physique":
        if "boutique" not in data:
            return False, "Champ 'boutique' manquant pour boutique physique"
        if "mode_paiement" not in data:
            return False, "Champ 'mode_paiement' manquant pour boutique physique"

    # Validation de la liste de produits
    if not isinstance(data["produits"], list) or len(data["produits"]) == 0:
        return False, "Liste de produits invalide ou vide"

    # Validation de la structure de chaque produit
    for i, produit in enumerate(data["produits"]):
        produit_fields = ["nom_produit", "quantite", "prix_unitaire", "prix_total"]
        for field in produit_fields:
            if field not in produit:
                return False, f"Produit {i + 1}: champ '{field}' manquant"

    return True, "OK"


def detect_canal_from_filename(filename):
    """Détecter le canal à partir du nom de fichier"""
    if "WEB" in filename:
        return "site_web"
    elif "MOB" in filename:
        return "application_mobile"
    elif "BOU" in filename:
        return "boutique_physique"
    else:
        # Essayer de détecter à partir du chemin
        for canal in ["site_web", "application_mobile", "boutique_physique"]:
            if canal in filename.lower():
                return canal
        return "inconnu"


def process_file(filepath, collection):
    """Traiter un fichier JSON et l'insérer dans MongoDB"""
    try:
        # Lire le fichier JSON
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Détecter le canal
        filename = os.path.basename(filepath)
        canal_detected = detect_canal_from_filename(filename)

        # Si le canal n'est pas déjà dans les données, l'ajouter
        if "canal" not in data:
            data["canal"] = canal_detected
        else:
            canal_detected = data["canal"]

        # Valider les données selon le canal
        is_valid, message = validate_json(data, canal_detected)
        if not is_valid:
            print(f"   ⚠️  Validation échouée pour {filename}: {message}")
            stats["erreurs"] += 1
            return False

        # Standardiser la structure
        commande_standard = standardize_commande(data, canal_detected)

        # Insérer dans MongoDB
        collection.insert_one(commande_standard)

        # Mettre à jour les statistiques
        stats["succes"] += 1
        stats["par_canal"][canal_detected] += 1

        print(f"   ✅ Commande insérée: {commande_standard['id_commande']} ({canal_detected})")

        # Archiver le fichier
        archive_path = os.path.join(ARCHIVE_DIR, filename)
        shutil.move(filepath, archive_path)

        return True

    except DuplicateKeyError:
        stats["doublons"] += 1
        print(f"   ⚠️  Doublon détecté: {filename}")
        # Archiver quand même
        archive_path = os.path.join(ARCHIVE_DIR, filename)
        if os.path.exists(filepath):
            shutil.move(filepath, archive_path)
        return False

    except json.JSONDecodeError as e:
        stats["erreurs"] += 1
        print(f"   ❌ Erreur JSON dans {filename}: {e}")
        # Déplacer le fichier corrompu vers un dossier d'erreurs
        error_dir = os.path.join(ARCHIVE_DIR, "erreurs")
        os.makedirs(error_dir, exist_ok=True)
        error_path = os.path.join(error_dir, filename)
        if os.path.exists(filepath):
            shutil.move(filepath, error_path)
        print(f"   📁 Fichier déplacé vers: {error_path}")
        return False

    except Exception as e:
        stats["erreurs"] += 1
        print(f"   ❌ Erreur lors du traitement de {filename}: {e}")
        return False


def scan_directories(collection):
    """Scanner les répertoires sources et traiter les nouveaux fichiers"""
    files_to_process = []

    for source_dir in SOURCE_DIRS:
        if not os.path.exists(source_dir):
            print(f"⚠️  Répertoire inexistant: {source_dir}")
            continue

        # Lister uniquement les fichiers .json
        for filename in os.listdir(source_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(source_dir, filename)
                files_to_process.append(filepath)

    return files_to_process


def print_stats():
    """Afficher les statistiques détaillées"""
    print("\n" + "=" * 60)
    print("📊 STATISTIQUES DÉTAILLÉES")
    print("=" * 60)
    print(f"   Total traité:           {stats['total_traite']}")
    print(f"   ✅ Succès:              {stats['succes']}")
    print(f"   ⚠️  Doublons:            {stats['doublons']}")
    print(f"   ❌ Erreurs:             {stats['erreurs']}")
    print("\n   📈 Par canal:")
    for canal, count in stats['par_canal'].items():
        print(f"      • {canal}: {count}")

    taux_succes = (stats['succes'] / stats['total_traite'] * 100) if stats['total_traite'] > 0 else 0
    print(f"\n   📊 Taux de succès:       {taux_succes:.1f}%")
    print("=" * 60 + "\n")


def main():
    print("=" * 60)
    print("🚀 DÉMARRAGE DU SYSTÈME DE COLLECTE ET INTÉGRATION")
    print("=" * 60)
    print(f"⏰ Heure de démarrage: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔍 Surveillance des répertoires:")
    for dir_path in SOURCE_DIRS:
        print(f"   • {dir_path}")
    print(f"📦 Archivage dans: {ARCHIVE_DIR}")
    print(f"⏱️  Intervalle de scan: 10 secondes")
    print("=" * 60 + "\n")

    # Connexion à MongoDB
    collection = connect_mongodb()
    if collection is None:
        print("❌ Impossible de continuer sans connexion MongoDB")
        return

    print("🔄 Démarrage de la surveillance...\n")

    try:
        cycle = 0
        while True:
            cycle += 1
            print(f"🔍 Cycle {cycle} - {datetime.now().strftime('%H:%M:%S')}")

            # Scanner les répertoires
            files_to_process = scan_directories(collection)

            if files_to_process:
                print(f"   📁 {len(files_to_process)} fichier(s) trouvé(s)")

                for filepath in files_to_process:
                    stats["total_traite"] += 1
                    process_file(filepath, collection)

                # Afficher les stats après chaque cycle de traitement
                if cycle % 3 == 0:  # Afficher détaillé tous les 3 cycles
                    print_stats()
                else:
                    print(f"   📊 Traitement effectué: {len(files_to_process)} fichier(s)")
            else:
                print("   ℹ️  Aucun nouveau fichier")

            # Attendre 10 secondes
            time.sleep(10)

    except KeyboardInterrupt:
        print("\n\n⚠️  Arrêt du système demandé")
        print_stats()
        print("👋 Au revoir!\n")


if __name__ == "__main__":
    main()