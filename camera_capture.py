#!/usr/bin/env python3
"""
Raspberry Pi Camera Capture - Jede Minute ein Foto
Speichert auf FritzNAS via SMB, maximal 50 Fotos
"""
from datetime import datetime
from pathlib import Path
from picamera2 import Picamera2
from smb.SMBConnection import SMBConnection
import time
import io

# SMB/NAS Konfiguration
SMB_SERVER = "192.168.178.1"  # IP-Adresse der FritzBox (ggf. anpassen)
SMB_USERNAME = "fritz4192"
SMB_PASSWORD = "nagel0924"
SMB_SHARE = "FRITZ.NAS"  # Freigabe-Name in Großbuchstaben
SMB_FOLDER = "RaspberryCaptures"  # Unterordner auf dem NAS

# Kamera Konfiguration
RESOLUTION = (1920, 1080)
MAX_FILES = 50
INTERVAL = 60


def get_smb_connection():
    """Erstellt SMB-Verbindung zur FritzBox."""
    print(f"Verbindungsdetails: Server={SMB_SERVER}, User={SMB_USERNAME}, Share={SMB_SHARE}")
    
    # Methode 1: Mit Server-Name
    try:
        conn = SMBConnection(
            SMB_USERNAME,
            SMB_PASSWORD,
            "raspberry",
            "FRITZBOX",  # Standard NetBIOS-Name
            use_ntlm_v2=True,
            is_direct_tcp=True
        )
        if conn.connect(SMB_SERVER, 445):
            print("Verbunden (Methode 1: NetBIOS FRITZBOX)")
            return conn
    except Exception as e:
        print(f"Methode 1 fehlgeschlagen: {e}")
    
    # Methode 2: Ohne NetBIOS
    try:
        conn = SMBConnection(
            SMB_USERNAME,
            SMB_PASSWORD,
            "",
            "",
            use_ntlm_v2=True,
            is_direct_tcp=True
        )
        if conn.connect(SMB_SERVER, 445):
            print("Verbunden (Methode 2: Direct TCP)")
            return conn
    except Exception as e:
        print(f"Methode 2 fehlgeschlagen: {e}")
    
    # Methode 3: Mit Domain
    try:
        conn = SMBConnection(
            SMB_USERNAME,
            SMB_PASSWORD,
            "raspberry",
            "FRITZBOX",
            domain="WORKGROUP",
            use_ntlm_v2=True,
            is_direct_tcp=True
        )
        if conn.connect(SMB_SERVER, 445):
            print("Verbunden (Methode 3: Mit WORKGROUP)")
            return conn
    except Exception as e:
        print(f"Methode 3 fehlgeschlagen: {e}")
    
    raise ConnectionError("Alle Verbindungsmethoden fehlgeschlagen")


def list_smb_files(conn):
    """Listet alle Capture-Dateien auf dem SMB-Share."""
    try:
        files = conn.listPath(SMB_SHARE, f"/{SMB_FOLDER}/")
        captures = [
            f for f in files 
            if f.filename.startswith("capture_") and f.filename.endswith(".jpg")
        ]
        return sorted(captures, key=lambda f: f.last_write_time)
    except:
        return []


def trim_smb_directory(conn, max_files: int) -> None:
    """Löscht älteste Dateien auf SMB-Share wenn mehr als max_files vorhanden."""
    files = list_smb_files(conn)
    while len(files) > max_files:
        victim = files.pop(0)
        try:
            conn.deleteFiles(SMB_SHARE, f"/{SMB_FOLDER}/{victim.filename}")
            print(f"Entfernt: {victim.filename}")
        except Exception as e:
            print(f"Fehler beim Löschen von {victim.filename}: {e}")


def save_to_smb(conn, image_data: bytes, filename: str) -> None:
    """Speichert Bilddaten auf SMB-Share."""
    file_obj = io.BytesIO(image_data)
    conn.storeFile(SMB_SHARE, f"/{SMB_FOLDER}/{filename}", file_obj)


def main():
    # SMB-Verbindung herstellen
    print("Verbinde mit FritzNAS...")
    try:
        smb_conn = get_smb_connection()
        print(f"✓ Verbunden mit {SMB_SERVER}")
        
        # Liste verfügbare Freigaben
        print("\nVerfügbare Freigaben:")
        try:
            shares = smb_conn.listShares()
            for share in shares:
                if not share.isSpecial:
                    print(f"  - {share.name}")
        except Exception as e:
            print(f"Fehler beim Listen der Freigaben: {e}")
        
        # Zielordner auf NAS erstellen falls nicht vorhanden
        try:
            smb_conn.createDirectory(SMB_SHARE, f"/{SMB_FOLDER}")
            print(f"✓ Ordner erstellt: {SMB_SHARE}/{SMB_FOLDER}")
        except Exception as e:
            print(f"Info: {e} (Ordner existiert vermutlich bereits)")
            
    except Exception as e:
        print(f"\n✗ Fehler bei SMB-Verbindung: {e}")
        print("\nTroubleshooting:")
        print("1. Prüfe IP-Adresse der FritzBox (aktuell: {})" .format(SMB_SERVER))
        print("2. Prüfe Freigabe-Name (aktuell: {})" .format(SMB_SHARE))
        print("3. Prüfe Benutzername/Passwort")
        print("4. FritzBox: Heimnetz → Speicher (NAS) → Zugriff aus Heimnetz aktiviert?")
        return
    
    # Kamera initialisieren
    print("Initialisiere Kamera...")
    picam = Picamera2()
    config = picam.create_still_configuration(main={"size": RESOLUTION})
    picam.configure(config)
    picam.start()
    print(f"Kamera gestartet. Speichere auf {SMB_SERVER}/{SMB_SHARE}/{SMB_FOLDER}")
    print(f"Maximal {MAX_FILES} Fotos, Intervall: {INTERVAL} Sekunden")
    
    try:
        while True:
            # Zeitstempel für Dateiname
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"capture_{timestamp}.jpg"
            
            # Foto aufnehmen in Speicher
            image_data = io.BytesIO()
            picam.capture_file(image_data, format='jpeg')
            
            # Auf NAS speichern
            try:
                save_to_smb(smb_conn, image_data.getvalue(), filename)
                print(f"Gespeichert: {filename}")
            except Exception as e:
                print(f"Fehler beim Speichern: {e}")
                # Verbindung neu aufbauen
                try:
                    smb_conn.close()
                    smb_conn = get_smb_connection()
                    save_to_smb(smb_conn, image_data.getvalue(), filename)
                    print(f"Erneut gespeichert: {filename}")
                except Exception as e2:
                    print(f"Speichern fehlgeschlagen: {e2}")
            
            # Alte Fotos löschen falls Limit überschritten
            trim_smb_directory(smb_conn, MAX_FILES)
            
            # Warten bis zur nächsten Aufnahme
            time.sleep(INTERVAL)
            
    except KeyboardInterrupt:
        print("\nBeende Aufnahme...")
    finally:
        picam.stop()
        smb_conn.close()
        print("Kamera gestoppt, SMB-Verbindung geschlossen.")


if __name__ == "__main__":
    main()
