import asyncio
from asyncio import Protocol, WriteTransport, StreamReader, StreamWriter

HOST = '127.0.0.1'
PORT = 7777


async def echo_connection_received(client_reader: StreamReader, client_writer: StreamWriter):
    print(f"Got a connection from {client_writer.get_extra_info('peername')}")
    while not client_reader.at_eof():
        data: bytes = await client_reader.readline()
        print(f"Received data: {data.decode()}")

        client_writer.write(data)
        await client_writer.drain()

    print("Closed")


loop = asyncio.get_event_loop()
loop.run_until_complete(
    asyncio.start_server(echo_connection_received, HOST, PORT))
loop.run_forever()
