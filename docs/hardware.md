# Montaje y firmware

Objetivo: ESP32 DevKit clásico (`esp32dev`), DS18B20 impermeable y módulo pH
acondicionado. Confirmar el modelo exacto de placa y sonda antes del montaje.

| Señal | ESP32 | Observaciones |
|---|---|---|
| DS18B20 DATA | GPIO 4 | Pull-up 4,7 kΩ a 3,3 V |
| pH analógico | GPIO 34 (ADC1) | No superar 3,3 V; adaptar el módulo si requiere divisor |
| Referencia | GND | Masa común y alimentación conforme a la ficha de cada módulo |

No asumir que un módulo alimentado a 5 V tiene salida compatible con el ESP32.
Usar ADC1 para mantener compatibilidad con Wi-Fi. Caracterizar ruido y precisión.

1. Instalar VS Code y PlatformIO.
2. Copiar `include/secrets.example.h` a `include/secrets.h` dentro de `firmware/esp32`.
3. Configurar Wi-Fi, IP del broker incluida en SAN, contraseña del dispositivo y CA pública.
4. Calibrar la sonda con soluciones patrón; sustituir `PH_SLOPE` y `PH_INTERCEPT`
   en `src/main.cpp` y activar `PH_CALIBRATED`. De fábrica **no publica mediciones**
   para evitar presentar coeficientes de ejemplo como mediciones reales.
5. Ejecutar `pio run -d firmware/esp32`, después añadir `-t upload` para grabar.
   Abrir `pio device monitor -b 115200`.

El firmware sincroniza la hora por NTP antes de TLS, reintenta la conexión y
reserva secuencias NVS en lotes de 1000. El DS18B20 desconectado y el valor de
arranque 85 °C impiden publicar. Ante fallos, el controlador genera alarma de
datos ausentes. No se habilitan Secure Boot ni eFuses automáticamente.

El simulador y la placa representan la misma identidad por defecto: detener el
simulador antes de usar hardware. Para cambiar de emisor, usar una nueva identidad
con nuevas credenciales o migrar de forma controlada la secuencia persistente.
No borrar SQLite para eludir el control de repetición.
