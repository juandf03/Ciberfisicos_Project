# ScadaBR clásico 1.2

Los comandos Bash de esta guía y el build se ejecutan en la **VM Debian**, donde
están Docker y todos los servicios. El WAR debe descargarse en la copia del
repositorio de Debian. Windows solo necesita SSH y navegador para la HMI.

Se mantiene **ScadaBR clásico**, exigido por el profesor. Su
[documentación oficial](https://github.com/ScadaBR/ScadaBR/blob/master/README.md)
indica Java 8, Tomcat 9 y Derby por defecto. No se utiliza Scada-LTS.

## Paquete oficial e imagen propia

Descargar el WAR desde la publicación oficial:

```bash
curl --fail --location --proto '=https' --tlsv1.2 \
  https://github.com/ScadaBR/ScadaBR/releases/download/v1.2/ScadaBR.war \
  -o infrastructure/scadabr/vendor/ScadaBR.war
sha256sum infrastructure/scadabr/vendor/ScadaBR.war
```

Registrar el hash, origen y fecha de descarga en las evidencias. Un hash calculado
localmente sirve para identificar el artefacto; no equivale a una firma del autor.
El WAR permanece fuera de Git. La imagen propia usa Tomcat 9/Java 8, extrae la
aplicación y configura Derby en `/opt/scadabr-data`, un volumen persistente.
El build falla si no encuentra la propiedad de conexión esperada.

```bash
sudo docker compose --env-file .env -f infrastructure/compose.yaml --profile scada up -d --build
```

Acceder desde Windows mediante un túnel SSH:

```powershell
ssh -L 8080:127.0.0.1:8080 usuario@IP_DEBIAN
```

Abrir `http://localhost:8080/ScadaBR/`. Cambiar inmediatamente las credenciales
iniciales del paquete y crear usuarios separados de administración y consulta.
No publicar esta interfaz HTTP en la LAN sin una capa HTTPS y control de acceso.

## Fuente de datos real

1. Crear una fuente **Modbus IP/TCP**, host `controller`, puerto `1502`, unidad `1`,
   periodo de consulta 5 s.
2. Crear puntos **Input Register** (función 04) de acuerdo con el
   [mapa Modbus](architecture.md). Los offsets del mapa empiezan en cero;
   comprobar la convención mostrada por la interfaz y contrastar con la lectura
   CLI antes de asumir que una referencia 30001 corresponde al offset 0.
3. Temperatura: entero 16 bits con signo y multiplicador 0,01; pH: entero sin
   signo y multiplicador 0,01. Alarmas, calidad, edad y secuencia: enteros sin signo.
4. Activar registro histórico y una lista de vigilancia con temperatura y pH.
5. Crear gráfico de tendencias y detectores de límites (20–30 °C, 6,5–8,5 pH).
6. Crear detector de calidad igual a 0 y mostrar la máscara de alarmas. Un valor
   antiguo no debe interpretarse como una medida actual aunque siga visible.
7. Para la fase inicial sin controlador se pueden crear dos puntos virtuales;
   identificarlos como simulados y separarlos de la fuente Modbus real.

Exportar la configuración como JSON desde ScadaBR, revisar que no contenga
secretos y guardarla en `infrastructure/scadabr/`. Capturas en `docs/screenshots/`.
La configuración interactiva y el dashboard deben realizarse en la instancia;
no se incluyen exportaciones ficticias ni se dan por configurados.

## Estado de validación

El arranque de esta imagen, la persistencia Derby y la conexión desde la HMI
necesitan comprobarse en Debian con Docker. Las pruebas Python verifican el
servidor Modbus, pero no sustituyen esa comprobación. Los tags de imágenes deben
actualizarse y fijarse a digest tras validar la instalación de entrega.
