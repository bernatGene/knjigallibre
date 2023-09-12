import asyncio
from datetime import datetime
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.style import Style
from rich.console import Console
from rich.logging import RichHandler
from rich.padding import Padding

from enum import IntFlag, auto
import logging
import os

class ParagraphCommand(IntFlag):
    NEXT_W = auto()
    PREV_W = auto()




class ConsolePanel(Console):
    def __init__(self,*args,**kwargs):
        console_file = open(os.devnull,'w')
        super().__init__(record=True,file=console_file,*args,**kwargs)

    def __rich_console__(self,console,options):
        lines = self.export_text(clear=False, styles=True).splitlines()
        for line in lines[-options.height:]:
            yield Text(line, justify="left")

from collections import deque

class LoggerFile():
    _instance = None
    def __init__(self):
        self.messages = deque(["sa"])
        self.size = 10

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance

    def write(self, message):
        print(message)
        self.messages.extend(message.splitlines())
        while len(self.messages) > self.size:
            self.messages.popleft()

    def flush(self):
        pass

    def render(self):
        return Panel(Text("\n".join(self.messages)))

from rich.highlighter import Highlighter

# class ConsoleHighligher(Highlighter):


FORMAT = "%(message)s"
class Display:
    def __init__(self, text) -> None:
        self.command_queue = asyncio.Queue()
        self.paragraph = Paragraph(text)
        self.logging_file = LoggerFile()
        self.console = ConsolePanel()
        self.handler = RichHandler(console=self.console, show_level=True, show_path=False)
        logging.basicConfig(level="NOTSET", format=FORMAT,  datefmt="[%X]", handlers=[self.handler]
        )
        self.log = logging.getLogger("caca")

    def make_layout(self) -> Layout:
        layout = Layout(name="root")
        layout.split_row(
            Layout(name="sidebar", minimum_size=15, ratio=2),
            Layout(name="main", minimum_size=80, ratio=5),
            Layout(name="debug", minimum_size=50, ratio=4)
        )
        layout["main"].split(
            Layout(name="header", size=3),
            Layout(name="paragraph", ratio=1),
            Layout(name="card"),
        )
        return layout
    
    async def display(self):
        layout = self.make_layout()
        layout["paragraph"].update(self.paragraph.get_text())
        layout["header"].update(Header())
        self.console.width = 250
        layout["debug"].update(Padding(self.console, (2, 4)))
        with Live(layout, auto_refresh=False) as live:
            while True:
                command = await self.command_queue.get()
                self.log.info("command, %d", command)
                self.paragraph.handle_command(command)
                layout["paragraph"].update(self.paragraph.get_text())
                layout["debug"].update(Padding(self.console, (2, 4)))
                live.update(layout)
                live.refresh()
    

class Paragraph:
    def __init__(self, text: str) -> None:
        self.windex = 0
        self.sindex = 0
        self.text_str = text
        self.sentences = text.split(".") # better use a regex
        self.words = []
        word = ""
        for idx, char in enumerate(self.text_str):
            if char == " ":
                self.words.append((word, idx - len(word)))
                word = ""
            else:
                word += char

    def get_text(self) -> Panel:
        text = Text(self.text_str)
        word, idx = self.words[self.windex]
        text.stylize(Style(bgcolor="green"), idx, idx + len(word))
        return Panel(text)
   
    def handle_command(self, command: ParagraphCommand):
        match command:
            case ParagraphCommand.NEXT_W:
                self.windex += 1
            case ParagraphCommand.PREV_W:
                self.windex -= 1


class Header:
    """Display header with clock."""

    def __rich__(self) -> Panel:
        grid = Table.grid(expand=True)
        grid.add_column(justify="center", ratio=1)
        grid.add_column(justify="right")
        grid.add_row(
            "[b]KnjigaLlibre[/b] Application",
            datetime.now().ctime().replace(":", "[blink]:[/]"),
        )
        return Panel(grid, style="white on blue")
