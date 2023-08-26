import asyncio
from pynput import keyboard
from functools import partial
import sys


def on_press(writer, key):
    char = None
    try:
        char = key.char
        # print(char)
        writer.write(char.encode())
    except AttributeError:
        if key == keyboard.Key.space:
            writer.write(" ".encode())
        if key == keyboard.Key.backspace:
            writer.write("<".encode())
        # print("special key {0} pressed".format(key))


def on_release(key):
    # print("{0} released".format(key))
    if key == keyboard.Key.esc:
        # Stop listener
        return False


async def tcp_echo_client(message):
    reader, writer = await asyncio.open_connection("127.0.0.1", 8888)

    # print(f"Send: {message!r}")
    writer.write(message.encode())
    await writer.drain()

    with keyboard.Listener(
        on_press=partial(on_press, writer), on_release=on_release, suppress=True
    ) as listener:
        listener.join()

    print("Close the connection")
    writer.close()
    await writer.wait_closed()


asyncio.run(tcp_echo_client("Hello World!"))
