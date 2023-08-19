import asyncio
import time

from rich import print
from rich.live import Live
from rich.text import Text
from rich.style import Style


def paragraph(word="") -> Text:
    text = Text(" ".join([f"text{i}" for i in range(100)]))
    style_high = Style(bgcolor="red")
    text.highlight_regex(f"{word}", style=style_high)
    return text


class TypingTest:
    def __init__(self, text: str) -> None:
        self.index = 0
        self.text_str = text
        self.cursor = 0
        self.missed = set()
        self.ts0 = 0

    def start(self):
        self.ts0 = time.time()

    def stop(self):
        elapsed = time.time() - self.ts0
        cpm = len(self.text_str) / elapsed
        wpm = round((cpm / 5) * 60)
        print(f"Speed: {cpm:.1f} chars / s, {wpm} wpm")
        print(f"Accuracy: {1 - (len(self.missed) / len(self.text_str)):.2f}")

    def get_text(self) -> Text:
        text = Text(self.text_str)
        text.stylize(Style(bgcolor="green"), 0, self.index)
        for miss in self.missed:
            text.stylize(Style(bgcolor="red"), miss, miss + 1)
        text.stylize(Style(bgcolor="blue"), self.index, self.index + 1)
        return text

    def char_input(self, char: str):
        if self.index == 0:
            self.start()
        elif self.index == len(self.text_str):
            self.stop()
            self.__init__(self.text_str)
            return
        if char == "<":
            self.index -= 1
            try:
                self.missed.remove(self.index)
            except KeyError:
                pass
            return
        if char != self.text_str[self.index]:
            self.missed.add(self.index)
        self.index += 1


async def handle_echo(reader, writer: asyncio.StreamWriter):
    data = await reader.read(100)
    message = data.decode()
    addr = writer.get_extra_info("peername")
    print(f"Received {message!r} from {addr!r}")
    ttest = TypingTest(
        "Just some words to experiment with this. Use Rich to make your command line applications visually appealing and present data in a more readable way"
    )
    with Live(ttest.get_text(), refresh_per_second=10) as live:
        while True:
            data = await reader.read(100)
            message = data.decode()
            ttest.char_input(message)
            live.update(ttest.get_text())
            if data == b"":
                break


async def run(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await proc.communicate()

    # print(f"[{cmd!r} exited with {proc.returncode}]")
    # if stdout:
    #     print(f"[stdout]\n{stdout.decode()}")
    # if stderr:
    #     print(f"[stderr]\n{stderr.decode()}")


async def main():
    server = await asyncio.start_server(handle_echo, "127.0.0.1", 8888)

    addrs = ", ".join(str(sock.getsockname()) for sock in server.sockets)
    print(f"Serving on {addrs}")

    async with server:
        await asyncio.gather(
            run("python typtestclient.py"),
            server.serve_forever(),
        )


asyncio.run(main())
