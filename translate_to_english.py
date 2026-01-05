#!/usr/bin/env python3
"""
Script to help translate French text to English in the codebase.
This script identifies French strings in Python files and provides translations.
"""

import re
import os
from pathlib import Path

# Common French to English translations for UI strings
TRANSLATIONS = {
    # Common UI phrases
    "Charger": "Load",
    "Explorer": "Explore", 
    "Analyser": "Analyze",
    "Exporter": "Export",
    "Données": "Data",
    "Aperçu": "Preview",
    "Résultat": "Result",
    "Question": "Question",
    "Réponse": "Answer",
    "Historique": "History",
    "Paramètres": "Settings",
    "Préférences": "Preferences",
    "Session": "Session",
    "Mémoire": "Memory",
    "Qualité": "Quality",
    "Erreur": "Error",
    "Succès": "Success",
    "Avertissement": "Warning",
    "Information": "Info",
    
    # Actions
    "Charger des données": "Load Data",
    "Explorer les données": "Explore Data",
    "Commencer l'analyse IA": "Start AI Analysis",
    "Voir l'historique": "View History",
    "Posez votre question": "Ask your question",
    "Analyser": "Analyze",
    "Sauvegarder": "Save",
    "Télécharger": "Download",
    "Effacer": "Clear",
    
    # Status messages
    "Aucune donnée chargée": "No data loaded",
    "Chargez un fichier": "Load a file",
    "Aucun résultat": "No result",
    "Traitement terminé": "Processing complete",
    "Erreur lors du traitement": "Error during processing",
}

def find_french_strings_in_file(file_path):
    """Find French strings in a Python file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find string literals (both single and double quotes)
    # This is a simple regex - may need refinement
    string_pattern = r'["\']([^"\']*[àâäéèêëïîôùûüÿçÀÂÄÉÈÊËÏÎÔÙÛÜŸÇ][^"\']*)["\']'
    matches = re.findall(string_pattern, content)
    
    return matches

def main():
    """Main function to scan files and identify French text."""
    project_root = Path('.')
    
    # Files to check
    files_to_check = []
    
    # Add Python files
    for ext in ['*.py']:
        files_to_check.extend(project_root.rglob(ext))
    
    # Filter out __pycache__ and .pyc files
    files_to_check = [f for f in files_to_check if '__pycache__' not in str(f)]
    
    print(f"Found {len(files_to_check)} Python files to check")
    print("\nFiles with French text:\n")
    
    for file_path in files_to_check:
        french_strings = find_french_strings_in_file(file_path)
        if french_strings:
            print(f"\n{file_path}:")
            for s in french_strings[:5]:  # Show first 5
                print(f"  - {s[:80]}")

if __name__ == "__main__":
    main()
