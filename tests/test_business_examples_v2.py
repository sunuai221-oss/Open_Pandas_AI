from core.business_examples import (
    get_all_business_examples,
    get_business_example,
    normalize_column_name,
    match_business_examples,
    get_domain_assets,
)


def test_business_examples_api_still_works():
    all_examples = get_all_business_examples()
    assert isinstance(all_examples, dict)
    assert "ecommerce_orders" in all_examples

    ex = get_business_example("ecommerce_orders")
    assert ex is not None
    assert ex.get("domain") == "ecommerce"
    assert "columns" in ex


def test_normalize_column_name_is_stable():
    assert normalize_column_name(" Order Date ") == "order_date"
    assert normalize_column_name("unit_price/usd") == "unit_price_usd"


def test_match_business_examples_scores_and_returns_sorted():
    cols = ["order_id", "customer_id", "amount", "order_date", "status"]
    scored = match_business_examples(cols)
    assert scored
    assert scored[0][1] >= scored[-1][1]


def test_get_domain_assets_returns_optional_fields():
    assets = get_domain_assets("ecommerce")
    assert isinstance(assets, dict)
    assert "typical_questions" in assets
    assert "common_metrics" in assets

