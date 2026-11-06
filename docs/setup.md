# Puesta en marcha en Debian 13

VMware: 2–4 vCPU, 4–6 GB RAM, 40 GB disco, adaptador puente. Debian y ESP32
deben poder comunicarse; comprobar aislamiento de clientes Wi-Fi. No se crea una
VM automáticamente desde este repositorio.

## Herramientas

Instalar Docker Engine y Compose desde el
[repositorio oficial para Debian](https://docs.docker.com/engine/install/debian/),
además de `git`, `openssh-server`, `openssl`, `unzip`, `curl` y `ca-certificates`.
Verificar `sudo docker run --rm hello-world` y `sudo docker compose version`.
Los comandos siguientes se ejecutan en Debian desde la raíz del repositorio.

```bash
git clone https://github.com/juandf03/Ciberfisicos_Project.git
cd Ciberfisicos_Project
cp .env.example .env
```

Editar `.env`: `MQTT_BIND_IP` debe ser la IP LAN de Debian para hardware real.
Mantener `SCADA_BIND_IP=127.0.0.1`. `DEVICE_ID` debe coincidir en firmware,
simulador y controlador; establecerlo antes de crear las credenciales.

```bash
sudo bash scripts/init-lab.sh 192.168.1.50
sudo docker compose --env-file .env -f infrastructure/compose.yaml --profile simulation up -d --build
sudo docker compose --env-file .env -f infrastructure/compose.yaml logs -f controller
```

Sustituir la IP de ejemplo por la real. El primer comando genera secretos y
certificados sin sobrescribir instalaciones anteriores. Los ficheros generados
necesitan propietarios numéricos del contenedor; usar `sudo` como indica el script.
Si falla a mitad, revisar los ficheros creados antes de reintentar.

En los logs deben aparecer lecturas aceptadas cada 5 s. La conexión MQTT se
reintenta mientras arranca Mosquitto. Aún no hay interfaz web si no se ha activado
ScadaBR. Seguir [scadabr.md](scadabr.md) para supervisión.

## Comprobar todo el flujo

Una vez arrancado el simulador y el controlador:

```bash
sudo docker compose --env-file .env -f infrastructure/compose.yaml exec controller python -c \
'from pymodbus.client import ModbusTcpClient; c=ModbusTcpClient("localhost", port=1502); assert c.connect(); r=c.read_input_registers(0,count=6,device_id=1); print(r); assert not r.isError(); assert r.registers[3] == 1; c.close()'
```

Detener el simulador y esperar más de 30 s:

```bash
sudo docker compose --env-file .env -f infrastructure/compose.yaml --profile simulation stop simulator
```

Repetir la lectura (sin la aserción de calidad igual a 1): el bit 8 debe estar
activo y la calidad debe ser 0. Reiniciar el simulador con `--profile simulation
up -d simulator`; la secuencia persistida permite continuar.

## Uso del ESP32

Detener el simulador. Seguir [hardware.md](hardware.md) para la placa, calibración
y credenciales. Planificar el cambio de identidad/secuencia: no ejecutar los dos
emisores con la misma identidad. No borrar los volúmenes con `down -v`: contienen
la secuencia antirrepetición y el histórico de ScadaBR.

## Pruebas de desarrollo

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest -q
docker compose --env-file .env.example -f infrastructure/compose.yaml --profile simulation --profile scada config --quiet
```

En Windows usar Python 3.12 y `.venv\Scripts\python.exe -m pytest -q`.
La CI comprueba Python, configuración Compose, compilación PlatformIO con
credenciales ficticias y el flujo Docker simulador → MQTT TLS → Modbus, incluido
el watchdog. Se puede repetir en Debian con `sudo bash scripts/verify-pipeline.sh`
después de generar los secretos. No certifica el montaje físico ni la configuración HMI.

## Operación

Restringir SSH a los administradores y 8883 a la red de laboratorio. Los puertos
publicados por Docker requieren revisar sus reglas propias; no confiar solo en
UFW. Actualizar y revisar imágenes antes de exponer el laboratorio. Hacer copia
coherente de los volúmenes con los servicios detenidos; almacenar fuera de Git.

Si cambia la IP de Debian, renovar el certificado SAN y distribuir la nueva CA
solo si se ha cambiado la CA. Mantener hora sincronizada y comprobar caducidad
con `openssl x509 -in infrastructure/certs/server.crt -noout -dates`.
