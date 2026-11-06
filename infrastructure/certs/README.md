# Material local (no versionar)

Ejecutar `bash scripts/init-lab.sh IP_DEBIAN` en Debian desde la raíz.
Genera una CA de laboratorio, certificado servidor con SAN IP/DNS,
contraseñas aleatorias por identidad y fichero Mosquitto con hashes.
Los clientes verifican la CA y el nombre del broker. No se usa `setInsecure`.

La CA privada y las claves quedan fuera de Git. Es una CA para la maqueta,
no una PKI de producción. La clave servidor solo puede leerla UID 1883;
las contraseñas cliente solo UID 10001 y root. La CA pública se copia al ESP32.
El directorio completo se monta únicamente en Mosquitto; el resto de
contenedores solo recibe su contraseña y la CA pública.
