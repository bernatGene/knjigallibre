from pathlib import Path
from rich.console import RenderableType

from textual.reactive import reactive
from textual import events, on
from textual.app import App, ComposeResult
from textual.message import Message
from textual.strip import Strip
from textual.widget import Widget
from textual.widgets import Static, Switch, Button, Label
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
        disabled: bool = False,
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

    def _handle_scroll(self, down: bool):
        current = self.scroll_offset[1]
        target = current + self.app.scroll_sensitivity_y * (down * 2 - 1)
        self.post_message(self.ScrolledBook(self.id, target - current))
        self.log(current, target)

    def on_mouse_scroll_down(self, event: events.MouseScrollDown) -> None:
        event.stop()
        self._handle_scroll(True)

    def on_mouse_scroll_up(self, event: events.MouseScrollUp) -> None:
        event.stop()
        self._handle_scroll(False)

    def render_line(self, y: int) -> Strip:
        scroll_y = self.scroll_offset[1]
        y += scroll_y
        segments = [Segment(self.text[y])]
        strip = Strip(segments, len(self.text[y]))
        return strip


class MediaPlayerControl(Static):
    media_player = MediaPlayer(sorted(list(Path("media/piknik").glob("*.mp4")))[0])
    curr_time = reactive(media_player.get_str_time())

    def on_mount(self) -> None:
        self.update_timer = self.set_interval(1 / 10, self.update_time, pause=True)

    def compose(self) -> ComposeResult:
        yield Button(label="⏮", id="seek_b", classes="media_button")
        yield Button(label="⏯", id="play_pause", classes="media_button")
        yield Button(label="⏭", id="seek_f", classes="media_button")
        yield Label()

    def update_time(self):
        if not self.media_player.is_playing:
            return
        self.curr_time = self.media_player.get_str_time()

    def watch_curr_time(self, new_time):
        self.query_one(Label).update(new_time)

    def play_pause(self):
        if self.media_player.is_playing():
            self.media_player.pause()
            self.update_timer.pause()
        else:
            self.media_player.play()
            self.update_timer.resume()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.curr_time = self.media_player.get_str_time()
        ts = self.media_player.get_time()
        seek_time = 5000
        match event.button.id:
            case "seek_b":
                self.media_player.set_time(ts - seek_time)
            case "seek_f":
                self.media_player.set_time(ts + seek_time)
            case "play_pause":
                self.play_pause()


class KLlApp(App):
    CSS_PATH = "kllapp2.tcss"

    def compose(self) -> ComposeResult:
        with Horizontal():
            with Vertical(id="sidebar", classes="sidebar"):
                yield Static("De/Couple scroll (C)")
                yield Switch(False, id="scroll_couple")
                yield MediaPlayerControl(id="mediacontrol")
            yield BookScroll(Path("media/piknik/picnic_utf8.txt"), id="ru")
            yield BookScroll(Path("media/piknik/picnic_eng.txt"), id="en")

    @on(BookScroll.ScrolledBook)
    def scroll_sibling(self, event: BookScroll.ScrolledBook) -> None:
        if not self.query_one("#scroll_couple", Switch).value:
            return
        a, b = self.query(BookScroll)
        other = {a.id: b, b.id: a}
        other[event.origin].scroll_relative(y=event.offset)
        self.log("parent", event.origin, event.offset)

    def on_key(self, event: Key) -> None:
        match event.key:
            case "h":
                self.query_one("#seek_b", Button).action_press()
            case "space":
                self.query_one("#play_pause", Button).action_press()
            case "l":
                self.query_one("#seek_f", Button).action_press()
            case "j":
                self.query_one("#ru", BookScroll)._handle_scroll(down=True)
            case "k":
                self.query_one("#ru", BookScroll)._handle_scroll(down=False)


if __name__ == "__main__":
    app = KLlApp()
    app.run()
