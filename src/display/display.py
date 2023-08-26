import asyncio
from datetime import datetime
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.style import Style

from enum import IntFlag, auto


class ParagraphCommand(IntFlag):
    NEXT_W = auto()
    PREV_W = auto()

class Display:
    def __init__(self, text) -> None:
        self.command_queue = asyncio.Queue()
        self.paragraph = Paragraph(text)

    def make_layout(self) -> Layout:
        layout = Layout(name="root")
        layout.split_row(
            Layout(name="sidebar", size=15),
            Layout(name="main", ratio=1),
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
        with Live(layout, auto_refresh=False) as live:
            while True:
                command = await self.command_queue.get()
                self.paragraph.handle_command(command)
                layout["paragraph"].update(self.paragraph.get_text())
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

    def get_text(self) -> Text:
        text = Text(self.text_str)
        word, idx = self.words[self.windex]
        text.stylize(Style(bgcolor="green"), idx, idx + len(word))
        print(idx + len(word))
        return text
   
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
            "[b]Rich[/b] Layout application",
            datetime.now().ctime().replace(":", "[blink]:[/]"),
        )
        return Panel(grid, style="white on blue")
