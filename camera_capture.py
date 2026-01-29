#!/usr/bin/env python3
"""
Raspberry Pi Camera Capture - Jede Minute ein Foto
Speichert maximal 50 Fotos, ältere werden automatisch gelöscht
"""
from datetime import datetime
from pathlib import Path
from picamera2 import Picamera2
import time

OUTPUT_DIR = Path("/home/mario/RSA")
RESOLUTION = (1920, 1080)  # Breite, Höhe in Pixeln
MAX_FILES = 50  # Maximale Anzahl gespeicherter Fotos
INTERVAL = 60  # Sekunden zwischen Aufnahmen


def trim_directory(path: Path, max_files: int) -> None:
    """Löscht älteste Dateien wenn mehr als max_files vorhanden sind."""
    files = sorted(path.glob("capture_*.jpg"), key=lambda p: p.stat().st_mtime)
    while len(files) > max_files:
        victim = files.pop(0)
        victim.unlink(missing_ok=True)
        print(f"Entfernt: {victim.name}")


def main():
    # Zielverzeichnis erstellen falls nicht vorhanden
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Kamera initialisieren
    print("Initialisiere Kamera...")
    picam = Picamera2()
    config = picam.create_still_configuration(main={"size": RESOLUTION})
    picam.configure(config)
    picam.start()
    print(f"Kamera gestartet. Speichere Fotos in: {OUTPUT_DIR}")
    print(f"Maximal {MAX_FILES} Fotos, Intervall: {INTERVAL} Sekunden")
    
    try:
        while True:
            # Zeitstempel für Dateiname
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = OUTPUT_DIR / f"capture_{timestamp}.jpg"
            
            # Foto aufnehmen
            picam.capture_file(str(filename))
            print(f"Gespeichert: {filename.name}")
            
            # Alte Fotos löschen falls Limit überschritten
            trim_directory(OUTPUT_DIR, MAX_FILES)
            
            # Warten bis zur nächsten Aufnahme
            time.sleep(INTERVAL)
            
    except KeyboardInterrupt:
        print("\nBeende Aufnahme...")
    finally:
        picam.stop()
        print("Kamera gestoppt.")


if __name__ == "__main__":
    main()
