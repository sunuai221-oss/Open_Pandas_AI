from datetime import datetime
import re

def calculate_age(birth_date_str, current_date_str="2025-05-31", fmt="%Y-%m-%d"):
    birth_date = datetime.strptime(birth_date_str, fmt)
    current_date = datetime.strptime(current_date_str, fmt)
    age = current_date.year - birth_date.year - ((current_date.month, current_date.day) < (birth_date.month, birth_date.day))
    return age

def calculate_days_between(date1_str, date2_str, fmt="%Y-%m-%d"):
    d1 = datetime.strptime(date1_str, fmt)
    d2 = datetime.strptime(date2_str, fmt)
    return abs((d2 - d1).days)

def extract_year(date_str, fmt="%Y-%m-%d"):
    return datetime.strptime(date_str, fmt).year

def is_valid_email(email):
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", str(email)))

def anonymize_phone(phone):
    phone = str(phone)
    if len(phone) <= 4:
        return "*" * len(phone)
    return "*" * (len(phone)-4) + phone[-4:]

def get_country_code(country_name):
    country_codes = {
        "France": "FR", "Germany": "DE", "Korea": "KR", "Nigeria": "NG",
        "United Kingdom": "GB", "Tunisia": "TN", "Indonesia": "ID",
        "Slovenia": "SI", "Nicaragua": "NI", "Congo": "CG"
    }
    return country_codes.get(country_name, "")

def format_currency(amount, currency="€"):
    try:
        amount = float(amount)
        return f"{amount:,.2f} {currency}".replace(",", " ").replace(".", ",")
    except:
        return str(amount)

def round_to(value, decimals=2):
    try:
        return round(float(value), decimals)
    except:
        return value

def age_category(age):
    try:
        age = int(age)
        if age < 18:
            return "Enfant"
        elif age < 65:
            return "Adulte"
        else:
            return "Senior"
    except:
        return "N/A"

def tenure_years(hire_date_str, end_date_str="2025-05-31", fmt="%Y-%m-%d"):
    start = datetime.strptime(hire_date_str, fmt)
    end = datetime.strptime(end_date_str, fmt)
    return end.year - start.year - ((end.month, end.day) < (start.month, start.day))

# ---- FONCTIONS AVANCÉES POUR GROUPBY MULTI-COLONNES ----

def valid_female_percentage(group):
    females = group[group['Sex'] == 'Female']
    if len(females) == 0:
        return 0
    return females['Valid_Email'].sum() / len(females) * 100

def average_age_plus1(group):
    sub = group[group['Phone'].astype(str).str.startswith('+1')]
    return sub['Age'].mean() if len(sub) > 0 else None

def top_3_jobs_under_30(group):
    jobs = group[group['Age'] < 30]['Job Title']
    return jobs.value_counts().head(3).index.tolist()

# ---- PATTERNS ROBUSTES PROPORTION & AGG ----

def female_percentage(s):
    """Renvoie le pourcentage de femmes dans une Series Sex."""
    return (s == 'Female').mean() * 100

def valid_email_percentage(s):
    """Renvoie le pourcentage d’emails valides dans une Series booléenne."""
    return s.mean() * 100

def _mean_age_by_sex(series, sex_value):
    parent_df = globals().get("df")
    if parent_df is not None and hasattr(parent_df, "columns") and "Sex" in parent_df.columns:
        try:
            mask = parent_df.loc[series.index, "Sex"] == sex_value
            return series[mask].mean()
        except Exception:
            return None
    if hasattr(series, "columns") and "Sex" in series.columns and "Age" in series.columns:
        try:
            return series[series["Sex"] == sex_value]["Age"].mean()
        except Exception:
            return None
    return None

def mean_age_females(s):
    """Mean age for female rows when a parent df with Sex is available."""
    return _mean_age_by_sex(s, "Female")

def mean_age_males(s):
    """Mean age for male rows when a parent df with Sex is available."""
    return _mean_age_by_sex(s, "Male")
