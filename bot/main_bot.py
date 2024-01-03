import telebot
from django.conf import settings
from bot.api.api import get_crypto_exchange_rate
from bot.utils.phone_validator import is_valid_phone_number
from custom_admin.models import TelegramUser
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN, parse_mode='HTML')
telebot.logger.setLevel(settings.LOG_LEVEL)

# Dictionary to store user states
user_states = {}

# Constants for states
STATE_UNREGISTERED = "unregistered"
STATE_REGISTERED = "registered"
STATE_PHONE_REGISTRATION = "phone_registration"

# Messages
START_MESSAGE_UNREGISTERED = "Hi there! I am your crypto companion. Type /start to begin."
START_MESSAGE_REGISTERED = "Hi there! I am your crypto companion."


@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    user_id = message.from_user.id

    if TelegramUser.objects.filter(telegram_id=user_id).exists():
        bot.send_message(user_id, START_MESSAGE_REGISTERED)
        user_states[user_id] = STATE_REGISTERED
        handle_registered_state(message)
    else:
        handle_unregistered_state(message)


# Handle other messages
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id

    if user_id in user_states:
        current_state = user_states[user_id]

        # Handle states
        if current_state == STATE_REGISTERED:
            handle_registered_state(message)
        elif current_state == STATE_UNREGISTERED:
            handle_unregistered_state(message)
        elif current_state == STATE_PHONE_REGISTRATION:
            handle_phone_registration_state(message)


def handle_registered_state(message):
    user_id = message.from_user.id

    keyboard = InlineKeyboardMarkup()

    button1 = InlineKeyboardButton(text="Bitcoin course", callback_data="course_bitcoin")
    button2 = InlineKeyboardButton(text="Ethereum course", callback_data="course_ethereum")

    keyboard.row(button1, button2)

    bot.send_message(user_id, "Choose an option:", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith("course"))
def handle_course_option(call):
    user_id = call.from_user.id
    option_selected = call.data[len("course_"):]

    if option_selected == "bitcoin":
        handle_crypto_info(call, "bitcoin")
    elif option_selected == "ethereum":
        handle_crypto_info(call, "ethereum")
    else:
        bot.send_message(user_id, "Invalid course option selected.")


def handle_crypto_info(call, crypto_symbol):
    user_id = call.from_user.id
    rate_usd, rate_reverse = get_crypto_exchange_rate(crypto_symbol)

    if rate_usd is not None and rate_reverse is not None:
        message = f"Current exchange rate for {crypto_symbol}:\n"
        message += f"- USD to {crypto_symbol}: ${rate_usd:.2f}\n"
        message += f"- {crypto_symbol} to USD: {rate_reverse:.8f} {crypto_symbol.upper()}"

        keyboard = InlineKeyboardMarkup()
        button_sell = InlineKeyboardButton(text=f"Sell {crypto_symbol.upper()}", callback_data=f"sell_{crypto_symbol}")
        button_buy = InlineKeyboardButton(text=f"Buy {crypto_symbol.upper()}", callback_data=f"buy_{crypto_symbol}")

        keyboard.row(button_sell, button_buy)

        bot.send_message(user_id, message, reply_markup=keyboard)
    else:
        bot.send_message(user_id, f"Could not retrieve exchange rate for {crypto_symbol}.")


@bot.callback_query_handler(func=lambda call: call.data.startswith(("sell_", "buy_")))
def handle_trade_option(call):
    user_id = call.from_user.id
    trade_option, crypto_symbol = call.data.split("_")[0], call.data.split("_")[1]

    # Перевірка, чи коректно розібрано дані
    if trade_option in ["sell", "buy"] and crypto_symbol:
        action = "selling" if trade_option == "sell" else "buying"

        # Отримання курсів для відповідної криптовалюти
        rate_usd, rate_reverse = get_crypto_exchange_rate(crypto_symbol)

        if action == "selling" and rate_usd is not None:
            handle_sell_option(call, user_id, crypto_symbol, rate_usd)
        elif action == "buying" and rate_reverse is not None:
            handle_buy_option(call, user_id, crypto_symbol, rate_reverse)
        else:
            bot.send_message(user_id, "Invalid rate value or action.")
    else:
        bot.send_message(user_id, "Invalid trade option selected.")


def handle_sell_option(call, user_id, crypto_symbol, rate_usd):
    # Відправлення повідомлення та питання про суму для продажу
    selected_option_message = f"You selected selling {crypto_symbol.upper()}."
    bot.send_message(user_id, selected_option_message)
    bot.send_message(user_id, "Enter the amount:")
    bot.register_next_step_handler(call.message, handle_sell_amount_input, crypto_symbol, rate_usd)


def handle_buy_option(call, user_id, crypto_symbol, rate_reverse):
    # Відправлення повідомлення та питання про суму для купівлі
    selected_option_message = f"You selected buying {crypto_symbol.upper()}."
    bot.send_message(user_id, selected_option_message)
    bot.send_message(user_id, "Enter the amount in USD:")
    bot.register_next_step_handler(call.message, handle_buy_amount_input, crypto_symbol, rate_reverse)


def handle_sell_amount_input(message, crypto_symbol, rate_usd):
    user_id = message.from_user.id
    amount = message.text

    try:
        amount = float(amount)

        if amount > 0:
            result = amount * rate_usd
            response_message = f"For {amount} {crypto_symbol.upper()}:\n"
            response_message += f"- In USD: ${result:.2f}\n"
            bot.send_message(user_id, response_message)
        else:
            raise ValueError("Invalid amount. Must be positive.")

    except ValueError as e:
        bot.send_message(user_id, f"Could not calculate result. {e}")
    except Exception as e:
        bot.send_message(user_id, f"An error occurred: {e}")


def handle_buy_amount_input(message, crypto_symbol, rate_reverse):
    user_id = message.from_user.id
    amount_usd = message.text

    try:
        amount_usd = float(amount_usd)

        if amount_usd > 0:
            result = amount_usd * rate_reverse
            response_message = f"For {amount_usd} USD:\n"
            response_message += f"- In {crypto_symbol.upper()}: {result:.8f} {crypto_symbol.upper()}"
            bot.send_message(user_id, response_message)
        else:
            raise ValueError("Invalid amount in USD. Must be positive.")

    except ValueError as e:
        bot.send_message(user_id, f"Could not calculate result. {e}")
    except Exception as e:
        bot.send_message(user_id, f"An error occurred: {e}")


def handle_unregistered_state(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "Welcome! Please register your phone number.")
    user_states[user_id] = STATE_PHONE_REGISTRATION


def handle_phone_registration_state(message):
    user_id = message.from_user.id

    phone_number = message.text
    if is_valid_phone_number(phone_number):
        telegram_user = TelegramUser.objects.create(
            telegram_id=user_id,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            username=message.from_user.username,
            phone_number=phone_number
        )
        telegram_user.save()
        bot.send_message(user_id, f"Phone number {phone_number} registered successfully!")

        user_states[user_id] = STATE_REGISTERED

        handle_registered_state(message)
    else:
        bot.send_message(user_id, "Invalid phone number. Please enter a valid numeric phone number.")


if __name__ == "__main__":
    bot.polling(none_stop=True)
