# 🌊 SurfAlert

Prévisions de surf pour repérer les **belles sessions à filmer** sur la côte landaise
(La Nord · La Gravière · Les Estagnots · Santocha · La Piste).

- **Alertes Telegram** quand les conditions sont bonnes (`surf_alert.py`)
- **Dashboard web** : où & quand filmer, sur 5 jours (`index.html` + `generate_data.py`)
- Données : [Open-Meteo](https://open-meteo.com) (gratuit, sans clé)

## Lancer en local

```bash
# 1. Installer les dépendances (une seule fois)
pip3 install requests astral pytz

# 2. Configurer les secrets (une seule fois)
cp .env.example .env        # puis éditer .env avec ton token Telegram

# 3. Générer les données du dashboard
python3 generate_data.py

# 4. Lancer le site en local
python3 serve.py            # puis ouvrir http://localhost:8000
```

## Mise en ligne

Le site est publié automatiquement sur **GitHub Pages**. À chaque jour (et à chaque
modification du code), GitHub Actions régénère les données et redéploie le site.
Voir [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml).

## Sécurité

Le token Telegram n'est **jamais** dans le code : il est lu depuis un fichier `.env`
local (ignoré par git) ou depuis les *Secrets* GitHub.
