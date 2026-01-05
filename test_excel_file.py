"""
Test du système hybride sur le fichier Excel "Order for Nabih Nagib.xls"
"""

import pandas as pd
from core.smart_dictionary_detector import detect_and_load_dictionary
from core.data_dictionary_manager import DataDictionaryManager
import json


def test_order_file():
    """Test détection et dictionnaire sur le fichier commande"""
    
    print("=" * 80)
    print("TEST: Système hybride sur Order for Nabih Nagib.xls")
    print("=" * 80)
    
    # Charger le fichier Excel
    try:
        file_path = "tableaux excel/Order for Nabih Nagib.xls"
        df = pd.read_excel(file_path)
        
        print(f"\n✅ Fichier chargé: {file_path}")
        print(f"   Shape: {df.shape[0]} lignes × {df.shape[1]} colonnes")
        
    except FileNotFoundError:
        print(f"\n❌ Fichier non trouvé: {file_path}")
        return
    except Exception as e:
        print(f"\n❌ Erreur chargement: {e}")
        return
    
    # ===== AFFICHER APERÇU DES DONNÉES =====
    print("\n" + "=" * 80)
    print("APERÇU DES DONNÉES")
    print("=" * 80)
    
    print(f"\nColonnes ({len(df.columns)}):")
    for i, col in enumerate(df.columns, 1):
        dtype = df[col].dtype
        nulls = df[col].isna().sum()
        uniques = df[col].nunique()
        print(f"  {i}. {col:30} | Type: {str(dtype):15} | Nulls: {nulls:3} | Uniques: {uniques}")
    
    print(f"\nPremières 5 lignes:")
    print(df.head().to_string())
    
    # ===== DÉTECTION AUTOMATIQUE =====
    print("\n" + "=" * 80)
    print("DÉTECTION AUTOMATIQUE")
    print("=" * 80)
    
    matched_key, dictionary, confidence = detect_and_load_dictionary(df)
    
    print(f"\n✓ Matched Domain: {matched_key if matched_key else 'NONE (Auto-generated)'}")
    print(f"✓ Confidence: {confidence*100:.0f}%")
    print(f"✓ Dataset Name: {dictionary.get('dataset_name', 'N/A')}")
    print(f"✓ Domain: {dictionary.get('domain', 'N/A')}")
    print(f"✓ Detection Method: {dictionary.get('detection', {}).get('method', 'N/A')}")
    
    # ===== ENRICHISSEMENT AVEC STATISTIQUES =====
    print("\n" + "=" * 80)
    print("ENRICHISSEMENT AVEC STATISTIQUES")
    print("=" * 80)
    
    enriched_dict = DataDictionaryManager.enrich_with_statistics(dictionary, df)
    
    print(f"\n✓ Total Rows: {enriched_dict['statistics']['total_rows']}")
    print(f"✓ Total Columns: {enriched_dict['statistics']['total_columns']}")
    print(f"✓ Memory Usage: {enriched_dict['statistics']['memory_usage_mb']} MB")
    print(f"✓ Missing Values: {enriched_dict['statistics']['missing_values_pct']:.2f}%")
    
    # ===== AFFICHER DICTIONNAIRE COMPLET =====
    print("\n" + "=" * 80)
    print("DICTIONNAIRE COMPLET")
    print("=" * 80)
    
    for col_name, col_info in enriched_dict['columns'].items():
        print(f"\n📋 {col_name}:")
        print(f"   Description: {col_info.get('description', 'N/A')}")
        print(f"   Type: {col_info.get('data_type', 'N/A')}")
        
        if 'statistics' in col_info:
            stats = col_info['statistics']
            print(f"   Statistics:")
            print(f"     - Null %: {stats.get('null_pct', 0):.1f}%")
            print(f"     - Unique: {stats.get('unique_count', 0)}")
            
            if 'min' in stats:
                print(f"     - Min: {stats['min']}")
            if 'max' in stats:
                print(f"     - Max: {stats['max']}")
            if 'mean' in stats:
                print(f"     - Mean: {stats['mean']:.2f}")
            
            if 'unique_values' in stats:
                values = stats['unique_values']
                print(f"     - Sample values: {values[:5]}")
        
        if 'possible_values' in col_info:
            print(f"   Possible values: {col_info['possible_values']}")
    
    # ===== VALIDATION =====
    print("\n" + "=" * 80)
    print("VALIDATION DICTIONNAIRE")
    print("=" * 80)
    
    validation = DataDictionaryManager.validate_dictionary(enriched_dict, df)
    
    print(f"\n✓ Is Valid: {validation['is_valid']}")
    print(f"✓ Coverage: {validation['coverage']['coverage_pct']:.1f}%")
    print(f"✓ Documented: {validation['coverage']['documented_columns']}/{validation['coverage']['total_columns']}")
    
    if validation['warnings']:
        print(f"\n⚠️  Warnings ({len(validation['warnings'])}):")
        for warning in validation['warnings']:
            print(f"   - {warning}")
    
    if validation['suggestions']:
        print(f"\n💡 Suggestions ({len(validation['suggestions'])}):")
        for suggestion in validation['suggestions']:
            print(f"   - {suggestion}")
    
    # ===== CONTEXTE POUR PROMPT =====
    print("\n" + "=" * 80)
    print("CONTEXTE POUR PROMPT LLM")
    print("=" * 80)
    
    prompt_context = DataDictionaryManager.create_prompt_context(enriched_dict)
    print(f"\n{prompt_context}")
    
    # ===== RÉSUMÉ FINAL =====
    print("\n" + "=" * 80)
    print("RÉSUMÉ")
    print("=" * 80)
    
    print(f"""
✅ Fichier: Order for Nabih Nagib.xls
✅ Détection: {'✓ ' + matched_key if matched_key else '⚠️ Auto-générée'}
✅ Confiance: {confidence*100:.0f}%
✅ Colonnes: {len(df.columns)}
✅ Lignes: {len(df):,}
✅ Couverture dict: {validation['coverage']['coverage_pct']:.0f}%
✅ État: {'PRÊT' if validation['is_valid'] else 'À enrichir'}
    """)


if __name__ == "__main__":
    test_order_file()
