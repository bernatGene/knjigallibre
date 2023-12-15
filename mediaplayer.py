from datetime import timedelta
from pathlib import Path
import asyncio
import vlc


class MediaPlayer:
    def set_media(self, source_path):
        vlc_instance = vlc.Instance()
        player = vlc_instance.media_player_new()
        media = vlc_instance.media_new(source_path.as_posix())
        player.set_media(media)
        self.player = player

    def __init__(self, source_path: Path = None, playlist: list[Path] = None) -> None:
        if playlist is not None and playlist:
            self.playlist = sorted(playlist)
            source_path = playlist[0]
        else:
            self.playlist = [source_path]
        self.chapter_idx = 0
        if not source_path.exists():
            raise FileNotFoundError
        self.set_media(source_path)

    @classmethod
    def from_single(cls, source_path: Path):
        return cls(source_path)

    @classmethod
    def from_playlist(cls, playlist: list[Path]):
        return cls(None, playlist)

    def iter_playlist(self, incr: int = 1) -> None:
        self.chapter_idx = (self.chapter_idx + incr) % len(self.playlist)
        chp = self.playlist[self.chapter_idx]
        self.pause()
        self.player.stop()
        self.set_media(chp)

    def prev_item(self) -> None:
        self.iter_playlist(-1)

    def next_item(self) -> None:
        self.iter_playlist(1)

    def is_playing(self) -> bool:
        return bool(self.player.is_playing())

    def get_source_length(self) -> int:
        return self.player.get_length()

    def get_time(self) -> int:
        return self.player.get_time()

    def get_str_time(self) -> str:
        return self.normalize_time(self.get_time())

    def get_str_length(self) -> str:
        return self.normalize_time(self.get_source_length())

    def normalize_time(self, time_ms: int) -> str:
        delta = timedelta(milliseconds=time_ms)
        return str(delta)

    def pause(self) -> None:
        self.player.pause()

    def play(self) -> None:
        self.player.play()

    def set_time(self, ts_ms: int) -> None:
        self.player.set_time(ts_ms)


async def main():
    async def print_timestamps(player: MediaPlayer):
        while True:
            print(
                player.is_playing(),
                player.get_str_time(),
                "/",
                player.get_str_length(),
                end="\r",
            )
            await asyncio.sleep(0.01)

    async def play_mp3(player: MediaPlayer):
        player.play()
        await asyncio.sleep(10)
        t = player.get_time()
        player.pause()
        await asyncio.sleep(4)
        player.play()
        await asyncio.sleep(4)
        print(player.get_time())
        player.set_time(t)
        await asyncio.sleep(10)

    player = MediaPlayer(
        Path(
            "/Users/bernatskrabec/p/knjigallibre/media/piknik/Арестович 🎙Пикник на обочине 14 Стругацкие Аудиокнига.mp4"
        )
    )
    await asyncio.gather(print_timestamps(player), play_mp3(player))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
