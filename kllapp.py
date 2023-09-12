from typing import Any, Coroutine
from textual.app import App, ComposeResult
from textual.widgets import Static, RichLog
from textual.events import Key
from rich.text import Text
from rich.style import Style

class TextLoader:
    def __init__(self, full_text_path) -> None:
        self.full_text_path
        self.cursor = 0
    
    def next_paragraph(self):
        with open(self.full_text_path, "r") as read:
            pass





    


class Paragraph(Static):
    def load_text(self, text_str):
        self.text_str = text_str
        self.renderable = Text(text_str)
        self.windex = 0
        self.sindex = 0
        self.sentences = text_str.split(".")  # better use a regex
        self.words = []
        word = ""
        for idx, char in enumerate(self.text_str):
            if char == " ":
                self.words.append((word, idx - len(word)))
                word = ""
            else:
                word += char

    def update_renderable(self):
        text = Text(self.text_str)
        word, idx = self.words[self.windex]
        text.stylize(Style(color="green"), idx, idx + len(word))
        self.update(text)


    def on_key(self, event: Key) -> None:
        match event.key:
            case "j":
                self.windex += 1
            case "k":
                self.windex -= 1
        self.update_renderable()

class DebugLog(RichLog):
    pass

class KLlApp(App):
    def compose(self) -> ComposeResult:
        yield Paragraph(id="maintxt")
        # yield DebugLog()

    def on_mount(self) -> None:
        main_text = self.query_one(Paragraph)
        main_text.focus()
        with open("media/sample_text.txt", "r") as read:
        # with open("media/piknik/picnic_utf8.txt", "r") as read:
            main_text.load_text(read.read())
            main_text.update_renderable()

    def on_key(self, event: Key) -> None:
        text = self.query_one(Paragraph)
        # debug = self.query_one(DebugLog)
        match event.key:
            case "j":
                text.windex += 1
            case "k":
                text.windex -= 1
            case "space":
                text.sindex += 1
            case "shift+space":
                text.sindex -= 1
        text.update_renderable()
        # debug.write(event)



if __name__ == "__main__":
    app = KLlApp()
    app.run()
