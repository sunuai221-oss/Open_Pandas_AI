"""
Test du système hybride de dictionnaire de données
"""

import pandas as pd
from core.smart_dictionary_detector import detect_and_load_dictionary
from core.data_dictionary_manager import DataDictionaryManager


def test_e_commerce_detection():
    """Test détection domaine e-commerce"""
    # Créer un DataFrame type e-commerce
    df = pd.DataFrame({
        'customer_id': ['C001', 'C002', 'C003'],
        'email': ['test1@email.com', 'test2@email.com', 'test3@email.com'],
        'first_name': ['John', 'Jane', 'Bob'],
        'last_name': ['Doe', 'Smith', 'Johnson'],
        'phone': ['123-456-7890', '234-567-8901', '345-678-9012'],
        'address': ['123 Main St', '456 Oak Ave', '789 Pine Rd'],
        'city': ['New York', 'Los Angeles', 'Chicago'],
        'country': ['USA', 'USA', 'USA'],
        'signup_date': ['2024-01-15', '2024-02-20', '2024-03-10'],
        'lifetime_value': [1500.0, 2300.0, 890.0]
    })
    
    print("=" * 60)
    print("TEST 1: Détection E-commerce")
    print("=" * 60)
    
    matched_key, dictionary, confidence = detect_and_load_dictionary(df)
    
    print(f"✓ Matched Key: {matched_key}")
    print(f"✓ Confidence: {confidence*100:.0f}%")
    print(f"✓ Dataset Name: {dictionary.get('dataset_name')}")
    print(f"✓ Domain: {dictionary.get('domain')}")
    print(f"✓ Columns documented: {len(dictionary['columns'])}")
    
    assert matched_key is not None, "Should detect e-commerce domain"
    assert confidence > 0.7, "Confidence should be > 70%"
    
    print("\n✅ Test 1 PASSED\n")


def test_auto_generation():
    """Test génération automatique pour dataset inconnu"""
    # Créer un DataFrame unique
    df = pd.DataFrame({
        'var_x': [1, 2, 3],
        'var_y': [4, 5, 6],
        'var_z': ['a', 'b', 'c'],
        'strange_col': [10.5, 20.3, 30.1]
    })
    
    print("=" * 60)
    print("TEST 2: Auto-génération (dataset inconnu)")
    print("=" * 60)
    
    matched_key, dictionary, confidence = detect_and_load_dictionary(df)
    
    print(f"✓ Matched Key: {matched_key}")
    print(f"✓ Confidence: {confidence*100:.0f}%")
    print(f"✓ Method: {dictionary['detection']['method']}")
    print(f"✓ Columns generated: {len(dictionary['columns'])}")
    
    # Vérifier que chaque colonne a une description générée
    for col_name, col_dict in dictionary['columns'].items():
        assert 'description' in col_dict, f"Column {col_name} should have description"
        print(f"  - {col_name}: {col_dict['description']}")
    
    print("\n✅ Test 2 PASSED\n")


def test_enrichment_with_statistics():
    """Test enrichissement avec statistiques"""
    df = pd.DataFrame({
        'age': [25, 30, 35, 40, 45, None],
        'salary': [50000, 60000, 75000, 80000, 90000, None],
        'department': ['Sales', 'IT', 'HR', 'Sales', 'IT', 'HR']
    })
    
    print("=" * 60)
    print("TEST 3: Enrichissement avec statistiques")
    print("=" * 60)
    
    _, dictionary, _ = detect_and_load_dictionary(df)
    enriched = DataDictionaryManager.enrich_with_statistics(dictionary, df)
    
    print(f"✓ Total rows: {enriched['statistics']['total_rows']}")
    print(f"✓ Total columns: {enriched['statistics']['total_columns']}")
    print(f"✓ Memory usage: {enriched['statistics']['memory_usage_mb']} MB")
    
    # Vérifier les stats par colonne
    for col_name, col_dict in enriched['columns'].items():
        if 'statistics' in col_dict:
            stats = col_dict['statistics']
            print(f"\n  Column: {col_name}")
            print(f"    - Null %: {stats.get('null_pct', 'N/A')}")
            print(f"    - Unique: {stats.get('unique_count', 'N/A')}")
            if 'mean' in stats:
                print(f"    - Mean: {stats['mean']:.2f}")
    
    print("\n✅ Test 3 PASSED\n")


def test_validation():
    """Test validation du dictionnaire"""
    df = pd.DataFrame({
        'id': [1, 2, 3],
        'name': ['Alice', 'Bob', 'Charlie'],
        'email': ['a@test.com', 'b@test.com', None],
        'unused_col': [10, 20, 30]
    })
    
    print("=" * 60)
    print("TEST 4: Validation du dictionnaire")
    print("=" * 60)
    
    _, dictionary, _ = detect_and_load_dictionary(df)
    validation = DataDictionaryManager.validate_dictionary(dictionary, df)
    
    print(f"✓ Is Valid: {validation['is_valid']}")
    print(f"✓ Coverage: {validation['coverage']['coverage_pct']:.0f}%")
    print(f"✓ Warnings: {len(validation['warnings'])}")
    
    for warning in validation['warnings']:
        print(f"  - {warning}")
    
    for suggestion in validation['suggestions']:
        print(f"  💡 {suggestion}")
    
    print("\n✅ Test 4 PASSED\n")


def test_prompt_context():
    """Test création du contexte pour prompt"""
    df = pd.DataFrame({
        'product_id': ['P001', 'P002', 'P003'],
        'product_name': ['Laptop', 'Mouse', 'Keyboard'],
        'price': [999.99, 29.99, 79.99],
        'stock': [50, 200, 150]
    })
    
    print("=" * 60)
    print("TEST 5: Contexte pour prompt")
    print("=" * 60)
    
    _, dictionary, _ = detect_and_load_dictionary(df)
    enriched = DataDictionaryManager.enrich_with_statistics(dictionary, df)
    
    context = DataDictionaryManager.create_prompt_context(enriched)
    
    print("Context généré:")
    print(context[:500] + "...\n")
    
    # Vérifier que le contexte contient les éléments clés
    assert 'Available Columns' in context, "Should contain 'Available Columns'"
    assert 'Description' in context or 'description' in context, "Should contain column descriptions"
    
    print("✅ Test 5 PASSED\n")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("TESTS DU SYSTÈME HYBRIDE DE DICTIONNAIRE")
    print("="*60 + "\n")
    
    try:
        test_e_commerce_detection()
        test_auto_generation()
        test_enrichment_with_statistics()
        test_validation()
        test_prompt_context()
        
        print("\n" + "="*60)
        print("✅ TOUS LES TESTS PASSÉS!")
        print("="*60 + "\n")
        
    except AssertionError as e:
        print(f"\n❌ TEST ÉCHOUÉ: {e}\n")
        exit(1)
    except Exception as e:
        print(f"\n❌ ERREUR: {e}\n")
        import traceback
        traceback.print_exc()
        exit(1)
