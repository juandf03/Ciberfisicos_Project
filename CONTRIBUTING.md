# Trabajo en equipo

`main`: estable. `develop`: integración. Trabajar en `feature/esp32-sensors`,
`feature/controller`, `feature/scada-dashboard` o `feature/security` según tarea.

```bash
git switch develop
git pull --ff-only
git switch -c feature/mi-tarea
# implementar y verificar
git add ruta/archivo
git commit -m "Describe el cambio"
git push -u origin feature/mi-tarea
```

Abrir PR hacia `develop`, revisar y ejecutar CI. Integrar entregas estables hacia
`main`. No forzar push en ramas compartidas. Actualizar documentación y evidencias
cuando cambie el contrato MQTT, mapa Modbus, hardware o controles de seguridad.
Configurar repositorio privado, colaboradores y protección de ramas en GitHub;
estas opciones no se cambian automáticamente desde el código.
