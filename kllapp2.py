from pathlib import Path
from textual import events, on

from textual.app import App, ComposeResult
from textual.message import Message
from textual.strip import Strip
from textual.widget import Widget
from textual.widgets import Static, Switch, Button
from textual.geometry import Size
from textual.containers import Vertical, Horizontal, VerticalScroll
from textual.scroll_view import ScrollView
from textual.events import Key
from rich.segment import Segment
from mediaplayer import MediaPlayer


class BookScroll(ScrollView):
    def __init__(
        self,
        source: Path,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False
    ) -> None:
        self.text = source.read_text().splitlines()
        super().__init__(
            *children, name=name, id=id, classes=classes, disabled=disabled
        )
        self.virtual_size = Size(78, len(self.text))

    class ScrolledBook(Message):
        def __init__(self, origin: str, offset: int) -> None:
            self.origin = origin
            self.offset = offset
            super().__init__()

    def _handle_scroll(self, event, down: bool):
        current = self.scroll_offset[1]
        target = current + self.app.scroll_sensitivity_y * (down * 2 - 1)
        self.post_message(self.ScrolledBook(self.id, target - current))
        self.log(current, target)

    def on_mouse_scroll_down(self, event: events.MouseScrollDown) -> None:
        event.stop()
        self._handle_scroll(event, True)

    def on_mouse_scroll_up(self, event: events.MouseScrollUp) -> None:
        event.stop()
        self._handle_scroll(event, False)

    def render_line(self, y: int) -> Strip:
        scroll_y = self.scroll_offset[1]
        y += scroll_y
        segments = [Segment(self.text[y])]
        strip = Strip(segments, len(self.text[y]))
        return strip


class KLlApp(App):
    CSS_PATH = "kllapp2.tcss"

    def compose(self) -> ComposeResult:
        self.media_player = MediaPlayer(list(Path("media/piknik").glob("*.mp4"))[0])
        with Horizontal():
            with Vertical(classes="sidebar"):
                yield Static("De/Couple scroll (C)")
                yield Switch(False, id="scroll_couple")
                yield Button(label="Play (P)", id="play_audio")
            yield BookScroll(Path("media/piknik/picnic_utf8.txt"), id="ru")
            yield BookScroll(Path("media/piknik/picnic_eng.txt"), id="en")
        
    def on_button_pressed(self) -> None:
        if self.media_player.is_playing():
            self.media_player.pause()
        else:
            self.media_player.play()

    
    @on(BookScroll.ScrolledBook)
    def scroll_sibling(self, event: BookScroll.ScrolledBook) -> None:
        if not self.query_one("#scroll_couple", Switch).value:
            return
        a, b = self.query(BookScroll)
        other = {a.id: b, b.id: a}
        other[event.origin].scroll_relative(y=event.offset)
        self.log("parent", event.origin, event.offset)

    def on_key(self, event: Key) -> None:
        pass
        # text_ru = self.query_one(ScreenText)
        # text_en = self.query_one(ScreenText)
        # match event.key:
        #     case "j":
        #         text.line_cursor += 1
        #     case "k":
        #         text.line_cursor -= 1
        #     case "h":
        #         text.word_cursor += 1
        #     case "l":
        #         text.word_cursor -= 1
        # self.log("L:", even.line_cursor, "W:", text.word_cursor)
        # text.display_text()


if __name__ == "__main__":
    app = KLlApp()
    app.run()
