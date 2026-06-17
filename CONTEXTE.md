# SurfAlert — Contexte projet

## Vision
Application de prévisions surf pour **filmer des sessions de qualité** sur la côte landaise (Hossegor / Capbreton / Seignosse). Pierre a acheté un objectif Sony 200-600mm et cherche à constituer un portfolio vidéo pour trouver des clients dans le surf. L'objectif à terme est une vraie application (surfalerte.fr) avec une dimension communautaire.

## Ce qui est déjà en place

### `surf_alert.py` — Script opérationnel
- Récupère les données **Open-Meteo Marine** (houle) + **Open-Meteo Forecast** (vent, météo)
- Calcule un **score /10** par spot avec des paramètres affinés par spot
- Envoie des alertes **Telegram** uniquement si score ≥ 7.5 (silence total en dessous)
- Fenêtre d'analyse : **5 jours** avec badge J-1, J-2, J-3...
- Cron configuré : **6h, 12h et 18h** chaque jour

### Bot Telegram
- Token & Chat ID : stockés dans le fichier `.env` local (jamais publié — voir `.env.example`)
- Nom du bot : "Surf Alert"

### Spots surveillés (5)
| Spot | Coords | Houle optimale | Priorité |
|------|--------|---------------|----------|
| 🔥 La Nord (Hossegor) | 43.6750, -1.4380 | SO 215° ±25° | FIRE (≥8.5 = SESSION PRO) |
| 🏖 La Gravière (Hossegor) | 43.6673, -1.4347 | SO 220° ±25° | FIRE |
| 🏄 Les Estagnots (Seignosse) | 43.7045, -1.4289 | O/SO 240° ±30° | standard |
| 🌊 Santocha (Capbreton) | 43.6464, -1.4452 | O 255° ±35° | standard |
| 🏴 La Piste (Capbreton) | 43.6380, -1.4460 | O/SO 250° ±35° | standard |

### Logique de scoring (pondération)
| Critère | Poids | Notes |
|---------|-------|-------|
| Hauteur houle | 28% | Plage idéale par spot (ex: La Nord 1.5–4m) |
| Période | 22% | >12s = excellent |
| Direction houle | 20% | Calé sur l'optimum du spot |
| Vent | 18% | Vent Est = offshore pour toute la zone |
| Lumière | 8% | Golden hour matin/soir = 10/10 |
| Couverture nuageuse | 4% | Ciel dégagé = meilleur pour filmer |

### Seuils d'alerte
- **< 7.5** → silence total (aucun message)
- **≥ 7.5** → "📸 GO FILMER" (notification silencieuse)
- **≥ 8.5 sur spot FIRE** → "🚨 SESSION PRO" (notification avec vibration)

## Format du message Telegram
```
🚨 SESSION PRO — 🔥 La Nord (Hossegor)
────────────────────────────
📅 Demain à 09h  ⏱ J-1
🕐 Fenêtre : 08h–11h
⭐ Score : 8.9/10  █████████░

🌊 2.8m · 14s · SO 215°
💨 9km/h E ✅
📸 Lumière : 10/10  ← golden hour ✨
☁️  Ciel : 5%
```

## Stack technique
- **Python 3.9** (macOS natif)
- **Dépendances** : `requests`, `astral`, `pytz`
- **APIs gratuites** : Open-Meteo Marine, Open-Meteo Forecast
- **Notifications** : Telegram Bot API

## Roadmap

### Phase 1 ✅ — Script Telegram
Fait. Alertes automatiques opérationnelles (6h, 12h, 18h).

### Phase 2 — Page web / dashboard (prochaine étape)
- Dashboard consultable depuis le téléphone
- Graphiques de prévision sur 7 jours (houle, vent, score)
- Timeline horaire colorée (vert/orange/rouge) par spot
- Auto-mise à jour toutes les heures
- Hébergement : **Vercel** (gratuit) sur **surfalerte.fr** (domaine disponible)
- Stack suggérée : Next.js ou HTML/JS + Chart.js

### Phase 3 — Application mobile
- React Native (iOS + Android depuis une seule codebase)
- Notifications push natives

### Phase 4 — Communauté
- Rapports de conditions en temps réel (crowdsourcing)
- Galerie photos/vidéos géotagguées par spot
- Journal de sessions avec stats
- Carte des spots mondiale

## Idées différenciantes vs concurrents (Surfline, Windguru, MSW)
- Score **"Filmabilité"** distinct du score surf
- Alerte SESSION PRO quand conditions dépassent seuil critique
- Timeline visuelle tide + golden hour intégrée
- Détection events WSL quand conditions exceptionnelles
- Ambition : ouvrir à d'autres zones mondiales

## Fichiers du projet
```
/Users/pierrebargeles/Documents/Surf Alerte/
├── surf_alert.py       # Script principal (opérationnel)
├── setup_surfalert.sh  # Script d'installation + cron
├── surfalert.log       # Logs des exécutions cron
└── CONTEXTE.md         # Ce fichier
```
