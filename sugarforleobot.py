from time import sleep
import logging
import os
import html
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler

# Set up telegram token
TELEGRAM_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']

# Set up admin groups
admin_group_id = '-361131404'
sfl_channel_id = '@SugarForLeoBot'
admin_user_ids = [508423467, 384865431]  # jingying, keryin

# Using the admin id would allow you to send messages to everyone
#ADMIN_ID = os.environ["ADMIN_PASSWORD"]

# Set up logging
logging.basicConfig(
    format='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO)

logger = logging.getLogger(__name__)

# Function to build buttons menu for every occasion
def build_menu(buttons, n_cols, header_buttons, footer_buttons):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu

def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")
    return ConversationHandler.END

def main():
    updater = Updater(TELEGRAM_TOKEN)

    # dispatcher to register handlers
    dispatcher = updater.dispatcher
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    # logs all errors
    dispatcher.add_error_handler(error)

    updater.start_polling()
    updater.idle()

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

if __name__ == '__main__':
    main()
