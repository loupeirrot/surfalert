#!/bin/bash
# ──────────────────────────────────────────────────────────
# SurfAlert — Installation & configuration automatique
# Lance ce script une seule fois depuis ton terminal.
# ──────────────────────────────────────────────────────────

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SURF_SCRIPT="$SCRIPT_DIR/surf_alert.py"
LOG_FILE="$SCRIPT_DIR/surfalert.log"

echo ""
echo "🌊  SurfAlert — Installation"
echo "────────────────────────────"

# 1. Vérifie Python3
if ! command -v python3 &>/dev/null; then
    echo "❌ Python3 non trouvé. Installe-le via https://www.python.org"
    exit 1
fi
echo "✅ Python3 : $(python3 --version)"

# 2. Installe les dépendances
echo "📦 Installation des dépendances..."
pip3 install requests astral pytz --quiet --break-system-packages 2>/dev/null \
    || pip3 install requests astral pytz --quiet

echo "✅ Dépendances installées"

# 3. Test immédiat
echo ""
echo "🧪 Test d'envoi Telegram..."
python3 "$SURF_SCRIPT"
echo ""
echo "✅ Script OK ! Vérifie Telegram."

# 4. Configuration du cron (alertes 2x/jour)
echo ""
echo "⏰ Configuration des alertes automatiques..."

# Supprime les anciennes entrées surfalert si elles existent
(crontab -l 2>/dev/null | grep -v "surf_alert") | crontab -

# 3 checks par jour pour une anticipation maximale (5 jours de prévision)
(crontab -l 2>/dev/null; echo "0 6  * * * /usr/bin/python3 $SURF_SCRIPT >> $LOG_FILE 2>&1") | crontab -
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/python3 $SURF_SCRIPT >> $LOG_FILE 2>&1") | crontab -
(crontab -l 2>/dev/null; echo "0 18 * * * /usr/bin/python3 $SURF_SCRIPT >> $LOG_FILE 2>&1") | crontab -

echo "✅ Alertes programmées :"
echo "   → 6h00  (réveil : anticipe la journée)"
echo "   → 12h00 (midi : prévisions J+2/J+3 affinées)"
echo "   → 18h00 (soir : prépare le lendemain)"
echo ""
echo "📄 Logs disponibles dans : $LOG_FILE"
echo ""
echo "🎉 SurfAlert est opérationnel ! 🤙"
echo ""
echo "Commandes utiles :"
echo "  • Lancer manuellement : python3 $SURF_SCRIPT"
echo "  • Voir les alertes cron : crontab -l"
echo "  • Voir les logs : tail -f $LOG_FILE"
echo "  • Supprimer les crons : crontab -r"
