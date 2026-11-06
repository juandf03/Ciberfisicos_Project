"""Only FC04 input registers are exposed. All remote writes are rejected."""
import asyncio

from pymodbus.constants import ExcCodes
from pymodbus.datastore import ModbusDeviceContext, ModbusSequentialDataBlock, ModbusServerContext
from pymodbus.server import StartAsyncTcpServer


class ReadOnlyDevice(ModbusDeviceContext):
    def getValues(self, func_code, address, count=1):
        if func_code != 4:
            return ExcCodes.ILLEGAL_FUNCTION
        return super().getValues(func_code, address, count)

    def setValues(self, func_code, address, values):
        return ExcCodes.ILLEGAL_FUNCTION


def create_context(state):
    # PyModbus 3.11 adds one to protocol addresses inside ModbusDeviceContext.
    block = ModbusSequentialDataBlock(1, state.registers())
    device = ReadOnlyDevice(ir=block)
    return ModbusServerContext(devices={1: device}, single=False), block


async def serve(state, host="0.0.0.0", port=1502):
    context, block = create_context(state)

    async def refresh():
        while True:
            block.setValues(1, state.registers())
            await asyncio.sleep(1)

    task = asyncio.create_task(refresh())
    try:
        await StartAsyncTcpServer(context=context, address=(host, port))
    finally:
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
