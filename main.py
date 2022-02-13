from pathlib import Path
from typing import Any, Dict

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters.command import CommandStart
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, InlineKeyboardButton, KeyboardButton
from aiogram.types import TelegramObject
from aiogram.utils.i18n.middleware import I18nMiddleware
from aiogram.utils.i18n.core import I18n
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from emoji import emojize, demojize

import language

i18n_domain = "testbot"
LOCALES_DIR = Path(__file__).parent / 'locales'
i18n = I18n(path=LOCALES_DIR, default_locale="en", domain=i18n_domain)

TOKEN = ""
dp = Dispatcher()


def _(s: str) -> str:
    res = emojize(i18n.gettext(demojize(s)))
    if res:
        return res
    return emojize(i18n.gettext(s))


settings = _(':gear: Настройки')
language_ru = _(':Russia: RU')
language_ru_selected = _(':Russia: RU :check_mark_button:')

language_en = _(':United_States: EN')
language_en_selected = _(':United_States: EN :check_mark_button:')


async def admin_get_lang(user_id):
    if language.language:
        print(language.language)
        return language.language


class LangMiddleware(I18nMiddleware):
    async def get_locale(self, event: TelegramObject, data: Dict[str, Any], **kwargs) -> str:
        user = data.get('event_from_user', 0)
        return await admin_get_lang(user.id) or user.language_code


def menu_kb():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text=_(settings)))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def settings_kb():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text='set_lang', callback_data='set_lang'))
    builder.adjust(1)
    return builder.as_markup()


def langs_kb(lang):
    builder = InlineKeyboardBuilder()
    if lang == 'ru':
        builder.add(InlineKeyboardButton(text=_(language_ru_selected), callback_data='lang_ru'))
        builder.add(InlineKeyboardButton(text=_(language_en), callback_data='lang_en'))
    elif lang == 'en':
        builder.add(InlineKeyboardButton(text=_(language_ru), callback_data='lang_ru'))
        builder.add(InlineKeyboardButton(text=_(language_en_selected), callback_data='lang_en'))
    builder.adjust(2)
    return builder.as_markup()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(_("Hello, <b>{0}!</b>").format(message.from_user.full_name),
                         reply_markup=menu_kb())


@dp.message(text=_(settings))
async def settings_menu(m: types.Message):
    await m.answer('Settings', reply_markup=settings_kb())


@dp.callback_query(text='set_lang')
async def choice_language(call: types.CallbackQuery):
    admin = language.language
    lang = admin
    await call.message.edit_text('Select', reply_markup=langs_kb(lang))


@dp.callback_query(text_contains='lang')
async def change_language(call: types.CallbackQuery):
    lang = call.data[-2:]
    try:
        if lang != language.language:
            i18n.ctx_locale.set(lang)
            language.language = lang
            await call.message.edit_text('Select', reply_markup=langs_kb(lang))
            await call.message.answer('changed', reply_markup=menu_kb())
    except TelegramBadRequest:
        await call.message.answer('kk')


def main() -> None:
    LangMiddleware(i18n).setup(dp)
    bot = Bot(TOKEN, parse_mode="HTML")
    dp.run_polling(bot)


if __name__ == '__main__':
    main()
