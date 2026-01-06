import pandas as pd

from agents.detector import detect_domain
from core.business_examples import match_business_example, normalize_column_name


# ==================== Existing signature tests ====================

def test_detect_domain_hr_signature():
    df = pd.DataFrame(
        {
            "employee_id": ["EMP-001", "EMP-002"],
            "department": ["Sales", "HR"],
            "job_title": ["Manager", "HRBP"],
            "salary": [70000, 65000],
            "hire_date": ["2020-01-01", "2021-01-01"],
        }
    )
    res = detect_domain(df)
    assert res.domain == "hr"
    assert res.confidence >= 0.5
    assert res.reasons


def test_detect_domain_finance_signature():
    df = pd.DataFrame(
        {
            "transaction_id": ["TXN-1", "TXN-2"],
            "date": ["2024-01-01", "2024-01-02"],
            "amount": [100.0, -25.5],
            "category": ["income", "expense"],
            "account": ["Bank", "Bank"],
        }
    )
    res = detect_domain(df)
    assert res.domain == "finance"
    assert res.confidence >= 0.5


def test_detect_domain_ecommerce_signature():
    df = pd.DataFrame(
        {
            "order_id": ["ORD-1", "ORD-2"],
            "customer_id": ["C1", "C2"],
            "order_date": ["2024-01-01", "2024-01-02"],
            "amount": [50.0, 75.0],
            "status": ["delivered", "pending"],
        }
    )
    res = detect_domain(df)
    assert res.domain == "ecommerce"
    assert res.confidence >= 0.5


def test_detect_domain_crm_signature():
    df = pd.DataFrame(
        {
            "lead_id": ["L1", "L2"],
            "email": ["a@b.com", "c@d.com"],
            "company": ["Acme", "Globex"],
            "source": ["organic", "paid_ads"],
            "stage": ["qualified", "proposal"],
            "created_date": ["2024-01-01", "2024-01-02"],
        }
    )
    res = detect_domain(df)
    assert res.domain == "crm"
    assert res.confidence >= 0.5


# ==================== v2 tests: synonyms, date-like, ambiguities ====================

def test_detect_domain_synonyms_fr():
    """Detect domain using FR synonyms (montant, commande, client)."""
    df = pd.DataFrame(
        {
            "commande": ["CMD-1", "CMD-2"],
            "client": ["CL1", "CL2"],
            "montant": [100.0, 200.0],
            "date_creation": ["2024-01-01", "2024-01-02"],
        }
    )
    res = detect_domain(df)
    # Should pick up ecommerce via synonyms (order/customer/amount)
    assert res.domain in ("ecommerce", "finance")  # acceptable due to 'montant'
    assert res.confidence >= 0.3


def test_detect_domain_date_like_columns():
    """Columns that look date-like should contribute to detection."""
    df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "created_at": ["2024-01-01", "2024-02-01", "2024-03-01"],
            "updated_at": ["2024-01-02", "2024-02-02", "2024-03-02"],
            "value": [10.0, 20.0, 30.0],
        }
    )
    res = detect_domain(df)
    # Should fall back to generic or finance (date-like boost) but not crash
    assert res.domain in ("generic", "finance")
    assert res.confidence >= 0.2


def test_detect_domain_ambiguous_generic_fallback():
    """Ambiguous dataset with no clear domain should fall back to generic."""
    df = pd.DataFrame(
        {
            "col_a": ["x", "y", "z"],
            "col_b": [1, 2, 3],
            "col_c": [True, False, True],
        }
    )
    res = detect_domain(df)
    assert res.domain == "generic"
    assert res.confidence <= 0.5


def test_normalize_column_name_accents():
    """normalize_column_name should strip accents while keeping letters."""
    assert normalize_column_name("Prénom") == "prenom"
    assert normalize_column_name("Numéro de commande") == "numero_de_commande"
    assert normalize_column_name("Été 2024") == "ete_2024"
    assert normalize_column_name("Montant (€)") == "montant"


def test_match_business_example_alias():
    """match_business_example should be an alias for match_business_examples."""
    cols = ["customer_id", "email", "phone", "country", "status", "subscription_date"]
    result = match_business_example(cols)
    assert isinstance(result, list)
    # Expecting ecommerce_customers to score high
    if result:
        top_key, top_score = result[0]
        assert "ecommerce" in top_key or "customers" in top_key
        assert top_score >= 0.5

