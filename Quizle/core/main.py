from aiogram import types, Dispatcher, Bot
from aiogram.utils import executor
import aiogram.dispatcher.filters as filters
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from tables import *


#Запуск бота
bot = Bot(token="7914924800:AAG-5ZAJBcPn3Qh55z6s4uqJZuLnonEyZIc")
central = Dispatcher(bot, storage=MemoryStorage())



#КЛАВИАТУРЫ
start_keyboard = types.InlineKeyboardMarkup(row_width=1, inline_keyboard=[
    [types.InlineKeyboardButton(text='Продолжить', callback_data='main_menu')]
])

continue_keyboard = types.InlineKeyboardMarkup(row_width=2, inline_keyboard=[
    [types.InlineKeyboardButton(text='Начать игру', callback_data='start_game'), types.InlineKeyboardButton(text='Список лидеров', callback_data='leaderboard')],
    [types.InlineKeyboardButton(text='Панель администратора', callback_data='admin_panel')]
])

get_to_main_menu_keyboard = types.InlineKeyboardMarkup(row_width=1, inline_keyboard=[
    [types.InlineKeyboardButton(text='Назад', callback_data='main_menu')]
])

admin_access_denied_keyboard = types.InlineKeyboardMarkup(row_width=1, inline_keyboard=[
    [types.InlineKeyboardButton(text='Ввести пароль', callback_data='passcode_input'), types.InlineKeyboardButton(text='Назад', callback_data='main_menu')]
])

admin_panel_keyboard = types.InlineKeyboardMarkup(row_width=2, inline_keyboard=[
    [types.InlineKeyboardButton(text='Новые вопросы', callback_data='new_quiz'), types.InlineKeyboardButton(text='Начать/завершить игру', callback_data='start_end_game')],
    [types.InlineKeyboardButton(text='Выдать промокоды', callback_data='give_promocode')],#, types.InlineKeyboardButton(text='Изменить уровень доступа', callback_data='update_user_access')],
    [types.InlineKeyboardButton(text='Назад', callback_data='main_menu')]
])

confirm_keyboard = types.ReplyKeyboardMarkup(keyboard=[
    [types.KeyboardButton(text='Да'),types.KeyboardButton(text='Нет')]
    ],
    one_time_keyboard=True,
    resize_keyboard=True
)
# select_user_keyboard = types.InlineKeyboardMarkup(row_width=2, inline_keyboard=[
#     [types.InlineKeyboardButton(text=f"{get_users('all')[0]} - {get_users('all')[1]}", callback_data='user_selected')],
#     [types.InlineKeyboardButton(text='Назад', callback_data='main_menu')]
# ])


#СОСТОЯНИЯ
class HandleClient(StatesGroup):
    passcode_check = State()
    new_quiz = State()
    quiz_main = State()


#КОНЧЕНЫЕ АВТОМАТЫ
async def start(message : types.Message):
    await message.answer('Привет! Это бот Quizle для проведения быстрых квизов.' \
    '\nКаждый день в определённое время проводятся квизы на 5 вопросов.' \
    '\nВ конце дня 10 победителей получают промокоды "AE Shop".', reply_markup= start_keyboard)

async def main_menu(callback : types.CallbackQuery):
    await callback.message.edit_text('Выбери действие:', reply_markup=continue_keyboard)


    username = callback.from_user.username
    if not username:
        await callback.message.answer('Ошибка: Некорректный юзернейм')
    
    if not user_check(username, check='existance'):
        add_user(username=username, score=0, access_level=2)
    await callback.answer()

async def leaderboard(callback : types.CallbackQuery):
    await callback.message.edit_text(get_users('top_10'), reply_markup=get_to_main_menu_keyboard)
    await callback.answer()

async def admin_panel(callback : types.CallbackQuery):
    if user_check(username=callback.from_user.username, check='access_level') < 2:
        await callback.message.edit_text('Панель администратора доступна с уровнем доступа 2 и выше.', reply_markup=admin_access_denied_keyboard)
    else:
        await callback.message.edit_text('Выберите действие:',reply_markup=admin_panel_keyboard)
    await callback.answer()

async def passcode_input(callback : types.CallbackQuery):
    await callback.message.edit_text('Введите пароль для доступа к панели администратора.')
    await HandleClient.passcode_check.set()
    await callback.answer()

admin_passcode = "Cyberia"
async def passcode_check(message : types.Message, state : FSMContext):
    if message.text != admin_passcode:
        await message.answer('Неверный пароль. Доступ отклонён.', reply_markup=get_to_main_menu_keyboard)
    else:
        await message.answer('Доступ разрешён.', reply_markup=get_to_main_menu_keyboard)
        global access_level
        access_level += 1
    await state.finish()

async def new_quiz_intro(callback : types.CallbackQuery):
    await callback.message.edit_text('Для создания новых вопросов напишите вопросы в чат в формате "Вопрос: Ответ №1, Ответ №2, Ответ №3, Ответ №4; Номер правильного ответа".\n' \
    'Введите вопрос №1:')
    await callback.answer()
    await HandleClient.new_quiz.set()

async def new_quiz(message : types.Message, state: FSMContext):
    data = await state.get_data()
    questions_data = data.get('questions_data', [])
    current_question = data.get('current_question', 1)

    if message.text.count(':') == 1 and message.text.count(',') == 3 and message.text.count(';') == 1 and len(message.text) - 5 >= 6:
        questions_data.append(message.text)
        current_question += 1
        await state.update_data(questions_data=questions_data, current_question=current_question)

        if current_question < 6:
            await message.answer(f'Вопрос принят. Введите вопрос №{current_question}:')
        else:
            await message.answer('Все вопросы указаны.', reply_markup=get_to_main_menu_keyboard)
            await state.finish()
            create_new_questions(questions_data)

    else:
        await message.answer('Формат записи неверный.')
        await message.answer('Правильный формат записи: \n"Вопрос: Ответ №1, Ответ №2, Ответ №3, Ответ №4; Номер правильного ответа".\n')
        await message.answer(f'Введите вопрос №{current_question}:')

async def game_start(callback : types.CallbackQuery, state : FSMContext):
    await callback.message.delete()
    await callback.message.answer('Начать игру?',reply_markup=confirm_keyboard)
    await HandleClient.quiz_main.set()

async def quiz_main(message : types.Message, state : FSMContext):
    text = message.text
    if text == 'Нет' or text == '/start':
        await message.answer('Игра отменена', reply_markup=get_to_main_menu_keyboard)
        await state.finish()
    elif text == 'Да':
        await message.answer('Игра начата')
# async def update_user_access(callback : types.CallbackQuery, state : FSMContext):
#     await callback.message.edit_text('Выберите пользователя:',reply_markup=select_user_keyboard)

#ХЭНДЛЕРЫ
def register_handlers(central: Dispatcher):
    central.register_message_handler(start, commands="start")
    central.register_message_handler(passcode_check, state=HandleClient.passcode_check)
    central.register_message_handler(new_quiz, state=HandleClient.new_quiz)

    central.register_callback_query_handler(main_menu, lambda callback: callback.data == 'main_menu')
    central.register_callback_query_handler(leaderboard, lambda callback: callback.data == 'leaderboard')
    central.register_callback_query_handler(admin_panel, lambda callback: callback.data == 'admin_panel')
    central.register_callback_query_handler(passcode_input, lambda callback: callback.data == 'passcode_input')
    central.register_callback_query_handler(new_quiz_intro, lambda callback: callback.data == 'new_quiz')
    central.register_callback_query_handler(game_start, lambda callback : callback.data == 'start_game')
    # central.register_callback_query_handler(update_user_access, lambda callback: callback.data == 'update_user_access')

register_handlers(central)

#работа бота
executor.start_polling(central, skip_updates=True)