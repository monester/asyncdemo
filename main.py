import asyncio
from asyncio import Protocol, WriteTransport, StreamReader, StreamWriter

HOST = '127.0.0.1'
PORT = 7777


async def list_active():
    while True:
        print(asyncio.Task.all_tasks())
        await asyncio.sleep(1)


async def bug():
    await asyncio.sleep(3)
    print(1/0)

async def echo_connection_received(client_reader: StreamReader, client_writer: StreamWriter):
    print(f"Got a connection from {client_writer.get_extra_info('peername')}")
    loop.create_task(bug())
    while not client_reader.at_eof():
        data: bytes = await client_reader.readline()
        print(f"Received data: {data.decode()}")

        client_writer.write(data)
        await client_writer.drain()

    print("Closed")


loop = asyncio.get_event_loop()
loop.create_task(list_active())
loop.run_until_complete(
    asyncio.start_server(echo_connection_received, HOST, PORT))
loop.run_forever()
