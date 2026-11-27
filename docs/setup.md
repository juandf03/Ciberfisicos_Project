# Puesta en marcha en Kali Linux 2026.3

**Docker Engine, Compose y todos los contenedores se ejecutan dentro de la VM
Kali**, incluyendo Mosquitto, controlador Python, ScadaBR y simulador Python.
Windows aloja VirtualBox, el editor, Wokwi, el navegador y las herramientas para
grabar la placa por USB. Disponemos de un ESP32 físico; no se sustituye por Wokwi.

Asignación orientativa: 2–4 vCPU, 4–6 GB de RAM y 40 GB de disco. En VirtualBox,
abrir **Configuración → Red → Adaptador 1** y seleccionar **Adaptador puente**
sobre la interfaz física del anfitrión conectada a la LAN. Kali y el ESP32
deben poder comunicarse; comprobar aislamiento de clientes Wi-Fi. No se crea una
VM automáticamente desde este repositorio.

## Herramientas

En una VM Kali recién instalada, ejecutar los comandos siguientes **en Kali**:

```bash
sudo apt update
sudo apt install -y git openssh-server openssl unzip curl ca-certificates nano python3-venv
sudo systemctl enable --now ssh
sudo apt install -y docker.io docker-compose docker-buildx
sudo systemctl enable --now docker
sudo docker run --rm hello-world
sudo docker compose version
cat /etc/os-release
ip -br -4 addr
timedatectl status
```

La instalación usa los paquetes de Kali. Si Docker ya está instalado, comprobar
su versión y la de Compose antes de instalar paquetes. Mantener la hora
sincronizada. Reservar la IP LAN de Kali y comprobar el acceso SSH desde Windows.
[Guía de Docker en Kali](https://www.kali.org/docs/containers/installing-docker-on-kali/)
y [paquete Compose](https://pkg.kali.org/pkg/docker-compose). No instalar Docker en Windows
para seguir este despliegue.

Los comandos restantes se ejecutan desde la raíz del repositorio en Kali.

```bash
git clone https://github.com/juandf03/Ciberfisicos_Project.git
cd Ciberfisicos_Project
cp .env.example .env
```

Editar `.env`: `MQTT_BIND_IP` debe ser la IP LAN de Kali para hardware real.
Mantener `SCADA_BIND_IP=127.0.0.1`. `DEVICE_ID` debe coincidir en firmware,
simulador y controlador; establecerlo antes de crear las credenciales.

```bash
sudo bash scripts/init-lab.sh 192.168.1.50
sudo docker compose --env-file .env -f infrastructure/compose.yaml up -d --build mosquitto controller
sudo docker compose --env-file .env -f infrastructure/compose.yaml logs -f controller
```

Sustituir la IP de ejemplo por la real. El primer comando genera secretos y
certificados sin sobrescribir instalaciones anteriores. Los ficheros generados
necesitan propietarios numéricos del contenedor; usar `sudo` como indica el script.
Si falla a mitad, revisar los ficheros creados antes de reintentar.

El despliegue principal utiliza el ESP32 físico. Sin un emisor conectado, los
servicios pueden estar arrancados con calidad 0 y alarma de ausencia. Una vez
configurada/calibrada la placa, los logs deben mostrar lecturas aceptadas cada
5 s. La conexión MQTT se reintenta mientras arranca Mosquitto. Aún no hay interfaz
web si no se ha activado ScadaBR. Seguir [scadabr.md](scadabr.md) para supervisión.

Para pruebas con datos sintéticos, el perfil `simulation` arranca el simulador
Python. Usarlo con identidad/despliegue de ensayo separado, no con la identidad
del ESP32 físico. Wokwi es otra fase: ver [wokwi.md](wokwi.md).

## Comprobar todo el flujo

Una vez conectado el ESP32 físico o arrancado un simulador en un entorno de ensayo:

```bash
sudo docker compose --env-file .env -f infrastructure/compose.yaml exec controller python -c \
'from pymodbus.client import ModbusTcpClient; c=ModbusTcpClient("localhost", port=1502); assert c.connect(); r=c.read_input_registers(0,count=6,device_id=1); print(r); assert not r.isError(); assert r.registers[3] == 1; c.close()'
```

Desconectar el ESP32 y esperar más de 30 s. Si se está usando el simulador Python,
detenerlo con:

```bash
sudo docker compose --env-file .env -f infrastructure/compose.yaml --profile simulation stop simulator
```

Repetir la lectura (sin la aserción de calidad igual a 1): el bit 8 debe estar
activo y la calidad debe ser 0. Reconectar la placa o, en el entorno simulado,
reiniciar el emisor con `sudo docker compose --env-file .env -f infrastructure/compose.yaml --profile simulation up -d simulator`.
La secuencia persistida permite continuar con el mismo emisor.

## Uso del ESP32

Si estaba arrancado, detener el simulador. Seguir [hardware.md](hardware.md) para la placa, calibración
y credenciales. Planificar el cambio de identidad/secuencia: no ejecutar los dos
emisores con la misma identidad. No borrar los volúmenes con `down -v`: contienen
la secuencia antirrepetición y el histórico de ScadaBR.

## Pruebas de desarrollo

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest -q
sudo docker compose --env-file .env.example -f infrastructure/compose.yaml --profile simulation --profile scada config --quiet
```

En Windows usar Python 3.12 y `.venv\Scripts\python.exe -m pytest -q`.
La CI comprueba Python, configuración Compose, compilación PlatformIO con
credenciales ficticias y el flujo Docker simulador → MQTT TLS → Modbus, incluido
el watchdog. Se puede repetir en Kali con `sudo bash scripts/verify-pipeline.sh`
después de generar los secretos en un entorno de ensayo separado de la adquisición
real. No certifica el montaje físico ni la configuración HMI.

## Operación

Restringir SSH a los administradores y 8883 a la red de laboratorio. Los puertos
publicados por Docker requieren revisar sus reglas propias; no confiar solo en
UFW. Actualizar y revisar imágenes antes de exponer el laboratorio. Hacer copia
coherente de los volúmenes con los servicios detenidos; almacenar fuera de Git.

Si cambia la IP de Kali, renovar el certificado SAN y distribuir la nueva CA
solo si se ha cambiado la CA. Mantener hora sincronizada y comprobar caducidad
con `openssl x509 -in infrastructure/certs/server.crt -noout -dates`.
