import asyncio
import socket
from config import SOCKET_PORT
# Track raw socket clients
socket_clients = set()

async def start_socket_server(host='0.0.0.0', port=SOCKET_PORT):
    server = await asyncio.start_server(handle_raw_client, host, port)
    print(f"[Socket] Server running on {host}:{port}")
    async with server:
        await server.serve_forever()

async def handle_raw_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"[Socket] Client connected: {addr}")
    socket_clients.add(writer)

    try:
        while True:
            data = await reader.read(100)
            if not data:
                break
            # Optionally handle client messages here
    except Exception as e:
        print(f"[Socket] Error: {e}")
    finally:
        print(f"[Socket] Client disconnected: {addr}")
        socket_clients.remove(writer)
        writer.close()
        await writer.wait_closed()