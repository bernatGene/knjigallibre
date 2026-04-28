
import asyncio

from rich import print
from display.display import Display, ParagraphCommand


sample_text = """
– …Вероятно, вашим первым серьезным открытием, доктор Пильман, следует считать так называемый радиант Пильмана?
– Полагаю, что нет. Радиант Пильмана – это не первое, не серьезное и, собственно, не открытие. И не совсем мое.
– Вы, вероятно, шутите, доктор. Радиант Пильмана – понятие, известное всякому школьнику.
– Это меня не удивляет. Радиант Пильмана и был открыт впервые именно школьником. К сожалению, я не помню, как его звали. Посмотрите у Стетсона в его «Истории Посещения» – там все это подробно рассказано. Открыл радиант впервые школьник, опубликовал координаты впервые студент, а назвали радиант почему-то моим именем.
– Да, с открытиями происходят иногда удивительные вещи. Не могли бы вы объяснить нашим слушателям, доктор Пильман…
– Послушайте, земляк. Радиант Пильмана – это совсем простая штука. Представьте себе, что вы раскрутили большой глобус и принялись палить в него из револьвера. Дырки на глобусе лягут на некую плавную кривую. Вся суть того, что вы называете моим первым серьезным открытием, заключается в простом факте: все шесть Зон Посещения располагаются на поверхности нашей планеты так, словно кто-то дал по Земле шесть выстрелов из пистолета, расположенного где-то на линии Земля – Денеб. Денеб – это альфа созвездия Лебедя, а точка на небесном своде, из которой, так сказать, стреляли, и называется радиантом Пильмана.
– Благодарю вас, доктор. Дорогие хармонтцы! Наконец-то нам толком объяснили, что такое радиант Пильмана! Кстати, позавчера исполнилось ровно тринадцать лет со дня Посещения. Доктор Пильман, может быть, вы скажете своим землякам несколько слов по этому поводу?
"""



class CommandInterpreter:
    def __init__(self) -> None:
        pass

    def handle_paragraph_command(self, keystroke):
        match keystroke:
            case "j":
                return ParagraphCommand.NEXT_W
            case "k":
                return ParagraphCommand.PREV_W
            case _:
                pass

async def handle_echo(reader, writer: asyncio.StreamWriter):
    data = await reader.read(100)
    message = data.decode()
    addr = writer.get_extra_info("peername")
    print(f"Received {message!r} from {addr!r}")
    interpreter = CommandInterpreter()
    display = Display(sample_text)
    display_task = asyncio.create_task(display.display())
    while True:
        data = await reader.read(100)
        if data == b"":
            display_task.cancel()
            break
        message = data.decode()
        command = interpreter.handle_paragraph_command(message)
        await display.command_queue.put(command)


async def run(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()


async def main():
    server = await asyncio.start_server(handle_echo, "127.0.0.1", 8888)
    addrs = ", ".join(str(sock.getsockname()) for sock in server.sockets)
    print(f"Serving on {addrs}")

    async with server:
        await asyncio.gather(
            run("python keyboardclient.py"),
            server.serve_forever(),
        )

if __name__ == "__main__":
    asyncio.run(main())
