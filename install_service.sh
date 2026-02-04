#!/bin/bash

# Installation Script für Fan Control Service

echo "Installing Fan Control Service..."

# Kopiere die Service-Datei nach /etc/systemd/system/
sudo cp fancontrol.service /etc/systemd/system/

# Setze die richtigen Berechtigungen
sudo chmod 644 /etc/systemd/system/fancontrol.service

# Lade systemd neu
sudo systemctl daemon-reload

# Aktiviere den Service für Autostart
sudo systemctl enable fancontrol.service

# Starte den Service
sudo systemctl start fancontrol.service

# Zeige den Status
sudo systemctl status fancontrol.service

echo ""
echo "Installation abgeschlossen!"
echo ""
echo "Nützliche Befehle:"
echo "  Status anzeigen:    sudo systemctl status fancontrol"
echo "  Service starten:    sudo systemctl start fancontrol"
echo "  Service stoppen:    sudo systemctl stop fancontrol"
echo "  Service neustarten: sudo systemctl restart fancontrol"
echo "  Logs anzeigen:      sudo journalctl -u fancontrol -f"
