#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ $# -ne 1 || ! $1 =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo 'Uso: sudo bash scripts/init-lab.sh IP_DEBIAN' >&2
  exit 1
fi
if [[ $EUID -ne 0 ]]; then echo 'Ejecutar con sudo (permisos UID contenedores).' >&2; exit 1; fi
command -v docker >/dev/null
command -v openssl >/dev/null
device_id=$(sed -n 's/^DEVICE_ID=//p' .env | tr -d '\r' | tail -n 1)
device_id=${device_id:-esp32-01}
[[ $device_id =~ ^[a-zA-Z0-9_-]{1,48}$ && $device_id != controller ]] || exit 1
cert_dir=infrastructure/certs
if [[ -e $cert_dir/ca.key || -e infrastructure/mosquitto/passwords ]]; then
  echo 'Ya hay secretos. No se sobrescriben. Para rotarlos, planificar la renovación de clientes.' >&2
  exit 1
fi
umask 077
mkdir -p "$cert_dir"
openssl req -x509 -newkey rsa:3072 -sha256 -nodes -days 3650 \
  -keyout "$cert_dir/ca.key" -out "$cert_dir/ca.crt" -subj '/CN=Ciberfisicos Lab CA' \
  -addext 'basicConstraints=critical,CA:TRUE' -addext 'keyUsage=critical,keyCertSign,cRLSign'
openssl req -new -newkey rsa:2048 -nodes -keyout "$cert_dir/server.key" \
  -out "$cert_dir/server.csr" -subj '/CN=mosquitto'
cat > "$cert_dir/server.ext" <<EOF
subjectAltName=DNS:mosquitto,DNS:localhost,IP:127.0.0.1,IP:$1
basicConstraints=critical,CA:FALSE
keyUsage=critical,digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth
EOF
openssl x509 -req -in "$cert_dir/server.csr" -CA "$cert_dir/ca.crt" \
  -CAkey "$cert_dir/ca.key" -CAcreateserial -days 365 -sha256 \
  -extfile "$cert_dir/server.ext" -out "$cert_dir/server.crt"
openssl rand -hex 24 > "$cert_dir/controller.password"
openssl rand -hex 24 > "$cert_dir/device.password"
printf 'controller:%s\n%s:%s\n' "$(cat "$cert_dir/controller.password")" \
  "$device_id" "$(cat "$cert_dir/device.password")" > infrastructure/mosquitto/passwords
# -U converts the plaintext entries to salted hashes, without passwords in argv.
docker run --rm --user 0:0 --entrypoint mosquitto_passwd \
  -v "$PWD/infrastructure/mosquitto:/config" eclipse-mosquitto:2.0.22 -U /config/passwords
chown 1883:1883 "$cert_dir/server.key" infrastructure/mosquitto/passwords
chmod 640 "$cert_dir/server.key" infrastructure/mosquitto/passwords
chown 10001:10001 "$cert_dir/controller.password" "$cert_dir/device.password"
chmod 400 "$cert_dir/controller.password" "$cert_dir/device.password"
chmod 755 "$cert_dir"
chmod 644 "$cert_dir/ca.crt" "$cert_dir/server.crt"
echo 'TLS y credenciales preparados. Guardar ca.key fuera de la VM si se desea renovar certificados.'
