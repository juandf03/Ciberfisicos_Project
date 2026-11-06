# Wokwi: plan de integración y escalabilidad

## Alcance

Disponemos de un ESP32 físico. Wokwi representará dispositivos adicionales para
estudiar varios tanques. Broker, controlador, ScadaBR y Docker permanecerán en
la VM Debian. Esta guía es un **plan**: todavía no hay `diagram.json`,
`wokwi.toml`, firmware específico de simulación ni controlador multinodo.
No se han ejecutado simulaciones Wokwi. El simulador Python solo genera mensajes;
no ejecuta el firmware.

## Conectividad

Se propone Wokwi para VS Code en Windows, con su gateway integrado para acceder
a la LAN. En la versión web, el gateway público no alcanza la red local; el
privado requiere la modalidad que lo permita. Usar `Wokwi-GUEST` con contraseña
vacía para los nodos virtuales, conservando la Wi-Fi real en la placa física.
Referencias: [red ESP32](https://docs.wokwi.com/guides/esp32-wifi) y
[gateway VS Code](https://docs.wokwi.com/vscode/project-config#iot-gateway-esp32-wifi).

El broker será `IP_DEBIAN:8883`, con esa IP en SAN y verificación de CA activa.
No publicar el broker en Internet para resolver la conectividad. Cada nodo
necesita identidad y credencial de ensayo propias. No publicar contraseñas ni
binarios con credenciales reutilizables en proyectos compartidos.

## Hito 1: un nodo virtual aislado

1. Preparar una identidad de pruebas, por ejemplo `esp32-wokwi-01`, separada de
   la física. El script actual genera una identidad por despliegue y no añade
   nuevos usuarios a una instalación existente.
2. Crear circuito con ESP32, DS18B20 en GPIO 4 y señal analógica ajustable en
   GPIO 34 para representar el módulo pH. No equivale a simular la química de
   una sonda ni a calibrar la placa real.
3. Crear `diagram.json` y `wokwi.toml` en el proyecto de firmware, apuntando al
   `.bin` y `.elf` de PlatformIO. Compilar antes de iniciar. Referencia:
   [configuración oficial](https://docs.wokwi.com/vscode/project-config).
4. Separar parámetros físicos y virtuales: Wi-Fi, identidad, credencial y
   conversión de la señal de ensayo. El firmware con `PH_CALIBRATED=false` no
   publica: necesita un modo de ensayo explícito sin activar una calibración
   ficticia en el firmware destinado a la placa real.
5. Verificar TLS, lectura aceptada, calidad 1 y calidad 0 al parar la simulación.
6. Reiniciar Wokwi y comprobar secuencias. Si se reinicia su flash/NVS, el
   controlador puede rechazar el contador reutilizado. Diseñar persistencia
   o alta de nueva identidad, manteniendo la protección del controlador.

## Hito 2: coexistencia con el hardware real

Diseño propuesto, **pendiente de implementar**:

| Identidad | Origen | Topic |
|---|---|---|
| `esp32-01` | Placa física | `farm/esp32-01/telemetry` |
| `esp32-wokwi-01` | Simulación 1 | `farm/esp32-wokwi-01/telemetry` |
| `esp32-wokwi-02` | Simulación 2 | `farm/esp32-wokwi-02/telemetry` |

Ampliar el controlador con un registro explícito de nodos autorizados y estado
por identidad. Debe comprobar que el nodo del topic coincide con el payload y
aplicar validación, secuencia, calidad y alarmas de forma independiente.

También hay que provisionar nuevas credenciales Mosquitto sin sobrescribir las
existentes, conservar secuencias por nodo en SQLite y crear mapas Modbus y puntos
ScadaBR estables. Un topic comodín por sí solo no implementa estos cambios.

Una opción es asignar una unidad Modbus fija por nodo y conservar sus seis
registros actuales. Es una propuesta a validar con ScadaBR; el servidor actual
solo expone unidad 1. Documentar las asignaciones antes de implementarlas.

Otra opción es un controlador por nodo, cada uno con client ID MQTT, configuración,
volumen y destino Modbus propios. `--scale controller` con la configuración actual
duplicaría el client ID `farm-controller` y compartiría parámetros y base de datos.

## Hito 3: medir escalabilidad

Probar incrementos acordados, por ejemplo 1, 3 y 5 nodos. Validar primero las
posibilidades del entorno/cuenta para simulaciones simultáneas: no asumir que un
único circuito admite cualquier número de ESP32.

| Experimento | Evidencia |
|---|---|
| Cada nodo publica cada 5 s | Mensajes enviados/aceptados, secuencias perdidas y carga |
| Más nodos simultáneos | CPU/RAM de VM y contenedores, errores y estabilidad |
| Detener un nodo | Solo ese nodo genera calidad 0 y alarma de ausencia |
| Repetir un mensaje | Rechazo sin afectar a otros nodos |
| Usar topic ajeno | ACL impide escritura; no se acepta la lectura |
| Reiniciar controlador/nodos | Persistencia independiente y recuperación |
| Cambiar una señal virtual | Se actualiza el punto correcto en ScadaBR |

Separar latencia de llegada al controlador y de visualización HMI, que depende
del refresco Modbus y consulta SCADA. Sin relojes sincronizados, el timestamp
no mide latencia unidireccional con precisión. La simulación funcional no demuestra
capacidad real de radio, precisión química ni capacidad industrial a gran escala.
