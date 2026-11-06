#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
compose=(docker compose --env-file .env -f infrastructure/compose.yaml --profile simulation)
"${compose[@]}" up -d --build mosquitto controller simulator
ready=false
for attempt in {1..30}; do
  if "${compose[@]}" exec -T controller python -c '
from pymodbus.client import ModbusTcpClient
c = ModbusTcpClient("localhost", port=1502, timeout=2)
assert c.connect()
try:
    r = c.read_input_registers(0, count=6, device_id=1)
    assert not r.isError() and r.registers[3] == 1, str(r)
    assert 2000 <= r.registers[0] <= 3000 and 650 <= r.registers[1] <= 850
finally:
    c.close()
'; then
    ready=true
    break
  fi
  sleep 2
done
[[ $ready == true ]] || { "${compose[@]}" logs; exit 1; }
"${compose[@]}" stop simulator
sleep 35
"${compose[@]}" exec -T controller python -c '
from pymodbus.client import ModbusTcpClient
c = ModbusTcpClient("localhost", port=1502)
assert c.connect()
try:
    r = c.read_input_registers(0, count=6, device_id=1)
    assert not r.isError() and r.registers[2] & 8 and r.registers[3] == 0, str(r)
finally:
    c.close()
'
"${compose[@]}" start simulator
echo 'Flujo simulador → MQTT TLS → controlador → Modbus y watchdog comprobados.'
