import os
import json

def load_json(file):
    """Charge le contenu d'un fichier JSON, ou retourne une liste vide si le fichier n'existe pas ou est vide."""
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print(f"Erreur de décodage JSON dans le fichier : {file}")
                return []
    return []

def save_json(file, data):
    """Sauvegarde les données dans un fichier JSON."""
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
