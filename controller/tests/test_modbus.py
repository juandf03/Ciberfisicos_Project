import asyncio
import socket

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.server import ModbusTcpServer

from app.modbus_server import create_context
from app.state import TelemetryState


def test_real_modbus_read_and_write_rejection(tmp_path):
    async def scenario():
        state = TelemetryState(str(tmp_path / "state.sqlite"), "esp32-01")
        context, _ = create_context(state)
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]
        server = ModbusTcpServer(context, address=("127.0.0.1", port))
        task = asyncio.create_task(server.serve_forever())
        client = AsyncModbusTcpClient("127.0.0.1", port=port)
        try:
            for _ in range(30):
                if await client.connect():
                    break
                await asyncio.sleep(0.05)
            assert client.connected
            reply = await client.read_input_registers(0, count=6, device_id=1)
            assert not reply.isError()
            assert reply.registers == [0, 0, 8, 0, 65535, 0]
            reply = await client.write_register(0, 1234, device_id=1)
            assert reply.isError()
            reply = await client.read_holding_registers(0, count=1, device_id=1)
            assert reply.isError()
            reply = await client.read_input_registers(6, count=1, device_id=1)
            assert reply.isError()
        finally:
            client.close()
            await server.shutdown()
            await task
            state.close()
    asyncio.run(scenario())
