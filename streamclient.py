import asyncio
from pynput import keyboard
from functools import partial
import sys

def on_press(writer, key):
    char = None
    try:
        char = key.char
        print(char)
        writer.write(char.encode())
    except AttributeError:
        if key == keyboard.Key.space:
            writer.write(" ".encode())
        if key == keyboard.Key.backspace:
            writer.write("<".encode())
        print('special key {0} pressed'.format(
            key))

def on_release(key):
    print('{0} released'.format(
        key))
    if key == keyboard.Key.esc:
        # Stop listener
        return False

async def tcp_echo_client(message):
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 8888)

    print(f'Send: {message!r}')
    writer.write(message.encode())
    await writer.drain()

    # data = await reader.read(100)
    # print(f'Received: {data.decode()!r}')




    with open("tmpout", "wb") as w:
        # Collect events until released
        with keyboard.Listener(
                on_press=partial(on_press, writer),
                on_release=on_release) as listener:
            listener.join()
    # stdread = asyncio.StreamReader()
    # pipe = sys.stdin
    # loop = asyncio.get_running_loop()
    # await loop.connect_read_pipe(lambda: asyncio.StreamReaderProtocol(stdread), pipe)
    # while True:
    #     ret = await stdread.readuntil(b' ')
    #     print(ret)
    #     writer.write(ret)
    await writer.drain()

    print('Close the connection')
    writer.close()
    await writer.wait_closed()

asyncio.run(tcp_echo_client('Hello World!'))