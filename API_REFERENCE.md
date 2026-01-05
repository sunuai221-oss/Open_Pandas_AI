# 📚 Référence API - Nouveau Système de Design

Guide complet des APIs et fonctions du nouveau système de design.

---

## 📦 Module: `design_tokens.py`

Source unique de vérité pour tous les tokens de design.

### 🎨 Dictionnaire Principal: `DESIGN_TOKENS`

```python
DESIGN_TOKENS = {
    "colors": {
        "light": {...},
        "dark": {...}
    },
    "spacing": {...},
    "typography": {...},
    "radii": {...},
    "shadows": {...},
    "z_index": {...},
    "transitions": {...},
}
```

### 🔧 Fonctions Utilitaires

#### `get_color(color_key: str, theme: str) -> str`

Récupère une couleur spécifique.

```python
from components.design_tokens import get_color

primary = get_color('primary', 'dark')  # "#60a5fa"
```

**Paramètres:**
- `color_key` (str): Clé de la couleur (ex: 'primary', 'bg_secondary')
- `theme` (str): 'light' ou 'dark'

**Retour:** Code couleur hex (str)

---

#### `get_spacing(spacing_key: str) -> str`

Récupère une valeur d'espacement.

```python
from components.design_tokens import get_spacing

padding = get_spacing('lg')  # "16px"
```

**Paramètres:**
- `spacing_key` (str): 'xs', 'sm', 'md', 'lg', 'xl', '2xl', '3xl'

**Retour:** Valeur CSS (str)

---

#### `get_font_size(size_key: str) -> str`

Récupère une taille de police.

```python
from components.design_tokens import get_font_size

font = get_font_size('lg')  # "18px"
```

**Paramètres:**
- `size_key` (str): 'xs', 'sm', 'base', 'lg', 'xl', '2xl', '3xl'

**Retour:** Taille CSS (str)

---

#### `get_radius(radius_key: str) -> str`

Récupère un rayon border-radius.

```python
from components.design_tokens import get_radius

border_radius = get_radius('md')  # "8px"
```

**Paramètres:**
- `radius_key` (str): 'none', 'sm', 'md', 'lg', 'xl', 'full'

**Retour:** Rayon CSS (str)

---

#### `get_all_colors(theme: str) -> dict`

Récupère toute la palette pour un thème.

```python
from components.design_tokens import get_all_colors

dark_colors = get_all_colors('dark')
# {'primary': '#60a5fa', 'bg_primary': '#020617', ...}
```

**Paramètres:**
- `theme` (str): 'light' ou 'dark'

**Retour:** Dict de toutes les couleurs

---

## 🎭 Module: `theme_manager.py`

Gestion centralisée du thème avec support Streamlit.

### 🏛️ Classe: `ThemeManager`

Gestionnaire singleton pour le thème actif.

#### Constants

```python
THEME_AUTO = "auto"    # Mode auto (détection système)
THEME_LIGHT = "light"  # Mode clair
THEME_DARK = "dark"    # Mode sombre

VALID_MODES = [THEME_AUTO, THEME_LIGHT, THEME_DARK]
```

#### `init_theme(default_mode: str = THEME_AUTO)`

Initialise le thème en session_state.

```python
from components.theme_manager import ThemeManager

ThemeManager.init_theme(ThemeManager.THEME_DARK)
```

⚠️ **À appeler une seule fois au démarrage de l'app.**

**Paramètres:**
- `default_mode` (str): Mode initial

---

#### `get_mode() -> str`

Récupère le mode de thème actuel.

```python
mode = ThemeManager.get_mode()  # "dark" ou "light" ou "auto"
```

**Retour:** Mode ('auto', 'light', 'dark')

---

#### `set_mode(mode: str)`

Définit le mode de thème.

```python
ThemeManager.set_mode(ThemeManager.THEME_DARK)
```

**Paramètres:**
- `mode` (str): Mode à appliquer

**Raises:** ValueError si mode invalide

---

#### `get_current_theme() -> str`

Récupère le thème réel actif (light ou dark).

```python
theme = ThemeManager.get_current_theme()  # "dark" ou "light"
```

**Retour:** 'light' ou 'dark'

---

#### `is_dark() -> bool`

Retourne True si mode sombre actif.

```python
if ThemeManager.is_dark():
    print("Dark mode!")
```

**Retour:** bool

---

#### `is_light() -> bool`

Retourne True si mode clair actif.

```python
if ThemeManager.is_light():
    print("Light mode!")
```

**Retour:** bool

---

#### `toggle_theme()`

Bascule entre light et dark.

```python
ThemeManager.toggle_theme()  # dark → light ou light → dark
```

---

#### `get_colors() -> dict`

Récupère la palette pour le thème actuel.

```python
colors = ThemeManager.get_colors()
primary = colors['primary']  # Couleur dynamique
```

**Retour:** Dict de couleurs

---

#### `get_color(color_key: str) -> str`

Récupère une couleur pour le thème actuel.

```python
primary = ThemeManager.get_color('primary')
```

**Paramètres:**
- `color_key` (str): Clé de la couleur

**Retour:** Code couleur hex

---

### 🔗 Instance Globale

```python
from components.theme_manager import theme

# Utilisation courte
theme.is_dark()
theme.get_color('primary')
```

---

## 🎨 Module: `css_generator.py`

Génération dynamique de CSS à partir des tokens.

### 🔧 Fonctions

#### `generate_css_variables(theme: str = "dark") -> str`

Génère les variables CSS pour un thème.

```python
from components.css_generator import generate_css_variables

css_vars = generate_css_variables('dark')
# ":root { --color-primary: #60a5fa; ... }"
```

**Retour:** Bloc CSS :root

---

#### `generate_base_styles() -> str`

Génère les styles de base réutilisables.

```python
from components.css_generator import generate_base_styles

styles = generate_base_styles()
# Contient .card, .button, .input, etc.
```

**Retour:** Bloc CSS complet

---

#### `generate_streamlit_overrides() -> str`

Génère les overrides pour éléments Streamlit.

```python
from components.css_generator import generate_streamlit_overrides

overrides = generate_streamlit_overrides()
# Override .stButton, .stTextInput, etc.
```

**Retour:** Bloc CSS pour Streamlit

---

#### `generate_complete_css(theme: str = "dark") -> str`

Génère l'intégralité du CSS pour un thème.

```python
from components.css_generator import generate_complete_css

css = generate_complete_css('dark')
# CSS complet prêt pour injection
```

**Retour:** CSS complet

---

#### `inject_custom_css(theme: str = "dark")`

Injecte le CSS dans Streamlit via `st.markdown()`.

```python
from components.css_generator import inject_custom_css

inject_custom_css('dark')
```

⚠️ **À appeler au démarrage de l'app.**

---

## 🧩 Module: `reusable_components.py`

Composants UI réutilisables construits avec design tokens.

### 📦 Composants

#### `render_card(title, content, footer, expandable, key, css_class)`

Rend une carte réutilisable.

```python
from components.reusable_components import render_card

render_card(
    title="Mon Titre",
    content="Contenu de la carte",
    footer="Note de bas",
    expandable=False
)
```

**Paramètres:**
- `title` (str, opt): Titre de la carte
- `content` (str, opt): Contenu principal
- `footer` (str, opt): Bas de la carte
- `expandable` (bool): Si True, utilise st.expander
- `key` (str, opt): Clé unique Streamlit
- `css_class` (str): Classes CSS additionnelles

---

#### `render_button_group(buttons, on_click_callback, orientation)`

Rend un groupe de boutons.

```python
from components.reusable_components import render_button_group

buttons = [
    {'label': 'Enregistrer', 'key': 'save', 'icon': '💾'},
    {'label': 'Annuler', 'key': 'cancel', 'icon': '✕'},
]

def callback(key):
    print(f"Bouton {key} cliqué")

render_button_group(buttons, on_click_callback=callback)
```

**Paramètres:**
- `buttons` (list): Liste de dict {'label', 'key', 'icon' (opt)}
- `on_click_callback` (callable, opt): Fonction appelée au clic
- `orientation` (str): 'horizontal' ou 'vertical'

---

#### `render_stat_card(label, value, unit, change, trend)`

Rend une carte de statistique.

```python
from components.reusable_components import render_stat_card

render_stat_card(
    label="Revenue",
    value="€45,230",
    unit="",
    change=12.5,
    trend="up"
)
```

**Paramètres:**
- `label` (str): Libellé
- `value` (str): Valeur à afficher
- `unit` (str, opt): Unité (ex: '%', '€')
- `change` (float, opt): Changement (ex: 5.2)
- `trend` (str, opt): 'up', 'down', 'neutral'

---

#### `render_badge(label, variant, size)`

Rend un badge/tag.

```python
from components.reusable_components import render_badge

render_badge("En cours", variant="info")
render_badge("Validé", variant="success", size="lg")
```

**Paramètres:**
- `label` (str): Texte du badge
- `variant` (str): 'primary', 'success', 'warning', 'error', 'info'
- `size` (str): 'sm', 'md', 'lg'

---

#### `render_alert(message, alert_type, dismissible, key)`

Rend une alerte personnalisée.

```python
from components.reusable_components import render_alert

render_alert("Succès!", alert_type="success")
render_alert("⚠️ Attention!", alert_type="warning")
```

**Paramètres:**
- `message` (str): Texte du message
- `alert_type` (str): 'info', 'success', 'warning', 'error'
- `dismissible` (bool): Si True, peut être fermée
- `key` (str, opt): Clé unique

---

#### `render_divider()`

Rend un séparateur.

```python
from components.reusable_components import render_divider

render_divider()
```

---

#### `render_section_header(title, subtitle, icon)`

Rend un en-tête de section.

```python
from components.reusable_components import render_section_header

render_section_header(
    title="Résultats",
    subtitle="Analyse complète",
    icon="📊"
)
```

**Paramètres:**
- `title` (str): Titre principal
- `subtitle` (str, opt): Sous-titre
- `icon` (str, opt): Emoji ou icône

---

#### `render_info_box(title, content, icon, variant)`

Rend une boîte d'information.

```python
from components.reusable_components import render_info_box

render_info_box(
    title="Conseil",
    content="Utilisez des mots clés pertinents.",
    icon="💡",
    variant="tip"
)
```

**Paramètres:**
- `title` (str): Titre
- `content` (str): Contenu
- `icon` (str, opt): Icône
- `variant` (str): 'info', 'tip', 'note', 'warning'

---

#### `render_metric_row(metrics)`

Rend une ligne de métriques côte à côte.

```python
from components.reusable_components import render_metric_row

render_metric_row([
    {'label': 'Total Users', 'value': '1,234'},
    {'label': 'Actifs', 'value': '567'},
    {'label': 'Conversion', 'value': '32.5', 'unit': '%'},
])
```

**Paramètres:**
- `metrics` (list): List de dict {'label', 'value', 'unit' (opt), 'change' (opt), 'trend' (opt)}

---

## 🎯 Module: `theme_selector.py`

Widget interactif pour changer de thème.

### 🔧 Fonctions

#### `render_theme_selector()`

Rend le sélecteur de thème dans la sidebar.

```python
from components.theme_selector import render_theme_selector

with st.sidebar:
    render_theme_selector()
```

Affiche:
- Dropdown (Auto/Light/Dark)
- Boutons rapides 🌙/☀️
- Indicator du thème actif

---

#### `render_theme_preview()`

Rend un aperçu complet des couleurs et composants.

```python
from components.theme_selector import render_theme_preview

render_theme_preview()
```

Utile pour développement et tests.

---

#### `init_theme_system()`

Initialise le système de thème au démarrage.

```python
from components.theme_selector import init_theme_system

# À appeler dans app.py
init_theme_system()
```

⚠️ **À appeler une seule fois, au DÉBUT du fichier principal.**

---

## 💡 Patterns Courants

### Pattern 1: Récupérer et utiliser une couleur

```python
from components.theme_manager import ThemeManager

colors = ThemeManager.get_colors()
primary_color = colors['primary']

st.markdown(f"""
<div style='color: {primary_color};'>
    Mon texte
</div>
""", unsafe_allow_html=True)
```

### Pattern 2: Créer un composant avec tokens

```python
from components.theme_manager import ThemeManager
from components.design_tokens import get_spacing, get_radius

colors = ThemeManager.get_colors()
padding = get_spacing('lg')
radius = get_radius('md')

st.markdown(f"""
<div style='
    background-color: {colors['bg_secondary']};
    padding: {padding};
    border-radius: {radius};
'>
    Contenu
</div>
""", unsafe_allow_html=True)
```

### Pattern 3: Utiliser les composants réutilisables

```python
from components.reusable_components import render_card, render_badge

render_card(
    title="Résultats",
    content="Mon contenu",
)

render_badge("Nouveau", variant="success")
```

### Pattern 4: Ajouter un composant personnalisé

```python
from components.theme_manager import ThemeManager

def render_my_widget(data):
    colors = ThemeManager.get_colors()
    
    st.markdown(f"""
    <div style='color: {colors["text_primary"]};'>
        {data}
    </div>
    """, unsafe_allow_html=True)

# Utilisation
render_my_widget("Mon texte")
```

---

## 🚀 Quick Reference

### Importer les couleurs
```python
from components.theme_manager import ThemeManager
colors = ThemeManager.get_colors()
```

### Importer les tokens
```python
from components.design_tokens import get_spacing, get_radius, get_font_size
```

### Importer les composants
```python
from components.reusable_components import render_card, render_badge, render_alert
```

### Importer le thème manager
```python
from components.theme_manager import theme
```

### Initialiser au démarrage
```python
from components.theme_selector import init_theme_system
init_theme_system()
```

---

## 📋 Checklist de Vérification

Avant de considérer une implémentation complète:

- [ ] Tous les imprts sont corrects
- [ ] `init_theme_system()` appelé au démarrage
- [ ] Pas de couleurs hardcodées
- [ ] Tous les composants changent au switch de thème
- [ ] Performance acceptable
- [ ] Tests en light ET dark mode passent

---

**Fin de la référence API! 📚**
