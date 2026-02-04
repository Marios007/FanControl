import time
import board
import neopixel

# WS2812B LED Ring Konfiguration (AZ-Delivery 12 LEDs)
pixel_pin = board.D18
num_pixels = 12
ORDER = neopixel.GRB  # WS2812B verwendet GRB-Reihenfolge
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.3, auto_write=False, pixel_order=ORDER)

def clear():
    """Alle LEDs ausschalten"""
    pixels.fill((0, 0, 0))
    pixels.show()

def test_individual_leds():
    """Jede LED einzeln testen"""
    print('  Teste jede LED einzeln...')
    for i in range(num_pixels):
        clear()
        pixels[i] = (255, 0, 0)  # Rot
        pixels.show()
        time.sleep(0.2)
    clear()

def rainbow_cycle(wait):
    """Regenbogen-Animation"""
    for j in range(255):
        for i in range(num_pixels):
            pixel_index = (i * 256 // num_pixels) + j
            pixels[i] = wheel(pixel_index & 255)
        pixels.show()
        time.sleep(wait)

def wheel(pos):
    """Farbrad für Regenbogen-Effekt"""
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

print('WS2812B LED Ring Test (AZ-Delivery 12 LEDs)')
print('[Drücken Sie CTRL + C um das Skript zu beenden!]\n')

# Initialisierung: Alle LEDs ausschalten
clear()
time.sleep(0.5)

try:
    while True:
        print('Rot (alle LEDs)')
        pixels.fill((255, 0, 0))
        pixels.show()
        time.sleep(2)
        
        print('Grün (alle LEDs)')
        pixels.fill((0, 255, 0))
        pixels.show()
        time.sleep(2)
        
        print('Blau (alle LEDs)')
        pixels.fill((0, 0, 255))
        pixels.show()
        time.sleep(2)
        
        print('Weiß (alle LEDs)')
        pixels.fill((255, 255, 255))
        pixels.show()
        time.sleep(2)
        
        test_individual_leds()
        
        print('Regenbogen-Animation')
        rainbow_cycle(0.001)
        
        clear()
        time.sleep(1)

except KeyboardInterrupt:
    print('\nScript Ende!')
    clear()
    print('Alle LEDs ausgeschaltet.')