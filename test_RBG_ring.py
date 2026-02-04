import time
import board
import neopixel

print('=== WS2812B LED Ring Diagnose ===\n')

# Konfiguration
num_pixels = 12
pin_to_test = board.D21  # GPIO 21 (Pin 40)

print(f'GPIO Pin: D21 (GPIO 21, physischer Pin 40)')
print(f'Anzahl LEDs: {num_pixels}')
print(f'Chip: WS2812B (AZ-Delivery)\n')

print('WICHTIG: Prüfen Sie die Verkabelung:')
print('  LED Ring VCC  -> Raspberry Pi Pin 2 oder 4 (5V)')
print('  LED Ring GND  -> Raspberry Pi Pin 6 (GND)')
print('  LED Ring DIN  -> Raspberry Pi Pin 40 (GPIO 21)\n')

# Teste verschiedene Farbreihenfolgen
color_orders = [
    (neopixel.GRB, "GRB (Standard WS2812B)"),
    (neopixel.RGB, "RGB"),
    (neopixel.RGBW, "RGBW")
]

for order, order_name in color_orders:
    try:
        print(f'\n--- Test mit {order_name} ---')
        pixels = neopixel.NeoPixel(
            pin_to_test, 
            num_pixels, 
            brightness=1.0,  # Volle Helligkeit für Test
            auto_write=False, 
            pixel_order=order
        )
        
        # Test 1: Alle LEDs Rot
        print('  [1] Alle LEDs ROT (volle Helligkeit)...')
        pixels.fill((255, 0, 0))
        pixels.show()
        time.sleep(3)
        
        # Test 2: Alle LEDs Grün
        print('  [2] Alle LEDs GRÜN...')
        pixels.fill((0, 255, 0))
        pixels.show()
        time.sleep(3)
        
        # Test 3: Alle LEDs Blau
        print('  [3] Alle LEDs BLAU...')
        pixels.fill((0, 0, 255))
        pixels.show()
        time.sleep(3)
        
        # Test 4: Erste LED weiß
        print('  [4] Erste LED WEISS...')
        pixels.fill((0, 0, 0))
        pixels[0] = (255, 255, 255)
        pixels.show()
        time.sleep(3)
        
        # Ausschalten
        pixels.fill((0, 0, 0))
        pixels.show()
        pixels.deinit()
        
        print(f'  ✓ Test mit {order_name} abgeschlossen')
        
    except Exception as e:
        print(f'  ✗ Fehler bei {order_name}: {e}')
        continue

print('\n=== Diagnose abgeschlossen ===')
print('\nWenn NICHTS geleuchtet hat:')
print('1. Prüfen Sie die 5V Stromversorgung am LED Ring')
print('2. Prüfen Sie, ob GND verbunden ist')
print('3. Script mit sudo ausführen: sudo python3 test_RBG_ring.py')
print('4. Testen Sie einen anderen GPIO Pin (z.B. GPIO 21, Pin 40)')
print('5. Prüfen Sie, ob die LEDs defekt sind (mit Multimeter)')