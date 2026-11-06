# Pruebas con hardware

La compilación CI usa únicamente `secrets.example.h`; nunca credenciales reales.
Antes de publicar datos reales: verificar DS18B20 desconectado/85 °C, calibrar pH
con al menos dos soluciones patrón, comprobar tensión máxima ADC, pérdida de Wi-Fi,
CA incorrecta y reinicio con continuidad de secuencia NVS. Guardar evidencias en
`security/test-results/`. No se han ejecutado estas pruebas sobre una placa real.
