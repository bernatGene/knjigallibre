from pathlib import Path
from datetime import date


class Bookmark:
    def __init__(self, texts: list[Path], audios: [Path], safe_file: Path = f"bookmarks/{date.today()}") -> None:
        self.texts = texts
        self.audios = audios
        assert all([p.exists() for p in self.texts + self.audios]), "Inexistent path"
    
    # def save_text(text, )

