from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional, Set, Tuple

import pandas as pd

from core.business_examples import get_all_business_examples, get_business_example, normalize_column_name
from core.smart_dictionary_detector import SmartDictionaryDetector


@dataclass(frozen=True)
class DetectionResult:
    domain: str
    confidence: float
    reasons: List[str]
    matched_columns: List[str]
    suggested_agent: str
    matched_example_key: Optional[str] = None


_DOMAIN_SIGNATURES: Dict[str, Set[str]] = {
    "finance": {"transaction_id", "amount", "account", "balance", "category", "date"},
    "hr": {"employee_id", "salary", "hire_date", "department", "job_title", "status"},
    "ecommerce": {"order_id", "product_id", "price", "stock", "customer_id", "order_date", "qty", "amount"},
    "crm": {"lead_id", "account_id", "stage", "company", "created_date", "source"},
}

# Patterns indicative of specific domains (for dtype/value heuristics)
_CURRENCY_LIKE_COLS = {"amount", "price", "total", "cost", "revenue", "profit", "fee", "salary", "balance", "budget"}
_DATE_LIKE_COLS = {"date", "created_at", "updated_at", "timestamp", "hire_date", "order_date", "created_date", "birth_date", "start_date", "end_date"}
_QTY_LIKE_COLS = {"qty", "quantity", "stock", "count", "units", "items"}


def _normalized_columns(df: pd.DataFrame) -> List[str]:
    return [normalize_column_name(str(c)) for c in df.columns]


def _fuzzy_match(target: str, candidates: Set[str], threshold: float = 0.80) -> Optional[str]:
    """Return candidate with best fuzzy ratio >= threshold, else None."""
    best: Optional[str] = None
    best_ratio = threshold
    for c in candidates:
        ratio = SequenceMatcher(None, target, c).ratio()
        if ratio >= best_ratio:
            best_ratio = ratio
            best = c
    return best


def _signature_score(domain: str, cols: Set[str]) -> Tuple[float, List[str], List[str]]:
    sig = _DOMAIN_SIGNATURES.get(domain, set())
    if not sig:
        return 0.0, [], []
    # Exact + fuzzy matching against signature columns
    matched: List[str] = []
    for s in sig:
        if s in cols:
            matched.append(s)
        else:
            fuzzy = _fuzzy_match(s, cols, 0.80)
            if fuzzy:
                matched.append(fuzzy)
    matched = sorted(set(matched))
    if not matched:
        return 0.0, [], []
    if len(matched) < 2:
        date_like_matches = [
            col
            for col in matched
            if (
                normalize_column_name(col) in _DATE_LIKE_COLS
                or _fuzzy_match(normalize_column_name(col), _DATE_LIKE_COLS, 0.80)
            )
        ]
        if len(date_like_matches) == len(matched):
            return 0.0, [], []
    # score is ratio of matched signature columns, capped to avoid overpowering business-example match
    score = min(0.85, len(matched) / max(4, len(sig)))
    reasons = [f"Signature columns matched for {domain}: {', '.join(matched[:8])}"]
    return score, reasons, matched


def _type_signal_score(df: pd.DataFrame, cols_set: Set[str]) -> Tuple[float, List[str], str]:
    """
    Heuristics based on column dtypes / values:
    - date-like columns -> generic/hr/finance/ecommerce (bump any)
    - currency-like (numeric + naming) -> finance/ecommerce
    - quantity-like -> ecommerce
    Returns (score_boost, reasons, suggested_domain_hint)
    """
    reasons: List[str] = []
    hints: Dict[str, int] = {"finance": 0, "ecommerce": 0, "hr": 0, "crm": 0}

    for col in df.columns:
        norm = normalize_column_name(str(col))
        dtype = df[col].dtype

        # Date detection
        if pd.api.types.is_datetime64_any_dtype(dtype):
            reasons.append(f"Column '{col}' is datetime")
            if norm in {"hire_date", "birth_date"}:
                hints["hr"] += 1
            elif norm in {"order_date", "created_date"}:
                hints["ecommerce"] += 1
            else:
                hints["finance"] += 1
        elif norm in _DATE_LIKE_COLS or _fuzzy_match(norm, _DATE_LIKE_COLS, 0.80):
            # attempt parse
            try:
                parsed = pd.to_datetime(df[col].dropna().head(20), errors="coerce")
                if parsed.notna().sum() >= 10:
                    reasons.append(f"Column '{col}' looks date-like")
                    hints["finance"] += 1
            except Exception:
                pass

        # Numeric + currency-like naming
        if pd.api.types.is_numeric_dtype(dtype):
            if norm in _CURRENCY_LIKE_COLS or _fuzzy_match(norm, _CURRENCY_LIKE_COLS, 0.80):
                reasons.append(f"Column '{col}' is numeric currency-like")
                hints["finance"] += 1
                hints["ecommerce"] += 1
            if norm in _QTY_LIKE_COLS or _fuzzy_match(norm, _QTY_LIKE_COLS, 0.80):
                reasons.append(f"Column '{col}' is quantity-like")
                hints["ecommerce"] += 1

    if not hints or max(hints.values()) == 0:
        return 0.0, [], "generic"

    best_domain = max(hints, key=lambda k: hints[k])
    score = min(0.3, hints[best_domain] * 0.07)  # small boost, max 0.3
    return score, reasons[:4], best_domain


def _synonym_match_score(cols: Set[str]) -> Tuple[float, List[str], List[str], Optional[str]]:
    """
    Use Business Examples v2 optional `column_synonyms` to match columns and infer the best example.
    Returns: (score, reasons, matched_columns, matched_example_key)
    """
    best_key: Optional[str] = None
    best_score = 0.0
    best_matches: List[str] = []
    best_reasons: List[str] = []

    examples = get_all_business_examples()
    for example_key, example in examples.items():
        synonyms: Dict[str, List[str]] = example.get("column_synonyms") or {}
        if not synonyms:
            continue
        matched: List[str] = []
        for canonical, syns in synonyms.items():
            canonical_norm = normalize_column_name(canonical)
            all_terms = {canonical_norm} | {normalize_column_name(s) for s in syns}
            if cols.intersection(all_terms):
                matched.append(canonical_norm)
        if not matched:
            continue
        score = min(0.8, len(matched) / max(3, len(synonyms)))
        if score > best_score:
            best_score = score
            best_key = example_key
            best_matches = sorted(set(matched))
            best_reasons = [f"Synonym matches against example '{example_key}': {', '.join(best_matches[:8])}"]

    return best_score, best_reasons, best_matches, best_key


def detect_domain(df: pd.DataFrame) -> DetectionResult:
    """
    Hybrid detector:
    1) Reuse SmartDictionaryDetector.detect(df) to find a best business example match (if any)
    2) Enrich with synonym matching (Business Examples v2)
    3) Enrich with domain signature columns (exact + fuzzy)
    4) Enrich with dtype/value heuristics (date-like, currency-like, quantity-like)
    """
    cols_list = _normalized_columns(df)
    cols_set = set(cols_list)

    reasons: List[str] = []
    matched_columns: List[str] = []

    # 1) SmartDictionaryDetector base match
    example_key, _dictionary, base_conf = SmartDictionaryDetector.detect(df)
    base_domain: Optional[str] = None
    if example_key:
        ex = get_business_example(example_key) or {}
        base_domain = ex.get("domain") or None
        if base_domain:
            reasons.append(f"Matched business example '{example_key}' (domain={base_domain}, score={base_conf:.2f})")

    # 2) Synonym matching (v2) with minimal gating to avoid single-hit overrides
    syn_score, syn_reasons, syn_matched, syn_key = _synonym_match_score(cols_set)
    min_syn_hits = 2
    min_syn_score = 0.45
    use_synonyms = syn_key and (len(syn_matched) >= min_syn_hits or syn_score >= min_syn_score)
    if use_synonyms:
        reasons.extend(syn_reasons)
        matched_columns.extend(syn_matched)

    domain_candidates: List[Tuple[str, float]] = []
    if base_domain:
        domain_candidates.append((base_domain, base_conf))
    if use_synonyms:
        syn_domain = (get_business_example(syn_key) or {}).get("domain") or None
        if syn_domain:
            domain_candidates.append((syn_domain, syn_score))

    # 3) Signature columns (exact + fuzzy)
    sig_best_domain = "generic"
    sig_best_score = 0.0
    sig_best_reasons: List[str] = []
    sig_best_cols: List[str] = []
    for domain in _DOMAIN_SIGNATURES.keys():
        sig_score, sig_reasons, sig_cols = _signature_score(domain, cols_set)
        if sig_score > sig_best_score:
            sig_best_score = sig_score
            sig_best_domain = domain
            sig_best_reasons = sig_reasons
            sig_best_cols = sig_cols

    if sig_best_score > 0:
        reasons.extend(sig_best_reasons)
        matched_columns.extend(sig_best_cols)
        domain_candidates.append((sig_best_domain, sig_best_score))

    # 4) Dtype/value heuristics (date-like, currency-like, qty-like)
    type_boost, type_reasons, type_hint = _type_signal_score(df, cols_set)
    if type_boost > 0:
        reasons.extend(type_reasons)
        # Add as low-priority candidate (or boost existing)
        domain_candidates.append((type_hint, type_boost))

    # Determine winner
    if domain_candidates:
        # Aggregate scores per domain (sum)
        domain_scores: Dict[str, float] = {}
        for d, s in domain_candidates:
            domain_scores[d] = domain_scores.get(d, 0.0) + s
        # pick best by aggregated score
        best_domain = max(domain_scores, key=lambda k: domain_scores[k])
        confidence = min(0.95, domain_scores[best_domain])
        domain = best_domain
    else:
        domain = "generic"
        confidence = 0.3
        reasons.append("No strong match found; using generic agent.")

    # Slightly bump confidence if multiple signals agree on same domain
    agreeing = [d for d, _s in domain_candidates if d == domain]
    if len(agreeing) >= 2:
        confidence = min(0.98, confidence + 0.08)
        if "Multiple signals agree on the same domain." not in reasons:
            reasons.append("Multiple signals agree on the same domain.")

    matched_columns = sorted(set(matched_columns))
    suggested_agent = domain if domain in _DOMAIN_SIGNATURES or domain in ("crm", "hr", "finance", "ecommerce") else "generic"

    return DetectionResult(
        domain=domain,
        confidence=round(confidence, 2),
        reasons=reasons[:6],
        matched_columns=matched_columns[:20],
        suggested_agent=suggested_agent,
        matched_example_key=example_key or syn_key,
    )

