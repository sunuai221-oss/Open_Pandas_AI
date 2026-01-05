# Guide d'utilisation de Tailwind CSS dans Open Pandas-AI

## Classes Tailwind pour les couleurs

### Texte principal (Light/Dark)
- `text-slate-900` - Texte principal (light mode)
- `dark:text-white` - Texte blanc (dark mode)
- `text-slate-600` - Texte secondaire (light mode)
- `dark:text-slate-200` - Texte secondaire clair (dark mode)
- `dark:text-slate-300` - Texte secondaire moyen (dark mode)

### Exemples d'utilisation

#### Sous-titre principal
```html
<p class="text-lg font-medium text-slate-900 dark:text-white">
    Votre texte ici
</p>
```

#### En-tête de section
```html
<h3 class="text-2xl font-bold text-slate-900 dark:text-white">
    🚀 Titre de section
</h3>
```

#### Texte secondaire
```html
<p class="text-sm text-slate-600 dark:text-slate-200">
    Description ou texte secondaire
</p>
```

#### Footer
```html
<div class="text-center py-5 text-slate-600 dark:text-slate-300">
    Texte du footer
</div>
```

#### Sidebar
```html
<div class="text-slate-900 dark:text-white">
    <h3 class="text-lg font-bold dark:text-white">Titre</h3>
    <p class="text-slate-700 dark:text-slate-200">Contenu</p>
</div>
```

## Couleurs Tailwind disponibles

### Slate (gris)
- `text-slate-50` à `text-slate-900` (light mode)
- `dark:text-slate-50` à `dark:text-slate-900` (dark mode)

### Blue (bleu)
- `text-blue-500`, `bg-blue-500`, etc.

### Autres couleurs
- `text-red-500`, `text-green-500`, `text-yellow-500`, etc.

## Dark Mode

Tailwind détecte automatiquement le dark mode via:
- `[data-theme="dark"]` (attribut Streamlit)
- `@media (prefers-color-scheme: dark)` (préférence système)

## Avantages

1. **Simplicité** : Classes utilitaires au lieu de CSS custom
2. **Cohérence** : Palette de couleurs standardisée
3. **Dark mode automatique** : Gestion native du dark mode
4. **Maintenabilité** : Code plus lisible et maintenable
