#!/usr/bin/env python3
"""
Kamera-Klasse für Raspberry Pi Camera
Macht ein Foto und lädt es auf FritzNAS via SMB
"""
from datetime import datetime
from picamera2 import Picamera2
from smb.SMBConnection import SMBConnection
import threading
import io
import config

class Camera:
    """Klasse zur Steuerung der Raspberry Pi Kamera"""
    
    def __init__(self):
        """Initialisiere Kamera-Konfiguration"""
        # SMB/NAS Konfiguration aus config.py
        self.smb_server = config.smb_server
        self.smb_username = config.smb_username
        self.smb_password = config.smb_password
        self.smb_share = config.smb_share
        self.smb_folder = config.smb_folder
        
        # Kamera Konfiguration
        self.resolution = (3280, 2464)
        self.max_files = 15
        
        self.picam = None
        self.timer = None
        print('Kamera Modul initialisiert')
    
    def get_smb_connection(self):
        """Erstellt SMB-Verbindung zur FritzBox."""
        conn = SMBConnection(
            self.smb_username,
            self.smb_password,
            "raspberry",
            "FRITZBOX",
            use_ntlm_v2=True,
            is_direct_tcp=True
        )
        conn.connect(self.smb_server, 445)
        return conn
    
    def list_smb_files(self, conn):
        """Listet alle Capture-Dateien auf dem SMB-Share."""
        try:
            files = conn.listPath(self.smb_share, f"/{self.smb_folder}/")
            captures = [
                f for f in files 
                if f.filename.startswith("capture_") and f.filename.endswith(".jpg")
            ]
            return sorted(captures, key=lambda f: f.last_write_time)
        except:
            return []
    
    def trim_smb_directory(self, conn, max_files):
        """Löscht älteste Dateien auf SMB-Share wenn mehr als max_files vorhanden."""
        files = self.list_smb_files(conn)
        while len(files) > max_files:
            victim = files.pop(0)
            try:
                conn.deleteFiles(self.smb_share, f"/{self.smb_folder}/{victim.filename}")
                print(f"Entfernt: {victim.filename}")
            except Exception as e:
                print(f"Fehler beim Löschen von {victim.filename}: {e}")
    
    def save_to_smb(self, conn, image_data, filename):
        """Speichert Bilddaten auf SMB-Share."""
        file_obj = io.BytesIO(image_data)
        conn.storeFile(self.smb_share, f"/{self.smb_folder}/{filename}", file_obj)
    
    def capture_photo(self):
        """Macht ein einzelnes Foto und lädt es auf den SMB Server"""
        try:
            # SMB-Verbindung herstellen
            print("Verbinde mit FritzNAS...")
            smb_conn = self.get_smb_connection()
            print(f"✓ Verbunden mit {self.smb_server}")
            
            # Zielordner auf NAS erstellen falls nicht vorhanden
            try:
                smb_conn.createDirectory(self.smb_share, f"/{self.smb_folder}")
            except:
                pass  # Ordner existiert bereits
            
            # Kamera initialisieren
            print("Initialisiere Kamera...")
            self.picam = Picamera2()
            config = self.picam.create_still_configuration(main={"size": self.resolution})
            self.picam.configure(config)
            self.picam.start()
            print("Kamera gestartet")
            
            # Zeitstempel für Dateiname
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"capture_{timestamp}.jpg"
            
            # Foto aufnehmen
            image_data = io.BytesIO()
            self.picam.capture_file(image_data, format='jpeg')
            
            # Auf NAS speichern
            self.save_to_smb(smb_conn, image_data.getvalue(), filename)
            print(f"Foto gespeichert: {filename}")
            
            # Alte Fotos löschen falls Limit überschritten
            self.trim_smb_directory(smb_conn, self.max_files)
            
            # Aufräumen
            self.picam.stop()
            smb_conn.close()
            self.picam = None
            
            print("Kamera-Aufnahme abgeschlossen")
            return True
            
        except Exception as e:
            print(f"Fehler bei Kamera-Aufnahme: {e}")
            if self.picam:
                try:
                    self.picam.stop()
                except:
                    pass
                self.picam = None
            return False
    
    def start_capture_with_timeout(self, timeout_seconds=300, interval_seconds=30):
        """
        Startet wiederholte Foto-Aufnahmen und beendet automatisch nach timeout
        
        Args:
            timeout_seconds: Zeit in Sekunden bis zum automatischen Beenden (Standard: 300 = 5 Minuten)
            interval_seconds: Intervall zwischen Fotos in Sekunden (Standard: 30 Sekunden)
        """
        # Stoppe vorherigen Timer falls vorhanden
        if self.timer:
            self.timer.cancel()
        
        # Wiederholte Fotos in separatem Thread aufnehmen
        capture_thread = threading.Thread(
            target=self._capture_repeatedly, 
            args=(timeout_seconds, interval_seconds)
        )
        capture_thread.daemon = True
        capture_thread.start()
        
        print(f"Kamera gestartet: macht alle {interval_seconds} Sekunden ein Foto für {timeout_seconds} Sekunden")
        
        # Timer zum automatischen Cleanup
        self.timer = threading.Timer(timeout_seconds, self._auto_cleanup)
        self.timer.start()
    
    def _capture_repeatedly(self, duration_seconds, interval_seconds):
        """
        Macht wiederholt Fotos in festgelegten Intervallen
        
        Args:
            duration_seconds: Gesamtdauer in Sekunden
            interval_seconds: Intervall zwischen Fotos in Sekunden
        """
        import time
        start_time = time.time()
        
        while (time.time() - start_time) < duration_seconds:
            try:
                self.capture_photo()
            except Exception as e:
                print(f"Fehler bei wiederholter Aufnahme: {e}")
            
            # Warte bis zum nächsten Intervall (nur wenn noch Zeit übrig ist)
            elapsed = time.time() - start_time
            if (elapsed + interval_seconds) < duration_seconds:
                time.sleep(interval_seconds)
            else:
                break
        
        print("Wiederholte Foto-Aufnahme beendet")
    
    def _auto_cleanup(self):
        """Automatisches Cleanup nach Timeout"""
        if self.picam:
            try:
                self.picam.stop()
                self.picam = None
                print("Kamera automatisch nach Timeout gestoppt")
            except:
                pass
        self.timer = None
    
    def cleanup(self):
        """Aufräumen beim Beenden"""
        if self.timer:
            self.timer.cancel()
            self.timer = None
        if self.picam:
            try:
                self.picam.stop()
            except:
                pass
            self.picam = None
        print('Kamera: Cleanup abgeschlossen')
