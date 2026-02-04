import time
import board
import neopixel
import threading

class LedRing:
    """Klasse zur Steuerung des WS2812B LED Rings"""
    
    def __init__(self, pin=board.D21, num_pixels=12, brightness=0.1):
        """
        Initialisiere den LED Ring
        
        Args:
            pin: GPIO Pin (Standard: D21/GPIO 21/Pin 40)
            num_pixels: Anzahl der LEDs (Standard: 12)
            brightness: Helligkeit 0.0-1.0 (Standard: 0.3)
        """
        self.num_pixels = num_pixels
        self.pixels = neopixel.NeoPixel(
            pin, 
            num_pixels, 
            brightness=brightness, 
            auto_write=False, 
            pixel_order=neopixel.GRB
        )
        self.timer = None
        self.clear()
        print(f'LED Ring initialisiert: {num_pixels} LEDs auf GPIO 21 (Pin 40)')
    
    def clear(self):
        """Alle LEDs ausschalten"""
        self.pixels.fill((0, 0, 0))
        self.pixels.show()
    
    def set_color(self, color):
        """
        Setze alle LEDs auf eine Farbe
        
        Args:
            color: Tuple (R, G, B) mit Werten 0-255
        """
        self.pixels.fill(color)
        self.pixels.show()
    
    def white(self):
        """Alle LEDs weiß"""
        self.set_color((255, 255, 255))
    
    def red(self):
        """Alle LEDs rot"""
        self.set_color((255, 0, 0))
    
    def green(self):
        """Alle LEDs grün"""
        self.set_color((0, 255, 0))
    
    def blue(self):
        """Alle LEDs blau"""
        self.set_color((0, 0, 255))
    
    def light_on(self, duration_seconds):
        """
        Schalte weißes Licht für eine bestimmte Dauer ein
        
        Args:
            duration_seconds: Dauer in Sekunden
        """
        # Stoppe vorherigen Timer falls vorhanden
        if self.timer:
            self.timer.cancel()
        
        # Licht einschalten
        self.white()
        print(f'LED Ring: Licht eingeschaltet für {duration_seconds} Sekunden')
        
        # Timer zum automatischen Ausschalten
        self.timer = threading.Timer(duration_seconds, self._auto_off)
        self.timer.start()
    
    def _auto_off(self):
        """Interne Methode zum automatischen Ausschalten"""
        self.clear()
        print('LED Ring: Licht automatisch ausgeschaltet')
        self.timer = None
    
    def rainbow_cycle(self, duration):
        """
        Regenbogen-Animation für bestimmte Dauer
        
        Args:
            duration: Dauer in Sekunden
        """
        frames = 255
        wait = duration / frames
        
        for j in range(frames):
            for i in range(self.num_pixels):
                pixel_index = (i * 256 // self.num_pixels) + j
                self.pixels[i] = self._wheel(pixel_index & 255)
            self.pixels.show()
            time.sleep(wait)
    
    def _wheel(self, pos):
        """Farbrad-Hilfsfunktion für Regenbogen-Effekt"""
        if pos < 0 or pos > 255:
            r = g = b = 0
        elif pos < 85:
            r = int(pos * 3)
            g = int(255 - pos * 3)
            b = 0
        elif pos < 170:
            pos -= 85
            r = int(255 - pos * 3)
            g = 0
            b = int(pos * 3)
        else:
            pos -= 170
            r = 0
            g = int(pos * 3)
            b = int(255 - pos * 3)
        return (r, g, b)
    
    def cleanup(self):
        """Aufräumen beim Beenden"""
        if self.timer:
            self.timer.cancel()
        self.clear()
        print('LED Ring: Cleanup abgeschlossen')
