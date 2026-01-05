import pandas as pd

from core import utils


def test_calculate_age_default_reference_date():
    assert utils.calculate_age("2000-05-31") == 25


def test_calculate_days_between():
    assert utils.calculate_days_between("2024-01-01", "2024-01-31") == 30


def test_anonymize_phone_masks_all_but_last_four():
    assert utils.anonymize_phone("0123456789") == "******6789"


def test_format_currency_localised():
    assert utils.format_currency(1234.5, "EUR") == "1 234,50 EUR"


def test_valid_female_percentage_over_group():
    group = pd.DataFrame(
        {
            "Sex": ["Female", "Female", "Male"],
            "Valid_Email": [True, False, True],
        }
    )
    assert utils.valid_female_percentage(group) == 50.0


def test_top_3_jobs_under_30_returns_ordered_list():
    group = pd.DataFrame(
        {
            "Age": [25, 27, 35, 21, 19],
            "Job Title": ["Data Scientist", "Data Scientist", "Analyst", "Engineer", "Engineer"],
        }
    )
    assert utils.top_3_jobs_under_30(group) == ["Data Scientist", "Engineer"]
