"""
Business Examples - Exemples métiers prédéfinis pour détection automatique.

v2 (retrocompatible):
- Ajout de champs OPTIONNELS (typical_questions, common_metrics, recommended_charts, column_synonyms, quality_rules, business_intents)
- Ajout d'utilitaires (normalize_column_name, match_business_examples, get_domain_assets)

Important: ne casse pas l'API existante:
- get_business_example(key)
- get_all_business_examples()
"""

from __future__ import annotations

from typing import Dict, Any, List, Tuple

import re

# ============================================
# 1. E-COMMERCE EXAMPLES
# ============================================

ECOMMERCE_CUSTOMERS = {
    "dataset_name": "E-commerce Customers",
    "domain": "ecommerce",
    "description": "List of customers with contact and subscription info",
    "columns": {
        "customer_id": {
            "description": "Unique customer identifier",
            "data_type": "string",
            "business_rules": ["Unique", "Never null", "Primary key"],
            "validation": "NOT NULL, UNIQUE",
            "examples": ["CUST-001", "C12345", "00001"]
        },
        "email": {
            "description": "Customer email address",
            "data_type": "string",
            "business_rules": ["Valid email format", "Unique", "For contact"],
            "validation": "MATCHES email_pattern, NOT NULL, UNIQUE",
            "examples": ["john@example.com", "jane.doe@company.com"]
        },
        "phone": {
            "description": "Customer phone number",
            "data_type": "string",
            "business_rules": ["International format", "Can be null"],
            "validation": "Matches phone_pattern OR NULL",
            "examples": ["+1-555-0123", "555.0123"]
        },
        "subscription_date": {
            "description": "Date customer joined",
            "data_type": "datetime",
            "business_rules": ["In past", "Registration date"],
            "validation": "NOT NULL, <= TODAY()",
            "examples": ["2024-01-15", "2023-12-01"]
        },
        "country": {
            "description": "Customer country of residence",
            "data_type": "string",
            "business_rules": ["ISO 2-letter code", "Affects tax"],
            "validation": "IN country_list",
            "examples": ["US", "FR", "DE", "GB"]
        },
        "status": {
            "description": "Customer account status",
            "data_type": "enum",
            "possible_values": ["active", "inactive", "suspended", "deleted"],
            "business_rules": ["Active = can order", "Deleted = do not contact"],
            "validation": "IN (active, inactive, suspended, deleted)",
            "examples": ["active", "suspended"]
        }
    }
    ,
    # v2 optional assets
    "typical_questions": [
        "Quels sont les pays avec le plus de clients actifs ?",
        "Quel est le taux de clients inactifs/suspendus ?",
    ],
    "common_metrics": ["customer_count", "active_customer_pct"],
    "recommended_charts": ["bar", "pie"],
    "column_synonyms": {
        "customer_id": ["id_client", "client_id", "customerid", "idcustomer"],
        "subscription_date": ["date_inscription", "signup_date", "date_adhesion"],
        "country": ["pays", "country_code"],
        "status": ["etat", "statut"],
    },
}

ECOMMERCE_PRODUCTS = {
    "dataset_name": "E-commerce Products",
    "domain": "ecommerce",
    "description": "Product catalog with pricing and inventory",
    "columns": {
        "product_id": {
            "description": "Unique product identifier",
            "data_type": "string",
            "business_rules": ["Unique", "Primary key"],
            "validation": "NOT NULL, UNIQUE",
            "examples": ["SKU-001", "PROD-12345"]
        },
        "name": {
            "description": "Product display name",
            "data_type": "string",
            "business_rules": ["For customer view", "Not null"],
            "validation": "NOT NULL, LENGTH > 3",
            "examples": ["iPhone 15 Pro", "Wireless Mouse"]
        },
        "price": {
            "description": "Current selling price (currency dependent)",
            "data_type": "float",
            "business_rules": ["Must be > 0", "Usually in USD/EUR", "Excludes tax"],
            "validation": "NOT NULL, > 0, <= 999999.99",
            "examples": [99.99, 1299.50, 25.00]
        },
        "stock": {
            "description": "Available inventory quantity",
            "data_type": "integer",
            "business_rules": ["Must be >= 0", "Affects availability"],
            "validation": "NOT NULL, >= 0",
            "examples": [0, 15, 1000]
        },
        "category": {
            "description": "Product category",
            "data_type": "enum",
            "possible_values": ["Electronics", "Clothing", "Books", "Home", "Sports"],
            "business_rules": ["For classification", "Affects shipping"],
            "validation": "IN category_list",
            "examples": ["Electronics", "Clothing"]
        },
        "status": {
            "description": "Product availability status",
            "data_type": "enum",
            "possible_values": ["in_stock", "backorder", "discontinued", "pre_order"],
            "business_rules": ["discontinued = hide from catalog"],
            "validation": "IN status_list",
            "examples": ["in_stock", "discontinued"]
        }
    }
}

ECOMMERCE_ORDERS = {
    "dataset_name": "E-commerce Orders",
    "domain": "ecommerce",
    "description": "Customer orders and transactions",
    "columns": {
        "order_id": {
            "description": "Unique order identifier",
            "data_type": "string",
            "business_rules": ["Unique", "For tracking"],
            "validation": "NOT NULL, UNIQUE",
            "examples": ["ORD-001", "2024-001234"]
        },
        "customer_id": {
            "description": "Customer who placed order (FK)",
            "data_type": "string",
            "business_rules": ["Must exist in customers", "Not null"],
            "validation": "NOT NULL, IN customers.customer_id",
            "examples": ["CUST-001"]
        },
        "order_date": {
            "description": "When order was placed",
            "data_type": "datetime",
            "business_rules": ["In past", "For analytics"],
            "validation": "NOT NULL, <= TODAY()",
            "examples": ["2024-01-15T14:30:00Z"]
        },
        "amount": {
            "description": "Total order amount (currency)",
            "data_type": "float",
            "business_rules": ["Must be > 0", "Includes tax"],
            "validation": "NOT NULL, > 0",
            "examples": [149.99, 1299.50]
        },
        "status": {
            "description": "Order fulfillment status",
            "data_type": "enum",
            "possible_values": ["pending", "confirmed", "shipped", "delivered", "cancelled"],
            "business_rules": ["Workflow: pending → confirmed → shipped → delivered"],
            "validation": "IN status_list",
            "examples": ["delivered", "cancelled"]
        }
    }
    ,
    "typical_questions": [
        "Quel est le chiffre d'affaires par mois ?",
        "Top 10 clients par montant total de commandes",
    ],
    "common_metrics": ["total_revenue", "avg_order_value", "order_count"],
    "recommended_charts": ["line", "bar"],
    "column_synonyms": {
        "order_id": ["commande", "numero_commande", "order", "id_commande"],
        "order_date": ["date_commande", "date_order", "created_at"],
        "amount": ["montant", "total", "revenue", "ca"],
        "customer_id": ["id_client", "client_id"],
        "status": ["etat", "statut_commande"],
    },
}

# ============================================
# 2. CRM EXAMPLES
# ============================================

CRM_LEADS = {
    "dataset_name": "CRM Leads",
    "domain": "crm",
    "description": "Sales leads and prospects",
    "columns": {
        "lead_id": {
            "description": "Unique lead identifier",
            "data_type": "string",
            "business_rules": ["Unique", "Primary key"],
            "validation": "NOT NULL, UNIQUE",
            "examples": ["LEAD-001", "L12345"]
        },
        "email": {
            "description": "Lead email address",
            "data_type": "string",
            "business_rules": ["For contact", "Can be null"],
            "validation": "MATCHES email_pattern OR NULL",
            "examples": ["prospect@company.com"]
        },
        "company": {
            "description": "Company name",
            "data_type": "string",
            "business_rules": ["For B2B classification"],
            "validation": "Can be null",
            "examples": ["Acme Corp", "Tech Startup Inc"]
        },
        "source": {
            "description": "How lead was acquired",
            "data_type": "enum",
            "possible_values": ["organic", "paid_ads", "referral", "event", "cold_outreach"],
            "business_rules": ["For ROI tracking"],
            "validation": "IN source_list",
            "examples": ["paid_ads", "referral"]
        },
        "stage": {
            "description": "Sales pipeline stage",
            "data_type": "enum",
            "possible_values": ["qualified", "contacted", "proposal", "negotiation", "closed_won", "closed_lost"],
            "business_rules": ["Workflow progression"],
            "validation": "IN stage_list",
            "examples": ["proposal", "closed_won"]
        },
        "created_date": {
            "description": "When lead was created",
            "data_type": "datetime",
            "business_rules": ["In past"],
            "validation": "NOT NULL, <= TODAY()",
            "examples": ["2024-01-10T10:00:00Z"]
        }
    }
    ,
    "typical_questions": [
        "Quelle est la repartition des leads par source et stage ?",
        "Combien de leads par mois ?",
    ],
    "common_metrics": ["lead_count", "conversion_rate"],
    "recommended_charts": ["bar", "line"],
    "column_synonyms": {
        "lead_id": ["id_lead", "prospect_id"],
        "created_date": ["date_creation", "created_at"],
        "stage": ["etape", "pipeline_stage"],
        "source": ["origine", "acquisition_source"],
        "company": ["entreprise", "societe"],
    },
}

CRM_ACCOUNTS = {
    "dataset_name": "CRM Accounts",
    "domain": "crm",
    "description": "Customer accounts and companies",
    "columns": {
        "account_id": {
            "description": "Unique account identifier",
            "data_type": "string",
            "business_rules": ["Unique", "Primary key"],
            "validation": "NOT NULL, UNIQUE",
            "examples": ["ACC-001", "A12345"]
        },
        "company_name": {
            "description": "Official company name",
            "data_type": "string",
            "business_rules": ["Not null"],
            "validation": "NOT NULL",
            "examples": ["Microsoft Corporation", "Apple Inc"]
        },
        "industry": {
            "description": "Industry classification",
            "data_type": "string",
            "business_rules": ["For segmentation"],
            "validation": "Can be null",
            "examples": ["Technology", "Finance", "Healthcare"]
        },
        "revenue": {
            "description": "Annual company revenue (in millions)",
            "data_type": "float",
            "business_rules": ["Can be null", "> 0 if present"],
            "validation": "NULL OR > 0",
            "examples": [250.5, 1000.0]
        },
        "employees": {
            "description": "Number of employees",
            "data_type": "integer",
            "business_rules": ["Can be null", ">= 0"],
            "validation": "NULL OR >= 0",
            "examples": [500, 50000]
        }
    }
}

# ============================================
# 3. HR EXAMPLES
# ============================================

HR_EMPLOYEES = {
    "dataset_name": "HR Employees",
    "domain": "hr",
    "description": "Employee master data",
    "columns": {
        "employee_id": {
            "description": "Unique employee identifier",
            "data_type": "string",
            "business_rules": ["Unique", "Primary key"],
            "validation": "NOT NULL, UNIQUE",
            "examples": ["EMP-001", "E12345"]
        },
        "email": {
            "description": "Company email address",
            "data_type": "string",
            "business_rules": ["Unique", "Official contact"],
            "validation": "NOT NULL, UNIQUE, MATCHES email_pattern",
            "examples": ["john.doe@company.com"]
        },
        "department": {
            "description": "Department assignment",
            "data_type": "string",
            "business_rules": ["For org structure"],
            "validation": "IN department_list",
            "examples": ["Engineering", "Sales", "HR"]
        },
        "job_title": {
            "description": "Job position title",
            "data_type": "string",
            "business_rules": ["For classification"],
            "validation": "NOT NULL",
            "examples": ["Software Engineer", "Sales Manager"]
        },
        "salary": {
            "description": "Annual salary (currency)",
            "data_type": "float",
            "business_rules": ["Confidential", "> 0", "Exclude interns if < min_salary"],
            "validation": "NOT NULL, > 0, < max_salary",
            "examples": [50000.00, 120000.00]
        },
        "hire_date": {
            "description": "Employment start date",
            "data_type": "datetime",
            "business_rules": ["In past"],
            "validation": "NOT NULL, <= TODAY()",
            "examples": ["2020-01-15"]
        },
        "status": {
            "description": "Employment status",
            "data_type": "enum",
            "possible_values": ["active", "on_leave", "terminated"],
            "business_rules": ["Active = current employee"],
            "validation": "IN status_list",
            "examples": ["active", "terminated"]
        }
    }
    ,
    "typical_questions": [
        "Quel est le salaire moyen par departement ?",
        "Quelle est l'anciennete moyenne par departement ?",
    ],
    "common_metrics": ["headcount", "avg_salary", "median_salary", "avg_tenure_years"],
    "recommended_charts": ["bar", "box"],
    "column_synonyms": {
        "employee_id": ["id_employe", "matricule", "emp_id"],
        "department": ["departement", "service"],
        "job_title": ["poste", "intitule_poste"],
        "hire_date": ["date_embauche", "date_entree"],
        "salary": ["salaire", "remuneration", "compensation"],
        "status": ["statut", "etat"],
    },
}

# ============================================
# 4. FINANCE EXAMPLES
# ============================================

FINANCE_TRANSACTIONS = {
    "dataset_name": "Finance Transactions",
    "domain": "finance",
    "description": "Financial transactions and ledger entries",
    "columns": {
        "transaction_id": {
            "description": "Unique transaction identifier",
            "data_type": "string",
            "business_rules": ["Unique", "Audit trail"],
            "validation": "NOT NULL, UNIQUE",
            "examples": ["TXN-001", "2024-001234"]
        },
        "date": {
            "description": "Transaction date",
            "data_type": "datetime",
            "business_rules": ["In past", "For reporting period"],
            "validation": "NOT NULL, <= TODAY()",
            "examples": ["2024-01-15"]
        },
        "amount": {
            "description": "Transaction amount (currency)",
            "data_type": "float",
            "business_rules": ["Can be positive or negative"],
            "validation": "NOT NULL",
            "examples": [1000.00, -500.50]
        },
        "category": {
            "description": "Transaction category",
            "data_type": "enum",
            "possible_values": ["income", "expense", "transfer", "adjustment"],
            "business_rules": ["For classification"],
            "validation": "IN category_list",
            "examples": ["income", "expense"]
        },
        "account": {
            "description": "Account number or name",
            "data_type": "string",
            "business_rules": ["For segregation"],
            "validation": "NOT NULL",
            "examples": ["Bank-001", "ACC-USD"]
        }
    }
    ,
    "typical_questions": [
        "Quel est le total des montants par categorie et par mois ?",
        "Quelles sont les plus grosses transactions (valeur absolue) ?",
    ],
    "common_metrics": ["total_amount", "net_amount", "expense_by_category"],
    "recommended_charts": ["bar", "line"],
    "column_synonyms": {
        "transaction_id": ["id_transaction", "txn_id"],
        "date": ["transaction_date", "date_transaction"],
        "amount": ["montant", "valeur"],
        "category": ["categorie", "type"],
        "account": ["compte", "account_name"],
    },
}

# ============================================
# 5. E-COMMERCE GnC ORDER (ORDER LINES)
# ============================================

ECOMMERCE_GNC_ORDER = {
    "dataset_name": "GnC order",
    "domain": "ecommerce",
    "description": "Order line items (GnC) with quantity and pricing",
    "columns": {
        "item_name": {
            "description": "SKU or product reference",
            "data_type": "string",
            "business_rules": ["Unique within order lines", "Not null"],
            "validation": "NOT NULL",
            "examples": ["ASW1100452", "ASYYF00041"]
        },
        "description": {
            "description": "Product description (EN)",
            "data_type": "string",
            "business_rules": ["Human-readable", "Not null"],
            "validation": "NOT NULL",
            "examples": [
                "Funko POP Dragon Ball Z Vegeta Blue Hair Cartoon Figure",
                "29 Styles Demon Slayer Kimetsu no Yaiba Character Cosplay Haori"
            ]
        },
        "remark_1": {
            "description": "Variant / option",
            "data_type": "string",
            "business_rules": ["Optional"],
            "validation": "NULL OR LENGTH > 0",
            "examples": ["Color:2", "Size:2XL", "None"]
        },
        "qty": {
            "description": "Quantity ordered for the line",
            "data_type": "integer",
            "business_rules": [">= 1"],
            "validation": "NOT NULL, >= 1",
            "examples": [3, 6, 10]
        },
        "unit_price/usd": {
            "description": "Unit price in USD",
            "data_type": "float",
            "business_rules": ["> 0", "USD"],
            "validation": "NOT NULL, > 0",
            "examples": [3.69, 5.23, 12.50]
        },
        "amount": {
            "description": "Line total (qty * unit_price)",
            "data_type": "float",
            "business_rules": [">= 0", "Should equal qty * unit_price"],
            "validation": "NOT NULL, >= 0",
            "examples": [11.07, 15.69, 19.92]
        },
    }
}

# ============================================
# MASTER DICTIONARY
# ============================================

BUSINESS_EXAMPLES = {
    # E-commerce
    "ecommerce_customers": ECOMMERCE_CUSTOMERS,
    "ecommerce_products": ECOMMERCE_PRODUCTS,
    "ecommerce_orders": ECOMMERCE_ORDERS,
    
    # CRM
    "crm_leads": CRM_LEADS,
    "crm_accounts": CRM_ACCOUNTS,
    
    # HR
    "hr_employees": HR_EMPLOYEES,
    
    # Finance
    "finance_transactions": FINANCE_TRANSACTIONS,

    # E-commerce GnC order (order lines)
    "ecommerce_gnc_order": ECOMMERCE_GNC_ORDER,
}

def get_all_business_examples() -> Dict[str, Dict[str, Any]]:
    """Retourne tous les exemples métiers disponibles"""
    return BUSINESS_EXAMPLES

def get_business_example(key: str) -> Dict[str, Any]:
    """Retourne un exemple métier spécifique"""
    return BUSINESS_EXAMPLES.get(key)

def list_available_examples() -> Dict[str, list]:
    """Liste tous les domaines et exemples disponibles"""
    domains = {}
    for key, example in BUSINESS_EXAMPLES.items():
        domain = example.get("domain")
        if domain not in domains:
            domains[domain] = []
        domains[domain].append({
            "key": key,
            "name": example.get("dataset_name"),
            "description": example.get("description")
        })
    return domains


def normalize_column_name(col: str) -> str:
    """
    Normalize a column name for matching:
    - lowercase
    - remove accents (unicode NFKD decomposition)
    - replace spaces and separators with underscores
    """
    import unicodedata
    if col is None:
        return ""
    col = str(col).strip().lower()
    # Remove accents: decompose then drop combining marks
    col = unicodedata.normalize("NFKD", col)
    col = "".join(c for c in col if not unicodedata.combining(c))
    col = re.sub(r"[^\w]+", "_", col, flags=re.UNICODE)
    col = re.sub(r"_+", "_", col).strip("_")
    return col


def match_business_example(df_columns: List[str], examples: Dict[str, Dict[str, Any]] | None = None) -> List[Tuple[str, float]]:
    """Alias for match_business_examples (backward-compat)."""
    return match_business_examples(df_columns, examples)


def match_business_examples(df_columns: List[str], examples: Dict[str, Dict[str, Any]] | None = None) -> List[Tuple[str, float]]:
    """
    Score examples against df columns (normalized).
    Returns a list of (example_key, score) sorted by score desc.
    """
    examples = examples or BUSINESS_EXAMPLES
    cols = {normalize_column_name(c) for c in df_columns}

    scored: List[Tuple[str, float]] = []
    for key, example in examples.items():
        ex_cols = {normalize_column_name(c) for c in (example.get("columns") or {}).keys()}
        if not ex_cols:
            continue
        matches = len(cols & ex_cols)
        score = matches / len(ex_cols) if ex_cols else 0.0

        # bonus for synonyms if provided (v2)
        synonyms: Dict[str, List[str]] = example.get("column_synonyms") or {}
        if synonyms:
            syn_hits = 0
            for canonical, syns in synonyms.items():
                canonical_norm = normalize_column_name(canonical)
                all_terms = {canonical_norm} | {normalize_column_name(s) for s in syns}
                if cols.intersection(all_terms):
                    syn_hits += 1
            score = max(score, min(0.85, syn_hits / max(3, len(synonyms))))

        scored.append((key, float(score)))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored


def get_domain_assets(domain: str) -> Dict[str, Any]:
    """
    Aggregate optional v2 assets by domain.
    Useful for agent prompts / UI suggestions.
    """
    domain = (domain or "").lower()
    assets: Dict[str, Any] = {
        "typical_questions": [],
        "common_metrics": [],
        "recommended_charts": [],
        "quality_rules": [],
        "business_intents": {},
    }
    for _key, example in BUSINESS_EXAMPLES.items():
        if (example.get("domain") or "").lower() != domain:
            continue
        for k in ("typical_questions", "common_metrics", "recommended_charts", "quality_rules"):
            items = example.get(k) or []
            if isinstance(items, list):
                assets[k].extend(items)
        intents = example.get("business_intents") or {}
        if isinstance(intents, dict):
            assets["business_intents"].update(intents)

    # dedupe lists while preserving order
    for k in ("typical_questions", "common_metrics", "recommended_charts", "quality_rules"):
        seen = set()
        deduped = []
        for item in assets[k]:
            marker = str(item)
            if marker in seen:
                continue
            seen.add(marker)
            deduped.append(item)
        assets[k] = deduped

    return assets
