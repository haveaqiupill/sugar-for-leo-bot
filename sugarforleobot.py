from time import sleep
import logging
import os
import html
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler

# Set up telegram token
TELEGRAM_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']

# Set up admin groups
admin_group_id = '-1001199257588'
food_channel_id = '@nsefoodbottestchannel'
admin_user_ids = [250741897, ]  # cpf, nich, yt

# Set up logging
logging.basicConfig(
    format='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO)

logger = logging.getLogger(__name__)

# set up temporary store of info
INFOSTORE = {}


# Function to build buttons menu for every occasion
def build_menu(buttons, n_cols, header_buttons, footer_buttons):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


# Set up unique conversation states
(AFTER_START, CONSUME_TIME) = range(2)

maintenance = 0


def start(bot, update):
    user = update.message.from_user
    chatid = update.message.chat.id
    logger.info(update.message.text.strip())

    if maintenance == 1:
        logger.info("MAINTENANCE replied to {}".format(user.username if user.username else user.first_name))
        replytext = "Sorry, we are currently in maintenance, do check back for more free food!"
        replytext += "\n\nYour user ID = {}, chat ID = {}".format(str(user.id) if user.id else str(chatid), str(chatid))

        bot.send_message(text=replytext,
                         parse_mode=ParseMode.HTML,
                         chat_id=chatid)

        return ConversationHandler.END

    else:
        logger.info("User {} with User ID {} just started conversation with bot.".format(
            user.username if user.username else user.first_name, user.id))
        button_list = [InlineKeyboardButton(text='Talk to my sugar parent', callback_data='foodrescue'),
                       InlineKeyboardButton(text='Talk to my sugar baby', callback_data='feedback'),
                       InlineKeyboardButton(text='Cancel', callback_data='cancel')]

        menu = build_menu(button_list, n_cols=1, header_buttons=None, footer_buttons=None)

        mainmenutext = "<b>Hello {}!</b>\n\n".format(user.username if user.username else user.first_name)
        mainmenutext += "What do you want to do?"

        # set up INFOSTORE
        INFOSTORE[user.id] = {}
        INFOSTORE[user.id]['food'] = {}
        INFOSTORE[user.id]["BotMessageID"] = []

        msgsent = bot.send_message(text=mainmenutext,
                                   chat_id=chatid,
                                   reply_markup=InlineKeyboardMarkup(menu),
                                   parse_mode=ParseMode.HTML)

        # appends message sent by bot itself - the very first message: start message
        INFOSTORE[user.id]["BotMessageID"].append(msgsent['message_id'])

    return AFTER_START


def submit_consume_time(bot, update):
    query = update.callback_query
    user = query.from_user
    logger.info("User {} has just started food rescue".format(user.username if user.username else user.first_name))

    button_list = [InlineKeyboardButton(text='Cancel', callback_data='cancel')]
    menu = build_menu(button_list, n_cols=1, header_buttons=None, footer_buttons=None)

    sendtext = "<b>When must the food be consumed by?</b>"
    sendtext = "\n\nType and send me the time below:"

    bot.editMessageText(text=sendtext,
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id,
                        reply_markup=InlineKeyboardMarkup(menu),
                        parse_mode=ParseMode.HTML)

    return CONSUME_TIME


def submit_halal_cert(bot, update):
    try:
        user = update.message.from_user
        consume_time = html.escape(update.message.text.strip())
        INFOSTORE[user.id]["food"]["consume_time"] = consume_time
        logger.info(
            "User {} has just submitted food consume time".format(user.username if user.username else user.first_name))
        chatid = update.message.chat.id
        datashown = html.escape(update.message.text.strip())

        # deletes message sent by bot
        bot.delete_message(chat_id=update.message.chat_id, message_id=INFOSTORE[user.id]["BotMessageID"][-1])

    # catch error due to back button:
    except AttributeError:
        query = update.callback_query
        user = query.from_user
        chatid = query.message.chat_id
        datashown = query.data
        logger.info('Data: query {}'.format(datashown))

        # deletes message previously sent by bot due to back
        bot.delete_message(chat_id=query.message.chat_id, message_id=INFOSTORE[user.id]["BotMessageID"][-1])

    button_list = [InlineKeyboardButton(text='Yes, it is Halal Certified.', callback_data='halalyes'),
                   InlineKeyboardButton(text='No, it is not.', callback_data='halalno')]

    menu = build_menu(button_list, n_cols=2, header_buttons=None, footer_buttons=None)
    sendtext = "Previous selection: {}.\n\n<b>Is the food Halal Certified?</b>".format(datashown)

    msgsent = bot.send_message(text=sendtext,
                               reply_markup=InlineKeyboardMarkup(menu),
                               chat_id=chatid,
                               parse_mode=ParseMode.HTML)

    # appends message sent by bot itself
    INFOSTORE[user.id]["BotMessageID"].append(msgsent['message_id'])

    return ConversationHandler.END


def send_feedback(bot, update):
    query = update.callback_query
    user = query.from_user
    logger.info("User {} wants to send feedback.".format(user.username if user.username else user.first_name))

    # deletes message sent previously by bot
    bot.delete_message(chat_id=query.message.chat_id, message_id=INFOSTORE[user.id]["BotMessageID"][-1])

    bot.send_message(text="Please send your feedback in text below! We appreciate your feedback, thank you!",
                     chat_id=query.message.chat_id,
                     message_id=query.message.message_id,
                     parse_mode=ParseMode.HTML)

    return ConversationHandler.END


# for user cancelling
def cancel(bot, update):
    query = update.callback_query
    user = query.from_user
    logger.info("User {} cancelled the conversation.".format(user.username if user.username else user.first_name))

    # deletes message sent previously by bot
    bot.delete_message(chat_id=query.message.chat_id, message_id=INFOSTORE[user.id]["BotMessageID"][-1])

    bot.send_message(text="Bye! Talk to me again if you have excess food to share! Press /start anytime to begin.",
                     chat_id=query.message.chat_id,
                     message_id=query.message.message_id,
                     parse_mode=ParseMode.HTML)

    return ConversationHandler.END


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    updater = Updater(TELEGRAM_TOKEN)

    # dispatcher to register handlers
    dispatcher = updater.dispatcher

    # set up conversation handling for user side (for sending food)
    food_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            AFTER_START: [CallbackQueryHandler(callback=submit_consume_time, pattern='^(foodrescue)$'),
                          CallbackQueryHandler(callback=send_feedback, pattern='^(feedback)$'),
                          CallbackQueryHandler(callback=cancel, pattern='^(cancel)$')],

            CONSUME_TIME: [MessageHandler(Filters.text, submit_halal_cert),
                           CallbackQueryHandler(callback=cancel, pattern='^(cancel)$')]},

        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True
    )

    # dispatch the food convo handler
    dispatcher.add_handler(food_conv_handler)

    # logs all errors
    dispatcher.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
