# ⚡ 5-Minute Quick Start - Nouveau Système de Design

Intégrez le nouveau système de design en **5 minutes maximum**.

---

## 🎯 Objectif
Ajouter un **dark mode dynamique** à votre app Streamlit avec un sélecteur de thème.

---

## ⚠️ IMPORTANT: Ordre Critique

`st.set_page_config()` DOIT être le PREMIER appel Streamlit, avant `init_theme_system()`!

---

## 📝 3 Étapes Seulement

### Étape 1: Modifier `app.py` (2 min)

Ouvrez `app.py` et ajoutez ce code **au tout début du fichier**:

```python
import streamlit as st
from components.theme_selector import init_theme_system

# 1️⃣ set_page_config() DOIT être le PREMIER appel Streamlit
st.set_page_config(page_title="Ma App", layout="wide")

# 2️⃣ PUIS initialiser le thème
init_theme_system()

# ... le reste de votre code commence après
```

⚠️ **Respectez l'ordre!**

### Étape 2: Ajouter le sélecteur (2 min)

Localisez le code de votre sidebar (cherchez `st.sidebar`), puis ajoutez:

```python
with st.sidebar:
    # ... votre code existant ...
    
    # Ajouter cette ligne (peut être n'importe où dans la sidebar)
    from components.theme_selector import render_theme_selector
    render_theme_selector()
```

### Étape 3: Tester (1 min)

```bash
streamlit run app.py
```

Allez à la sidebar et cliquez sur 🌙 ou ☀️ pour changer de thème!

---

## ✅ C'est Fait!

Votre app a maintenant:
- ✅ Dark mode dynamique
- ✅ Sélecteur light/dark/auto
- ✅ Changement instantané (0ms)
- ✅ Persistence en session

---

## 🎨 Utiliser dans votre code

Maintenant que le système est actif, vous pouvez commencer à l'utiliser:

### Récupérer les couleurs du thème actif

```python
from components.theme_manager import ThemeManager

colors = ThemeManager.get_colors()

# Utiliser une couleur
st.markdown(f"""
<p style='color: {colors['primary']}; font-size: 18px;'>
    Mon texte stylisé
</p>
""", unsafe_allow_html=True)
```

### Utiliser les composants réutilisables

```python
from components.reusable_components import render_card, render_badge, render_alert

# Rendre une carte
render_card(
    title="Mon Titre",
    content="Contenu de la carte"
)

# Rendre un badge
render_badge("En cours", variant="info")

# Rendre une alerte
render_alert("Succès!", alert_type="success")
```

---

## 🚀 Prochaines Étapes

Maintenant que c'est intégré, vous pouvez:

1. **Progressivement** migrer vos composants existants
2. **Lire** la documentation complète pour plus de détails
3. **Ajouter** de nouveaux tokens ou composants au besoin

### Pour plus de détails, lire:

- **[DESIGN_SYSTEM_GUIDE.md](DESIGN_SYSTEM_GUIDE.md)** - Guide complet (15 min)
- **[API_REFERENCE.md](API_REFERENCE.md)** - Référence des fonctions (Au besoin)
- **[INTEGRATION_CHECKLIST.md](INTEGRATION_CHECKLIST.md)** - Checklist d'intégration (Optionnel)

---

## 🎓 Exemple Complet (Minimal)

Voici un exemple minimal d'app avec le nouveau système:

```python
import streamlit as st
from components.theme_selector import init_theme_system, render_theme_selector
from components.theme_manager import ThemeManager
from components.reusable_components import render_card, render_badge, render_alert

# 1. Initialiser le thème au démarrage
init_theme_system()

# Configuration Streamlit
st.set_page_config(page_title="Ma App", layout="wide")

# 2. Ajouter sélecteur dans sidebar
with st.sidebar:
    st.markdown("## Paramètres")
    render_theme_selector()

# 3. Utiliser les couleurs du thème actif
st.title("🎨 Ma Super App")

colors = ThemeManager.get_colors()

st.markdown(f"""
<div style='
    background-color: {colors['bg_secondary']};
    padding: 20px;
    border-radius: 8px;
    color: {colors['text_primary']};
'>
    Bienvenue dans votre app avec dark mode! 🚀
</div>
""", unsafe_allow_html=True)

# 4. Utiliser les composants
col1, col2 = st.columns(2)

with col1:
    render_card(
        title="Fonctionnalité 1",
        content="Descripton de la fonctionnalité"
    )

with col2:
    render_badge("Nouveau", variant="info")
    render_alert("Tout fonctionne!", alert_type="success")
```

Exécutez avec: `streamlit run app.py`

---

## 📱 Vidéo de Démo

Ouvrez `pages/0_🎨_Design_Demo.py` pour voir une démo complète:

```bash
streamlit run pages/0_🎨_Design_Demo.py
```

---

## ❓ Problème?

### Le thème ne change pas
- ✅ Vérifiez que `init_theme_system()` est au **début** de `app.py`
- ✅ Vérifiez que le sélecteur est dans `st.sidebar`
- ✅ Relancez l'app complètement

### Les couleurs ne s'appliquent pas
- ✅ Vérifiez l'import: `from components.theme_manager import ThemeManager`
- ✅ Vérifiez que vous utilisez: `ThemeManager.get_color('couleur')`
- ✅ Vérifiez le markdown: `unsafe_allow_html=True`

### Composants non trouvés
- ✅ Vérifiez l'import: `from components.reusable_components import render_card`
- ✅ Vérifiez que `components/reusable_components.py` existe

---

## 🎯 Résumé

| Étape | Temps | Action |
|-------|-------|--------|
| 1 | 2 min | Ajouter `st.set_page_config()` puis `init_theme_system()` dans `app.py` |
| 2 | 2 min | Ajouter `render_theme_selector()` dans sidebar |
| 3 | 1 min | Tester avec `streamlit run app.py` |
| **Total** | **5 min** | ✅ Dark mode activé! |

---

## 🚀 Vous Êtes Prêt!

Commencez avec ces 3 lignes, puis explorez:

```python
import streamlit as st
from components.theme_selector import init_theme_system, render_theme_selector

# 1️⃣ FIRST: set_page_config
st.set_page_config(page_title="Ma App")

# 2️⃣ THEN: init_theme_system
init_theme_system()

# 3️⃣ Dans sidebar:
with st.sidebar:
    render_theme_selector()
```

---

## 📚 Ressources

- **Guide complet**: [DESIGN_SYSTEM_GUIDE.md](DESIGN_SYSTEM_GUIDE.md)
- **Référence API**: [API_REFERENCE.md](API_REFERENCE.md)
- **Vue d'ensemble**: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- **Navigation**: [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)

---

**C'est tout! Happy coding! 🎉**
