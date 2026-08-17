# DESIGN — `_template/`

> Le système de template canonique pour les sites d'Amine.
> Une structure, plusieurs vibes, des colorways illimités.

## North Star

**"Un instrument, pas une décoration."**

Chaque site doit lire comme un cahier de laboratoire publié, pas comme une landing page SaaS. Le visiteur — un admissions officer du MIT, un recruteur, un mentor — doit comprendre en 4 secondes qu'il y a un cerveau derrière, pas un template. La structure canonique reste identique partout ; seule l'**identité visuelle** change, parce que le sujet mérite une voix différente.

Le jugement d'un reviewer AWWWARDS est brutal et juste : si un site peut être confondu avec n'importe quel autre, il perd en Design (40%) et en Creativity (20%). Notre défense est **l'intentionnalité visible** — chaque décision typographique, chaque couleur, chaque mouvement doit pouvoir être défendu en une phrase.

## Anatomie

Le template canonique a exactement ces sections, dans cet ordre, jamais plus, jamais moins :

1. **Nav** — logo monospace + 3 liens max + 1 CTA externe
2. **Hero** — eyebrow, titre display, sous-titre, bio, double CTA
3. **Stats Row** — grille dense de métriques (4 à 6 cellules, fond uni, 1px de séparation)
4. **Manifesto** — section narrative en prose (max-width 780px)
5. **Projects Grid** — 2 colonnes desktop, 1 mobile, cartes à filet top animé
6. **About** — pourquoi, avec stats secondaires
7. **Footer** — nom + tagline + 3 liens externes

Cette structure ne change **jamais** entre vibes. C'est le squelette canonique, équivalent du SVG canonical d'archify.

## Les 4 Vibes

Chaque vibe est une **identité visuelle complète** — typographie, matière, motion, composition. Le choix d'une vibe dépend du sujet, pas du goût.

| Vibe | Pour qui | Matière | Type display | Type body | Type mono |
|---|---|---|---|---|---|
| **field-journal** | Projets over-engineer, math/physics modeling | Papier chaud, lignes réglées, encre | Syne (sans geometric) | DM Sans | DM Mono |
| **console** | Projets ML, systèmes, agent-runs | Terminal sombre, scanline | JetBrains Mono | JetBrains Mono | JetBrains Mono |
| **atlas** | Projets aero, cartographie, infra | Blueprint grid, drafting marks | Space Grotesk | Inter | JetBrains Mono |
| **dispatch** | Case studies, startup, narrative reportage | Magazine, photography-led | Playfair Display | Source Serif | JetBrains Mono |

## Colorways

Chaque vibe accepte un **colorway** — un swap d'accent unique qui préserve la hiérarchie. La règle absolue : **un seul accent saturé par page**, jamais deux. L'accent est porté par :

- le filet top des cartes au hover
- la barre de progression de scroll
- les liens externes au hover
- les chiffres stat-clé (`.stat-value`)
- le point d'eyebrow (`.hero-eyebrow::before`)

Huit colorways disponibles par vibe : `navy`, `vermilion`, `emerald`, `amber`, `sky`, `rose`, `violet`, `graphite`. Le colorway ne change jamais le background, le body text, ou les règles structurelles — seulement l'accent.

## Règles nommées (lues avant chaque PR)

### The Vibe Parity Rule
Deux sites utilisant la même vibe doivent partager la même typographie, la même matière, le même langage motion, la même composition. Ils peuvent différer par colorway. Si un over-engineer-traffic et un over-engineer-raindrops utilisent `field-journal`, ils doivent être reconnaissables comme frères jumeaux à première vue.

### The Colorway Identity Rule
Le colorway est un **accent**, pas une thématique. `amber` ne signifie pas "trafic" — il signifie "la couleur d'accent de ce projet est ambre". Le sens sémantique vient du contenu, pas de la couleur. On n'utilise jamais deux accents saturés sur la même page.

### The One Display Rule
Une seule famille display par vibe. Une seule famille body. Une seule famille mono. Les exceptions (italic, weight swap) sont autorisées ; les familles supplémentaires sont interdites.

### The Flat-at-Rest Rule
Pas de shadow par défaut. Les shadows apparaissent uniquement sur les éléments flottants actifs (nav au scroll, tooltip). Une carte au repos est définie par border + tonalité, jamais par élévation. Cette règle élimine 80% du "look SaaS générique".

### The No-Gradient Rule
Les dégradés sont interdits sauf dans deux cas : (1) un seul radial-subtle derrière le hero comme atmosphère (signal-flow), (2) les barres de progression techniques. Pas de gradient text, pas de gradient bouton, pas de gradient card.

### The Motion Budget Rule
Une page a droit à **trois signatures motion** au maximum :
1. Reveal on scroll (translateY + opacity, 0.8s)
2. Card hover (filet top 0.4s + gap link 0.2s)
3. Une signature motion propre à la vibe (atmosphere pulse pour console, ruling line draw pour field-journal, grid pan pour atlas, image parallax pour dispatch)

Tout autre mouvement est interdit. Pas de marquee, pas de count-up, pas de shimmer, pas de parallax partout.

### The Density Rule
Le body text est en `font-weight: 300` ou `400`, jamais plus. Les labels mono sont en `500`-`700`. Les display sont en `700`-`800`. Le contraste vient du poids, pas de la couleur.

### The Anti-Cliché Rule
Sont interdits :
- glassmorphism (backdrop-blur + transparency)
- gradients text
- icon packs génériques (lucide, heroicons en float)
- "Trusted by" logos grisés
- 3-card equal-height features
- hero avec illustration isométrique
- emoji comme icons
- "Get started" / "Learn more" comme CTA

## Do's

- **Do** charger les fonts en `media="print" onload` — pas de FOUT bloquant
- **Do** prévoir `prefers-reduced-motion` qui désactive les 3 signatures
- **Do** garder le `aspect-ratio` des images pour éviter le CLS
- **Do** écrire le `<title>` et le `<meta description>` par page, pas un template générique
- **Do** inclure un favicon SVG inline (un glyphe monospace)

## Don'ts

- **Don't** ajouter une 5e vibe "pour le fun" — quatre vibes, c'est un système
- **Don't** varier la structure canonique entre vibes
- **Don't** utiliser deux colorways sur la même page
- **Don't** mettre du JS framework (React, Vue) — c'est du statique, vanilla JS only
- **Don't** dépasser 50kb CSS total pour une page rendue

## Processus de génération

```
content.json + vibe + colorway
            ↓
       build.mjs (string substitution)
            ↓
       final index.html (self-contained)
```

Le `content.json` contient toutes les données variables (titre, bio, projets, stats, liens). Le `vibe` détermine le `<html data-vibe="...">`. Le `colorway` détermine le `<html data-colorway="...">`. Tout le reste est dans le template canonique.

## Checklist d'acceptation d'un site rendu

- [ ] `<html data-vibe="X" data-colorway="Y" data-theme="dark|light">` présent
- [ ] Toutes les 7 sections canoniques présentes, dans l'ordre
- [ ] Une seule famille display, body, mono chargée
- [ ] Un seul accent saturé visible
- [ ] Trois signatures motion maximum, toutes sous `prefers-reduced-motion`
- [ ] Lighthouse Performance ≥ 90, Accessibility ≥ 95
- [ ] Aucun `backdrop-filter` sauf nav scrolled
- [ ] Favicon SVG inline présent
- [ ] `<title>` et `<meta description>` spécifiques au projet
