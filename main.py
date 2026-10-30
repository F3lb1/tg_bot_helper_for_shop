import telebot
from google.colab import userdata
import sqlite3
import speech_recognition
token = userdata.get("token")
from telebot import types

bot = telebot.TeleBot(token)

OPERATOR_ID = id оператора

waiting_for_operator = set()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, """Привет! Я твой Telegram бот-Помощник!
  Напиши мне свой вопрос,а я постараюсь тебе на него ответить. """)

@bot.message_handler(commands=["help"])
def sendhelp(message):
  keyboard = types.InlineKeyboardMarkup()
  btn_ofor= types.InlineKeyboardButton(text="Как оформить заказ?", callback_data="answer_ofor")
  btn_stat= types.InlineKeyboardButton(text="Как узнать статус моего заказа?", callback_data="answer_stat")
  btn_otmen= types.InlineKeyboardButton(text="Как отменить заказ?", callback_data="answer_otmen")
  btn_brak= types.InlineKeyboardButton(text="Что делать, если товар пришел поврежденным?", callback_data="answer_brak")
  btn_help= types.InlineKeyboardButton(text="Как связаться с вашей технической поддержкой?", callback_data="answer_help")
  btn_info= types.InlineKeyboardButton(text="Как узнать информацию о доставке?", callback_data="answer_info")
  btn_drugoe= types.InlineKeyboardButton(text="Другое", callback_data="answer_drugoe")
  keyboard.add(btn_ofor)
  keyboard.add(btn_stat)
  keyboard.add(btn_help)
  keyboard.add(btn_info)
  keyboard.add(btn_otmen)
  keyboard.add(btn_brak)
  keyboard.add(btn_drugoe)
  bot.send_message(message.chat.id," Выберите вопрос", reply_markup=keyboard)
  answer = bot.reply_to(message, "Пришлите свой вопрос!")

@bot.callback_query_handler(func=lambda call: True)
def on_click(call):
    # Смотрим, какая кнопка была нажата, и отвечаем
    if call.data == "answer_ofor":
        bot.send_message(call.message.chat.id, "Для оформления заказа, пожалуйста, выберите интересующий вас товар и нажмите кнопку " "Добавить в корзину" ", затем перейдите в корзину и следуйте инструкциям для завершения покупки.")
    elif call.data == "answer_stat":
        bot.send_message(call.message.chat.id, "Вы можете узнать статус вашего заказа, войдя в свой аккаунт на нашем сайте и перейдя в раздел " "Мои заказы" ". Там будет указан текущий статус вашего заказа.")
    elif call.data == "answer_otmen":
        bot.send_message(call.message.chat.id, "Если вы хотите отменить заказ, пожалуйста, свяжитесь с нашей службой поддержки как можно скорее. Мы постараемся помочь вам с отменой заказа до его отправки.")
    elif call.data == "answer_brak":
        bot.send_message(call.message.chat.id, "При получении поврежденного товара, пожалуйста, сразу свяжитесь с нашей службой поддержки и предоставьте фотографии повреждений. Мы поможем вам с обменом или возвратом товара.")
    elif call.data == "answer_help":
        bot.send_message(call.message.chat.id, "Вы можете связаться с нашей технической поддержкой через телефон на нашем сайте или написать нам в чат-бота.")
    elif call.data == "answer_info":
        bot.send_message(call.message.chat.id, "Информацию о доставке вы можете найти на странице оформления заказа на нашем сайте. Там указаны доступные способы доставки и сроки.")
    elif call.data == "answer_drugoe":
       waiting_for_operator.add(call.from_user.id)
       bot.send_message(
        call.message.chat.id,
        "Напишите ваш вопрос одним сообщением — я передам его оператору, и он ответит вам здесь."
        )
       bot.answer_callback_query(call.id)
       #bot.register_next_step_handler(answer, getquestions )

@bot.message_handler(func=lambda m: m.from_user.id in waiting_for_operator, content_types=['text', 'photo', 'document'])
def relay_to_operator(message):
    waiting_for_operator.discard(message.from_user.id)  # снимаем режим после одного сообщения

    # Пересылаем оператору
    bot.forward_message(OPERATOR_ID, message.chat.id, message.message_id)

    # Подсказка оператору, как ответить (необязательно, но удобно)
    bot.send_message(
        OPERATOR_ID,
        f"↩️ Ответьте реплаем на сообщение выше, чтобы написать пользователю {message.from_user.full_name} (id: {message.from_user.id})."
    )

    bot.send_message(message.chat.id, "✅ Сообщение передано оператору. Ожидайте ответа.")


@bot.message_handler(func=lambda m: m.from_user.id == OPERATOR_ID, content_types=['text', 'photo', 'document'])
def relay_from_operator(message):
    # Оператор должен ответить реплаем на пересланное сообщение
    if not message.reply_to_message or not message.reply_to_message.forward_from:
        bot.send_message(OPERATOR_ID, "⚠️ Ответьте реплаем на сообщение пользователя, чтобы я знал, кому писать.")
        return

    user_id = message.reply_to_message.forward_from.id

    # Пересылаем ответ пользователю (можно копией, чтобы не палить оператора)
    bot.copy_message(user_id, OPERATOR_ID, message.message_id)



def getquestions(message):
  text = message.text
  bot.reply_to(message, text)


bot.polling()
