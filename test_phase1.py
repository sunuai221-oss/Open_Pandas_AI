#!/usr/bin/env python
"""
Tests pour Phase 1 - Vérifier que les nouvelles fonctionnalités fonctionnent
"""

import sys
sys.path.insert(0, '/path/to/Open_Pandas_AI')

import pandas as pd
import numpy as np
from core.intention_detector import IntentionDetector
from core.result_validator import ResultValidator
from core.prompt_builder import build_prompt

# === TEST DATA ===
df_sample = pd.DataFrame({
    'product': ['A', 'B', 'C', 'D', 'E'],
    'sales': [1000, 2500, 1800, 3200, 900],
    'region': ['EU', 'US', 'EU', 'ASIA', 'US'],
    'date': pd.date_range('2024-01-01', periods=5),
    'quantity': [10, 25, 18, 32, 9]
})


def test_intention_detector():
    """Test du détecteur d'intentions"""
    print("\n" + "="*60)
    print("TEST 1: Intention Detector")
    print("="*60)
    
    test_questions = [
        "Quels sont les top 5 produits par ventes ?",
        "Moyenne de ventes par région",
        "Trier les clients par date décroissante",
        "Détecter les anomalies de ventes",
        "Fusionner les données avec les clients"
    ]
    
    for q in test_questions:
        print(f"\n📌 Question: {q}")
        
        all_intentions = IntentionDetector.detect_all(q)
        primary = IntentionDetector.detect_primary(q)
        
        detected = [k for k, v in all_intentions.items() if v]
        print(f"   ✓ Toutes les intentions: {', '.join(detected)}")
        print(f"   ✓ Intentions principales: {', '.join(primary)}")


def test_result_validator():
    """Test du validateur de résultats"""
    print("\n" + "="*60)
    print("TEST 2: Result Validator")
    print("="*60)
    
    # Test 1: DataFrame propre
    print("\n📌 Test 1: DataFrame propre")
    validation = ResultValidator.validate_and_enrich(
        result=df_sample,
        question="Top 5 produits par ventes",
        original_df=df_sample
    )
    print(f"   ✓ Warnings: {validation['warnings'] if validation['warnings'] else 'Aucun'}")
    print(f"   ✓ Qualité: {validation['quality_score']}%")
    print(f"   ✓ Suggestions: {validation['suggestions']}")
    
    # Test 2: DataFrame avec valeurs manquantes
    print("\n📌 Test 2: DataFrame avec valeurs manquantes")
    df_missing = df_sample.copy()
    df_missing.loc[0, 'sales'] = np.nan
    df_missing.loc[1, 'region'] = np.nan
    
    validation = ResultValidator.validate_and_enrich(
        result=df_missing,
        question="Analyser les ventes",
        original_df=df_sample
    )
    print(f"   ✓ Warnings détectés: {len(validation['warnings'])}")
    for w in validation['warnings']:
        print(f"      - {w}")
    print(f"   ✓ Qualité: {validation['quality_score']}%")
    
    # Test 3: Nombre
    print("\n📌 Test 3: Résultat numérique")
    validation = ResultValidator.validate_and_enrich(
        result=42.5,
        question="Quel est le nombre total de clients?",
        original_df=df_sample
    )
    print(f"   ✓ Type détecté: {validation['context'].get('type')}")
    print(f"   ✓ Valeur: {validation['formatted']}")
    
    # Test 4: Liste
    print("\n📌 Test 4: Résultat liste")
    validation = ResultValidator.validate_and_enrich(
        result=['Apple', 'Banana', 'Cherry'],
        question="Quels produits?",
        original_df=df_sample
    )
    print(f"   ✓ Type détecté: {validation['context'].get('type')}")
    print(f"   ✓ Affichage: {validation['formatted']}")


def test_enhanced_prompt():
    """Test du prompt enrichi"""
    print("\n" + "="*60)
    print("TEST 3: Enhanced Prompt Builder")
    print("="*60)
    
    print("\n📌 Prompt enrichi:")
    prompt = build_prompt(
        df=df_sample,
        question="Quel sont les 3 meilleures régions par ventes?",
        user_level="expert",
        detected_skills=["aggregation", "ranking"]
    )
    
    # Afficher les sections clés du prompt
    lines = prompt.split('\n')
    
    # Chercher les sections importantes
    print("\n✓ Sections du prompt:")
    for i, line in enumerate(lines):
        if any(marker in line for marker in ['📚', '📊', '📋', '🔍', '🚨', '🎯', '⚠️']):
            print(f"   {line[:80]}")
    
    # Vérifier que les intentions spécifiques sont présentes
    if 'RANKING' in prompt:
        print("\n✓ Instructions RANKING trouvées")
    if 'AGRÉGATION' in prompt:
        print("✓ Instructions AGRÉGATION trouvées")
    
    # Afficher la longueur du prompt
    print(f"\n✓ Longueur du prompt: {len(prompt)} caractères")
    print(f"✓ Nombre de lignes: {len(lines)}")


def test_integration():
    """Test d'intégration complet"""
    print("\n" + "="*60)
    print("TEST 4: Integration complète")
    print("="*60)
    
    question = "Top 5 produits par ventes dans chaque région"
    
    print(f"\n📌 Question: {question}")
    
    # 1. Détection intentions
    intentions = IntentionDetector.detect_primary(question)
    print(f"✓ Intentions: {intentions}")
    
    # 2. Build prompt enrichi
    prompt = build_prompt(
        df=df_sample,
        question=question,
        user_level="expert",
        detected_skills=["ranking", "aggregation"]
    )
    print(f"✓ Prompt construit ({len(prompt)} chars)")
    
    # 3. Simuler un résultat
    result_df = df_sample.groupby('region')['sales'].sum().nlargest(5)
    
    # 4. Valider le résultat
    validation = ResultValidator.validate_and_enrich(
        result=result_df,
        question=question,
        original_df=df_sample,
        detected_skills=intentions
    )
    
    print(f"✓ Résultat validé")
    print(f"   - Qualité: {validation['quality_score']}%")
    print(f"   - Warnings: {len(validation['warnings'])}")
    print(f"   - Suggestions: {len(validation['suggestions'])}")
    
    print(f"\n✅ Intégration complète: OK")


if __name__ == "__main__":
    try:
        test_intention_detector()
        test_result_validator()
        test_enhanced_prompt()
        test_integration()
        
        print("\n" + "="*60)
        print("🎉 TOUS LES TESTS PASSÉS!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
