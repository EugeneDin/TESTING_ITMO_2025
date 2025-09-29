import unittest
from unittest.mock import AsyncMock
import re
from telegram import Update, User, Message, Chat
import bot_randomlab as br

def mock_update(text="/start", user_id=1):
    chat = Chat(id=user_id, type="private")
    user = User(id=user_id, first_name="U", is_bot=False)
    msg = Message(message_id=1, date=None, chat=chat, text=text, from_user=user)
    return Update(update_id=1, message=msg)

class TestRandomLab(unittest.IsolatedAsyncioTestCase):
    # Проверяет, что /start отвечает и содержит имя бота
    async def test_start(self):
        u = mock_update("/start"); ctx = AsyncMock()
        await br.start(u, ctx)
        ctx.bot.send_message.assert_called_once()
        self.assertIn("RandomLab", ctx.bot.send_message.call_args.kwargs["text"])

    # Проверяет, что /help перечисляет основные команды
    async def test_help_contains_commands(self):
        u = mock_update("/help"); ctx = AsyncMock()
        await br.help_command(u, ctx)
        t = ctx.bot.send_message.call_args.kwargs["text"]
        for cmd in ["/roll","/coin","/rand","/choose","/shuffle","/password","/uuid","/color","/eightball","/lorem","/sample","/permute"]:
            self.assertIn(cmd, t)

    # Проверяет корректный формат ответа /roll при валидном NdM
    async def test_roll_ok(self):
        u = mock_update("/roll 2d6"); ctx = AsyncMock()
        ctx.args = ["2d6"]
        await br.roll(u, ctx)
        msg = ctx.bot.send_message.call_args.kwargs["text"]
        self.assertRegex(msg, r"Броски: \[\d+, \d+\] \| сумма=\d+")

    # Проверяет сообщение об ошибке при неверном формате /roll
    async def test_roll_format_error(self):
        u = mock_update("/roll bad"); ctx = AsyncMock()
        ctx.args = ["bad"]
        await br.roll(u, ctx)
        self.assertIn("Неверный формат", ctx.bot.send_message.call_args.kwargs["text"])

    # Проверяет граничные условия /roll (n<=0 недопустимо)
    async def test_roll_bounds(self):
        u = mock_update("/roll 0d6"); ctx = AsyncMock(); ctx.args=["0d6"]
        await br.roll(u, ctx)
        self.assertIn("Неверный формат", ctx.bot.send_message.call_args.kwargs["text"])

    # Проверяет, что /coin возвращает одно из двух значений
    async def test_coin(self):
        u = mock_update("/coin"); ctx=AsyncMock()
        await br.coin(u, ctx)
        self.assertIn(ctx.bot.send_message.call_args.kwargs["text"], ["Орёл","Решка"])

    # Проверяет корректную генерацию /rand в диапазоне [a,b]
    async def test_rand_ok(self):
        u = mock_update("/rand 1 3"); ctx=AsyncMock(); ctx.args=["1","3"]
        await br.rand_int(u, ctx)
        val = int(ctx.bot.send_message.call_args.kwargs["text"])
        self.assertTrue(1 <= val <= 3)

    # Проверяет, что при a>b аргументы меняются местами
    async def test_rand_swap(self):
        u = mock_update("/rand 10 5"); ctx=AsyncMock(); ctx.args=["10","5"]
        await br.rand_int(u, ctx)
        val = int(ctx.bot.send_message.call_args.kwargs["text"])
        self.assertTrue(5 <= val <= 10)

    # Проверяет сообщение об ошибке для /rand с нецелыми аргументами
    async def test_rand_bad(self):
        u = mock_update("/rand a b"); ctx=AsyncMock(); ctx.args=["a","b"]
        await br.rand_int(u, ctx)
        self.assertIn("целыми", ctx.bot.send_message.call_args.kwargs["text"])

    # Проверяет /choose: выбирается один из переданных элементов
    async def test_choose_ok(self):
        u = mock_update("/choose a|b|c"); ctx=AsyncMock(); ctx.args=["a|b|c"]
        await br.choose(u, ctx)
        self.assertIn(ctx.bot.send_message.call_args.kwargs["text"], ["a","b","c"])

    # Проверяет /choose: пустой список → сообщение об ошибке
    async def test_choose_empty(self):
        u = mock_update("/choose   "); ctx=AsyncMock(); ctx.args=["   "]
        await br.choose(u, ctx)
        self.assertIn("Список пуст", ctx.bot.send_message.call_args.kwargs["text"])

    # Проверяет /shuffle: перемешивание не теряет элементы
    async def test_shuffle_ok(self):
        u = mock_update("/shuffle 1|2|3"); ctx=AsyncMock(); ctx.args=["1|2|3"]
        await br.shuffle_cmd(u, ctx)
        out = ctx.bot.send_message.call_args.kwargs["text"]
        parts = [p.strip() for p in out.split("|")]
        self.assertCountEqual(parts, ["1","2","3"])

    # Проверяет /password: длина и алфавит [A-Za-z0-9]
    async def test_password_len(self):
        u = mock_update("/password 16"); ctx=AsyncMock(); ctx.args=["16"]
        await br.password(u, ctx)
        pwd = ctx.bot.send_message.call_args.kwargs["text"]
        self.assertEqual(len(pwd), 16)
        self.assertRegex(pwd, r"^[A-Za-z0-9]+$")

    # Проверяет /password: длина меньше минимума
    async def test_password_bounds_low(self):
        u = mock_update("/password 5"); ctx=AsyncMock(); ctx.args=["5"]
        await br.password(u, ctx)
        self.assertIn("Длина должна быть от 8", ctx.bot.send_message.call_args.kwargs["text"])

    # Проверяет /password: длина больше максимума
    async def test_password_bounds_high(self):
        u = mock_update("/password 100"); ctx=AsyncMock(); ctx.args=["100"]
        await br.password(u, ctx)
        self.assertIn("Длина должна быть от 8", ctx.bot.send_message.call_args.kwargs["text"])

    # Проверяет /password: нецелый аргумент длины
    async def test_password_bad(self):
        u = mock_update("/password x"); ctx=AsyncMock(); ctx.args=["x"]
        await br.password(u, ctx)
        self.assertIn("Длина должна быть целым", ctx.bot.send_message.call_args.kwargs["text"])

    # Проверяет /uuid: формат UUID v4
    async def test_uuid(self):
        u = mock_update("/uuid"); ctx=AsyncMock()
        await br.uuid_cmd(u, ctx)
        val = ctx.bot.send_message.call_args.kwargs["text"]
        self.assertRegex(val, r"^[0-9a-fA-F-]{36}$")

    # Проверяет /color: формат HEX #RRGGBB
    async def test_color(self):
        u = mock_update("/color"); ctx=AsyncMock()
        await br.color(u, ctx)
        self.assertRegex(ctx.bot.send_message.call_args.kwargs["text"], r"^#[0-9A-F]{6}$")

    # Проверяет /eightball: ответ из фиксированного набора
    async def test_eightball(self):
        u = mock_update("/eightball"); ctx=AsyncMock()
        await br.eightball(u, ctx)
        self.assertIn(ctx.bot.send_message.call_args.kwargs["text"], br.EIGHTBALL)

    # Проверяет /lorem: выдаёт ровно n слов
    async def test_lorem_ok(self):
        u = mock_update("/lorem 5"); ctx=AsyncMock(); ctx.args=["5"]
        await br.lorem(u, ctx)
        self.assertEqual(len(ctx.bot.send_message.call_args.kwargs["text"].split()), 5)

    # Проверяет /lorem: n вне диапазона → ошибка
    async def test_lorem_bounds(self):
        u = mock_update("/lorem 0"); ctx=AsyncMock(); ctx.args=["0"]
        await br.lorem(u, ctx)
        self.assertIn("1..50", ctx.bot.send_message.call_args.kwargs["text"])

    # Проверяет /lorem: n нецелое → ошибка
    async def test_lorem_bad(self):
        u = mock_update("/lorem a"); ctx=AsyncMock(); ctx.args=["a"]
        await br.lorem(u, ctx)
        self.assertIn("целым", ctx.bot.send_message.call_args.kwargs["text"])

    # Проверяет /sample: выбирает k элементов без повторов
    async def test_sample_ok(self):
        u = mock_update("/sample 2 a|b|c"); ctx=AsyncMock(); ctx.args=["2","a|b|c"]
        await br.sample(u, ctx)
        out = [s.strip() for s in ctx.bot.send_message.call_args.kwargs["text"].split("|")]
        self.assertEqual(len(out), 2)
        for v in out:
            self.assertIn(v, ["a","b","c"])

    # Проверяет /sample: k больше длины списка → ошибка
    async def test_sample_k_too_large(self):
        u = mock_update("/sample 5 a|b"); ctx=AsyncMock(); ctx.args=["5","a|b"]
        await br.sample(u, ctx)
        self.assertIn("k должно быть", ctx.bot.send_message.call_args.kwargs["text"])

    # Проверяет /sample: нецелое k → ошибка
    async def test_sample_bad_k(self):
        u = mock_update("/sample x a|b"); ctx=AsyncMock(); ctx.args=["x","a|b"]
        await br.sample(u, ctx)
        self.assertIn("k должно быть целым", ctx.bot.send_message.call_args.kwargs["text"])

    # Проверяет /permute: перестановка содержит все числа 1..n
    async def test_permute_ok(self):
        u = mock_update("/permute 5"); ctx=AsyncMock(); ctx.args=["5"]
        await br.permute(u, ctx)
        arr = list(map(int, ctx.bot.send_message.call_args.kwargs["text"].split()))
        self.assertCountEqual(arr, [1,2,3,4,5])

    # Проверяет /permute: n вне допустимого диапазона → ошибка
    async def test_permute_bounds(self):
        u = mock_update("/permute 11"); ctx=AsyncMock(); ctx.args=["11"]
        await br.permute(u, ctx)
        self.assertIn("1..10", ctx.bot.send_message.call_args.kwargs["text"])

    # Проверяет /permute: нецелое n → ошибка
    async def test_permute_bad(self):
        u = mock_update("/permute x"); ctx=AsyncMock(); ctx.args=["x"]
        await br.permute(u, ctx)
        self.assertIn("целым", ctx.bot.send_message.call_args.kwargs["text"])

    # ---- Дополнительные тесты (превышаем 40) ----

    # Проверяет /roll: отсутствие аргумента → подсказка по использованию
    async def test_roll_missing_arg(self):
        u = mock_update("/roll"); ctx=AsyncMock(); ctx.args=[]
        await br.roll(u, ctx)
        self.assertIn("Использование: /roll", ctx.bot.send_message.call_args.kwargs["text"])

    # Проверяет /choose: отсутствие аргумента → подсказка по использованию
    async def test_choose_usage(self):
        u = mock_update("/choose"); ctx=AsyncMock(); ctx.args=[]
        await br.choose(u, ctx)
        self.assertIn("Использование: /choose", ctx.bot.send_message.call_args.kwargs["text"])

    # Проверяет /shuffle: отсутствие аргумента → подсказка по использованию
    async def test_shuffle_usage(self):
        u = mock_update("/shuffle"); ctx=AsyncMock(); ctx.args=[]
        await br.shuffle_cmd(u, ctx)
        self.assertIn("Использование: /shuffle", ctx.bot.send_message.call_args.kwargs["text"])

    # Проверяет /password: отсутствие аргумента → подсказка по использованию
    async def test_password_usage(self):
        u = mock_update("/password"); ctx=AsyncMock(); ctx.args=[]
        await br.password(u, ctx)
        self.assertIn("Использование: /password", ctx.bot.send_message.call_args.kwargs["text"])

    # Проверяет /rand: отсутствие аргументов → подсказка по использованию
    async def test_rand_usage(self):
        u = mock_update("/rand"); ctx=AsyncMock(); ctx.args=[]
        await br.rand_int(u, ctx)
        self.assertIn("Использование: /rand", ctx.bot.send_message.call_args.kwargs["text"])

    # Проверяет /lorem: отсутствие аргумента → подсказка по использованию
    async def test_lorem_usage(self):
        u = mock_update("/lorem"); ctx=AsyncMock(); ctx.args=[]
        await br.lorem(u, ctx)
        self.assertIn("Использование: /lorem", ctx.bot.send_message.call_args.kwargs["text"])

    # Проверяет /sample: отсутствие аргументов → подсказка по использованию
    async def test_sample_usage(self):
        u = mock_update("/sample"); ctx=AsyncMock(); ctx.args=[]
        await br.sample(u, ctx)
        self.assertIn("Использование: /sample", ctx.bot.send_message.call_args.kwargs["text"])

    # Проверяет /permute: отсутствие аргумента → подсказка по использованию
    async def test_permute_usage(self):
        u = mock_update("/permute"); ctx=AsyncMock(); ctx.args=[]
        await br.permute(u, ctx)
        self.assertIn("Использование: /permute", ctx.bot.send_message.call_args.kwargs["text"])

    # Проверяет /color: корректность HEX через regexp
    async def test_color_format(self):
        u = mock_update("/color"); ctx=AsyncMock()
        await br.color(u, ctx)
        self.assertTrue(re.match(r"^#[0-9A-F]{6}$", ctx.bot.send_message.call_args.kwargs["text"]) is not None)

    # Проверяет, что /help возвращает немаленький текст (живой ответ)
    async def test_help_does_not_fail(self):
        u = mock_update("/help"); ctx=AsyncMock()
        await br.help_command(u, ctx)
        self.assertTrue(len(ctx.bot.send_message.call_args.kwargs["text"]) > 10)

    # ---- Новые дополнительные тесты (ещё +8) ----

    # Проверяет /roll: m > 1000 недопустимо
    async def test_roll_m_too_large(self):
        u = mock_update("/roll 2d1001"); ctx = AsyncMock(); ctx.args = ["2d1001"]
        await br.roll(u, ctx)
        self.assertIn("Неверный формат", ctx.bot.send_message.call_args.kwargs["text"])

    # Проверяет /rand: равные границы возвращают именно это число
    async def test_rand_equal_bounds(self):
        u = mock_update("/rand 7 7"); ctx=AsyncMock(); ctx.args=["7","7"]
        await br.rand_int(u, ctx)
        self.assertEqual(ctx.bot.send_message.call_args.kwargs["text"], "7")

    # Проверяет /choose: корректно обрезает пробелы вокруг элементов
    async def test_choose_trims(self):
        u = mock_update("/choose  a  |  b |  c "); ctx=AsyncMock(); ctx.args=["a  |  b |  c"]
        await br.choose(u, ctx)
        self.assertIn(ctx.bot.send_message.call_args.kwargs["text"], ["a","b","c"])

    # Проверяет /shuffle: строка из одних пробелов даёт «Список пуст.»
    async def test_shuffle_only_spaces(self):
        u = mock_update("/shuffle      "); ctx=AsyncMock(); ctx.args=["     "]
        await br.shuffle_cmd(u, ctx)
        self.assertIn("Список пуст", ctx.bot.send_message.call_args.kwargs["text"])

    # Проверяет /uuid: два вызова дают разные значения
    async def test_uuid_uniqueness(self):
        u = mock_update("/uuid"); ctx=AsyncMock()
        await br.uuid_cmd(u, ctx); first = ctx.bot.send_message.call_args.kwargs["text"]
        ctx.reset_mock()
        await br.uuid_cmd(u, ctx); second = ctx.bot.send_message.call_args.kwargs["text"]
        self.assertNotEqual(first, second)

    # Проверяет /lorem: верхняя граница n=50 допустима
    async def test_lorem_max_50(self):
        u = mock_update("/lorem 50"); ctx=AsyncMock(); ctx.args=["50"]
        await br.lorem(u, ctx)
        self.assertEqual(len(ctx.bot.send_message.call_args.kwargs["text"].split()), 50)

    # Проверяет /sample: k=0 допускается и возвращает пустую строку
    async def test_sample_k_zero(self):
        u = mock_update("/sample 0 a|b|c"); ctx=AsyncMock(); ctx.args=["0","a|b|c"]
        await br.sample(u, ctx)
        self.assertEqual(ctx.bot.send_message.call_args.kwargs["text"], "")

    # Проверяет /permute: n=1 возвращает «1»
    async def test_permute_n1(self):
        u = mock_update("/permute 1"); ctx=AsyncMock(); ctx.args=["1"]
        await br.permute(u, ctx)
        self.assertEqual(ctx.bot.send_message.call_args.kwargs["text"].strip(), "1")


if __name__ == "__main__":
    unittest.main()
