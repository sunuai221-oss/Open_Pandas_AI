# 🎨 Guide d'Intégration - Nouveau Système de Design

Ce guide explique comment intégrer le nouveau système de design dans votre application Streamlit.

## Architecture mise en place

```
components/
├── design_tokens.py          # Système centralisé (couleurs, spacing, typographie)
├── theme_manager.py          # Gestionnaire de thème avec context Streamlit
├── css_generator.py          # Génération dynamique de CSS à partir des tokens
├── reusable_components.py    # Composants UI réutilisables (cards, buttons, etc.)
├── theme_selector.py         # Widget de sélection de thème pour sidebar
└── styles.py                 # (À refactoriser progressivement)
```

---

## ✅ Quick Start (15 minutes)

### Étape 1: Initialiser le système de thème dans app.py

```python
# app.py
import streamlit as st
from components.theme_selector import init_theme_system

# IMPORTANT: set_page_config() DOIT être le PREMIER appel Streamlit
st.set_page_config(page_title="Ma App", layout="wide")

# PUIS initialiser le système de thème
init_theme_system()

# ... le reste de votre code
```

⚠️ **ORDRE CRITIQUE:** `st.set_page_config()` → `init_theme_system()` → Reste

**C'est tout !** Le thème dark mode est maintenant actif avec support du switching.

---

## 📊 Utiliser les Design Tokens

### Dans du code Python

```python
from components.theme_manager import ThemeManager

# Récupérer toutes les couleurs du thème actuel
colors = ThemeManager.get_colors()
print(colors['primary'])          # #60a5fa (dark) ou #2563eb (light)

# Récupérer une couleur spécifique
primary_color = ThemeManager.get_color('primary')

# Vérifier le thème actif
if ThemeManager.is_dark():
    print("Mode sombre actif")
```

### Dans du HTML/Markdown

```python
colors = ThemeManager.get_colors()

st.markdown(f"""
<div style='color: {colors['text_primary']}; 
            background-color: {colors['bg_secondary']}; 
            padding: 16px;
            border-radius: 8px;'>
    Mon contenu stylisé
</div>
""", unsafe_allow_html=True)
```

---

## 🧩 Utiliser les Composants Réutilisables

Remplacez le HTML brut par des fonctions Python propres et maintenables.

### Cartes

```python
from components.reusable_components import render_card

render_card(
    title="Mon Titre",
    content="Contenu de la carte",
    footer="Note de bas",
    expandable=False
)
```

### Statistiques

```python
from components.reusable_components import render_stat_card, render_metric_row

# Carte unique
render_stat_card(
    label="Revenue",
    value="$12,345",
    unit="",
    change=5.2,
    trend="up"
)

# Ligne de métriques
render_metric_row([
    {'label': 'Total Users', 'value': '1,234'},
    {'label': 'Active Sessions', 'value': '567'},
    {'label': 'Bounce Rate', 'value': '32.5', 'unit': '%'},
])
```

### Boutons et Groupes

```python
from components.reusable_components import render_button_group

buttons = [
    {'label': 'Enregistrer', 'key': 'save', 'icon': '💾'},
    {'label': 'Annuler', 'key': 'cancel', 'icon': '✕'},
]

def handle_button_click(key):
    print(f"Bouton cliqué: {key}")

render_button_group(buttons, on_click_callback=handle_button_click)
```

### Alertes

```python
from components.reusable_components import render_alert

render_alert("Succès!", alert_type="success")
render_alert("Attention!", alert_type="warning")
render_alert("Erreur!", alert_type="error")
render_alert("Information", alert_type="info")
```

### Badges

```python
from components.reusable_components import render_badge

render_badge("En cours", variant="info")
render_badge("Validé", variant="success")
render_badge("Attention", variant="warning")
render_badge("Erreur", variant="error")
```

### Boîtes d'Information

```python
from components.reusable_components import render_info_box

render_info_box(
    title="Conseil",
    content="Utilisez des mots clés pertinents pour de meilleurs résultats.",
    icon="💡",
    variant="tip"
)
```

---

## 🎯 Sélecteur de Thème dans la Sidebar

```python
# dans votre sidebar
from components.theme_selector import render_theme_selector

with st.sidebar:
    st.markdown("## ⚙️ Paramètres")
    render_theme_selector()
```

Cela affiche:
- Dropdown pour sélectionner Auto/Light/Dark
- Boutons rapides 🌙/☀️
- Indicator du thème actif

---

## 🔄 Migration Progressive

Au lieu de refactoriser d'un coup, vous pouvez migrer progressivement:

### Avant (ancien code)

```python
# components/chat_interface.py
def render_chat_message(message, is_user=False):
    st.markdown(f"""
    <div style='background-color: {"#e3f2fd" if is_user else "#f5f5f5"}; 
                padding: 12px 16px; 
                border-radius: 8px; 
                margin: 8px 0;'>
        {message}
    </div>
    """, unsafe_allow_html=True)
```

### Après (nouveau code)

```python
# components/chat_interface.py
from components.theme_manager import ThemeManager

def render_chat_message(message, is_user=False):
    colors = ThemeManager.get_colors()
    bg_color = colors['primary_light'] if is_user else colors['bg_secondary']
    
    st.markdown(f"""
    <div style='background-color: {bg_color}; 
                padding: 12px 16px; 
                border-radius: 8px; 
                margin: 8px 0;
                color: {colors["text_primary"]};'>
        {message}
    </div>
    """, unsafe_allow_html=True)
```

**Avantages:**
- ✅ Support automatique light/dark
- ✅ Cohérence visuelle garantie
- ✅ Changement de couleur centralisé

---

## 🎨 Customiser les Couleurs

Modifiez directement `components/design_tokens.py`:

```python
DESIGN_TOKENS = {
    "colors": {
        "dark": {
            "primary": "#60a5fa",      # ← Modifier ici
            "bg_primary": "#020617",   # ← Ou ici
            ...
        },
        "light": {
            ...
        }
    }
}
```

**Ensuite:**
1. Tous les composants se mettront à jour automatiquement
2. Le CSS sera régénéré dynamiquement
3. Pas besoin de recompiler ou redémarrer

---

## 📱 Ajouter de nouvelles Couleurs

1. Ouvrez `components/design_tokens.py`
2. Ajoutez la couleur dans `DESIGN_TOKENS["colors"]["light"]` et `["dark"]`
3. Utilisez-la partout via `ThemeManager.get_color('new_color')`

Exemple:
```python
# design_tokens.py
"colors": {
    "dark": {
        "accent_purple": "#a78bfa",  # ← Nouvelle couleur
    },
    "light": {
        "accent_purple": "#7c3aed",
    }
}

# Votre code
accent = ThemeManager.get_color('accent_purple')
```

---

## 🧪 Tester le Thème

Naviguez vers une page quelconque et:

1. Ouvrez la sidebar
2. Cliquez sur le sélecteur de thème 🎨
3. Testez Light/Dark/Auto
4. L'interface devrait se mettre à jour instantanément

**Pour un aperçu complet des couleurs:**

```python
from components.theme_selector import render_theme_preview

render_theme_preview()
```

---

## 📊 Vérifier la Couverture CSS

Les éléments Streamlit suivants sont stylisés:
- ✅ Boutons
- ✅ Text inputs & textareas
- ✅ Selectbox & multiselect
- ✅ Expanders
- ✅ Tabs
- ✅ Dataframes
- ✅ Alerts (success, warning, error, info)
- ✅ Code blocks
- ✅ Spinners
- ✅ Metrics

Si vous trouvez des éléments non stylisés, ajoutez les sélecteurs correspondants dans `components/css_generator.py` → `generate_streamlit_overrides()`.

---

## 🚀 Points Clés

| Ancien Système | Nouveau Système |
|---|---|
| CSS brut avec `!important` | CSS généré depuis tokens |
| Couleurs codées en dur | `ThemeManager.get_color()` |
| Pas de dark mode dynamique | Switching light/dark en temps réel |
| Duplication HTML | Composants réutilisables |
| Refactorisation compliquée | Modifications centralisées |

---

## 📚 Fichiers de Référence

- **design_tokens.py** - Source unique de vérité pour les couleurs
- **theme_manager.py** - API pour accéder au thème actif
- **css_generator.py** - Génération CSS dynamique
- **reusable_components.py** - Librairie de composants
- **theme_selector.py** - Widget de sélection

---

## ❓ FAQ

**Q: Pourquoi ma couleur personnalisée ne s'applique pas?**
A: Assurez-vous que `init_theme_system()` est appelé AU DÉBUT de `app.py`, avant tout rendu.

**Q: Comment forcer le thème dark au démarrage?**
A: Modifiez `init_theme_system()`:
```python
ThemeManager.init_theme(ThemeManager.THEME_DARK)
```

**Q: Les changements de couleur ne sont pas instantanés?**
A: Utilisez `st.rerun()` après avoir changé le thème (voir `theme_selector.py`).

**Q: Je peux mélanger ancien et nouveau système?**
A: Oui, pendant la migration. Les deux peuvent coexister.

---

Besoin d'aide? Consultez les fichiers source pour plus de détails! 🚀
