from bs4 import UnicodeDammit
from pathlib import Path


file = Path("./media/picnic.txt")
bytes = file.read_bytes()
print(UnicodeDammit(bytes).unicode_markup)