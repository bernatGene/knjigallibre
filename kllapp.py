from pathlib import Path
from functools import reduce
from operator import add
from typing import Any, Coroutine

from rich.console import RenderableType
from textual.app import App, ComposeResult
from textual.widgets import Static, RichLog
from textual.containers import Vertical
from textual.events import Key
from rich.text import Text
from rich.style import Style


class ScreenText(Static):
    def on_mount(self):
        with open("media/piknik/picnic_utf8.txt", "r") as read:
            # TODO: lines must be hardwrapped to min(80, vp W)
            # dynamically
            self.lines = read.read().splitlines()
        self.line_cursor = 0
        self.word_cursor = 0
        self.log("mounted")


    def display_text(self):
        half = max(self.container_size.height // 2, 4)
        self.log(self.container_size)
        self.log(self.container_viewport)
        self.log(self.size)
        self.log(self.window_region)
        self.log(half)
        l_cur = self.line_cursor
        top_h = max(l_cur - half, 0)
        bot_h = min(l_cur + half, len(self.lines))
        self.log(bot_h, top_h)
        lines_above = self.lines[top_h:l_cur]
        lines_above += ["~"] * (half - len(lines_above))
        self.log(lines_above)
        lines_below = self.lines[l_cur:bot_h]
        lines_below += ["~"] * (half - len(lines_below))
        self.log(lines_below)
        self.log(len(lines_above))
        self.log(len(lines_below))

        line_words = self.lines[l_cur].split()
        line_word_index = reduce(
            add, [len(w) + 1 for w in line_words[: self.word_cursor]], 0
        )
        word_char_index = (
            sum([len(l) for l in lines_above]) + len(lines_above) + line_word_index
        )
        text = Text("\n".join(lines_above + lines_below))
        text.stylize(
            Style(color="green"),
            word_char_index,
            word_char_index + len(line_words[: self.word_cursor]),
        )
        self.update(text)

    def on_key(self, event: Key) -> None:
        match event.key:
            case "j":
                self.line_cursor += 1
            case "k":
                self.line_cursor -= 1
            case "h":
                self.word_cursor += 1
            case "l":
                self.word_cursor -= 1
        self.log("L:", self.line_cursor, "W:", self.word_cursor)
        self.display_text()

class DebugLog(RichLog):
    pass


class KLlApp(App):
    CSS_PATH = "kllapp.tcss"
    def compose(self) -> ComposeResult:
        with Vertical():
            yield ScreenText("media/piknik/picnic_utf8.txt")

    def on_mount(self) -> None:
        main_text = self.query_one(ScreenText)
        main_text.focus()
        main_text.display_text()

    def on_key(self, event: Key) -> None:
        text = self.query_one(ScreenText)
        match event.key:
            case "j":
                text.line_cursor += 1
            case "k":
                text.line_cursor -= 1
            case "h":
                text.word_cursor += 1
            case "l":
                text.word_cursor -= 1
        self.log("L:", text.line_cursor, "W:", text.word_cursor)
        text.display_text()



if __name__ == "__main__":
    app = KLlApp()
    app.run()
