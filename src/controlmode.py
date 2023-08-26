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


class ControlMode:
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
        return text
    
    def char_input(self, char: str):
        # if self.index == 0:
        #     self.start()
        # elif self.index == len(self.text_str):
        #     self.stop()
        #     self.__init__(self.text_str)
        #     return
        if char == "j":
            self.windex += 1
        if char == "k":
            self.windex -= 1



sample_text = """
– …Вероятно, вашим первым серьезным открытием, доктор Пильман, следует считать так называемый радиант Пильмана?
– Полагаю, что нет. Радиант Пильмана – это не первое, не серьезное и, собственно, не открытие. И не совсем мое.
– Вы, вероятно, шутите, доктор. Радиант Пильмана – понятие, известное всякому школьнику.
– Это меня не удивляет. Радиант Пильмана и был открыт впервые именно школьником. К сожалению, я не помню, как его звали. Посмотрите у Стетсона в его «Истории Посещения» – там все это подробно рассказано. Открыл радиант впервые школьник, опубликовал координаты впервые студент, а назвали радиант почему-то моим именем.
– Да, с открытиями происходят иногда удивительные вещи. Не могли бы вы объяснить нашим слушателям, доктор Пильман…
– Послушайте, земляк. Радиант Пильмана – это совсем простая штука. Представьте себе, что вы раскрутили большой глобус и принялись палить в него из револьвера. Дырки на глобусе лягут на некую плавную кривую. Вся суть того, что вы называете моим первым серьезным открытием, заключается в простом факте: все шесть Зон Посещения располагаются на поверхности нашей планеты так, словно кто-то дал по Земле шесть выстрелов из пистолета, расположенного где-то на линии Земля – Денеб. Денеб – это альфа созвездия Лебедя, а точка на небесном своде, из которой, так сказать, стреляли, и называется радиантом Пильмана.
– Благодарю вас, доктор. Дорогие хармонтцы! Наконец-то нам толком объяснили, что такое радиант Пильмана! Кстати, позавчера исполнилось ровно тринадцать лет со дня Посещения. Доктор Пильман, может быть, вы скажете своим землякам несколько слов по этому поводу?
"""


async def handle_echo(reader, writer: asyncio.StreamWriter):
    data = await reader.read(100)
    message = data.decode()
    addr = writer.get_extra_info("peername")
    print(f"Received {message!r} from {addr!r}")
    ttest = ControlMode(
        sample_text
    )
    with Live(ttest.get_text(), refresh_per_second=10) as live:
        while True:
            data = await reader.read(100)
            message = data.decode()
            ttest.char_input(message)
            live.update(ttest.get_text())
            if data == b"":
                break


async def main():
    server = await asyncio.start_server(handle_echo, "127.0.0.1", 8888)

    addrs = ", ".join(str(sock.getsockname()) for sock in server.sockets)
    print(f"Serving on {addrs}")

    async with server:
        await server.serve_forever()


asyncio.run(main())
