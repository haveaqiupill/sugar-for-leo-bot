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
ADMIN_ID = os.environ["ADMIN_PASSWORD"]

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
(AFTER_START, FORWARD_MESSAGE) = range(2)

maintenance = 0


def start(bot, update):
    user = update.message.from_user
    chatid = update.message.chat.id
    logger.info(update.message.text.strip())

    logger.info("User {} with User ID {} just started conversation with bot.".format(
        user.username if user.username else user.first_name, user.id))
    button_list = [InlineKeyboardButton(text='Talk to my sugar parent', callback_data='toparent'),
                   InlineKeyboardButton(text='Talk to my sugar baby', callback_data='tobaby'),
                   InlineKeyboardButton(text='Cancel', callback_data='cancel')]

    menu = build_menu(button_list, n_cols=1, header_buttons=None, footer_buttons=None)

    mainmenutext = "<b>Hello {}!</b>\n\n".format(user.username if user.username else user.first_name)
    mainmenutext += LION + " Welcome to Sugar for Leo! " + LION + "\n" + "What do you want to do?"

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


def send_to_parent(bot, update):
    query = update.callback_query
    user = query.from_user
    logger.info("User {} has just started food rescue".format(user.username if user.username else user.first_name))

    button_list = [InlineKeyboardButton(text='Done', callback_data='forward'),
                   InlineKeyboardButton(text='Cancel', callback_data='cancel')]
    menu = build_menu(button_list, n_cols=1, header_buttons=None, footer_buttons=None)

    sendtext = "<b>What do you want to tell your sugar parent?</b>" + "\n\nType and send me your message below:"

    bot.editMessageText(text=sendtext,
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id,
                        reply_markup=InlineKeyboardMarkup(menu),
                        parse_mode=ParseMode.HTML)

    return FORWARD_MESSAGE

def send_to_baby(bot, update):
    query = update.callback_query
    user = query.from_user
    logger.info("User {} has just started food rescue".format(user.username if user.username else user.first_name))

    button_list = [InlineKeyboardButton(text='Done', callback_data='forward'),
                   InlineKeyboardButton(text='Cancel', callback_data='cancel')]
    menu = build_menu(button_list, n_cols=1, header_buttons=None, footer_buttons=None)

    sendtext="<b>What do you want to tell your sugar baby?</b>" + "\n\nType and send me your message below:"

    bot.editMessageText(text=sendtext,
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id,
                        reply_markup=InlineKeyboardMarkup(menu),
                        parse_mode=ParseMode.HTML)

    return FORWARD_MESSAGE



def forward_to_party(bot, update):
    try:
        user = update.message.from_user
        message_to_send = html.escape(update.message.text.strip())
        logger.info(
            "User {} has just submitted message".format(user.username if user.username else user.first_name))
        chatid = update.message.chat.id
        datashown = html.escape(update.message.text.strip())

        # deletes message sent by bot
        # bot.delete_message(chat_id=update.message.chat_id, message_id=INFOSTORE[user.id]["BotMessageID"][-1])


    # catch error due to back button:
    except AttributeError:
        query = update.callback_query
        user = query.from_user
        chatid = query.message.chat_id
        datashown = query.data
        logger.info('Data: query {}'.format(datashown))

        # deletes message previously sent by bot due to back
        # bot.delete_message(chat_id=query.message.chat_id, message_id=INFOSTORE[user.id]["BotMessageID"][-1])

    button_list = [InlineKeyboardButton(text='continue', callback_data='_continue'),
                   InlineKeyboardButton(text='exit', callback_data='cancel')]

    menu = build_menu(button_list, n_cols=2, header_buttons=None, footer_buttons=None)

    sendtext = "Message: {}." + message + "\n\n<b>The above message has been forwarded. </b>\n What do you wanna do next?".format(
        datashown)

    msgsent = bot.send_message(text=sendtext,
                               reply_markup=InlineKeyboardMarkup(menu),
                               chat_id=chatid,
                               parse_mode=ParseMode.HTML)

    # appends message sent by bot itself
    INFOSTORE[user.id]["BotMessageID"].append(msgsent['message_id'])

    return ConversationHandler.END

def _continue(bot, update):

    return AFTER_START


# for user cancelling
def cancel(bot, update):
    query = update.callback_query
    user = query.from_user
    logger.info("User {} cancelled the conversation.".format(user.username if user.username else user.first_name))

    # deletes message sent previously by bot
    # bot.delete_message(chat_id=query.message.chat_id, message_id=INFOSTORE[user.id]["BotMessageID"][-1])

    bot.send_message(text="Bye bye!" + SMILEY + "\n" + "Hope to hear from you soon!\n\n" + "Press /start again to continue the convo!",
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
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            AFTER_START: [CallbackQueryHandler(callback=send_to_parent, pattern='^(toparent)$'),
                          CallbackQueryHandler(callback=send_to_baby, pattern='^(tobaby)$'),
                          CallbackQueryHandler(callback=cancel, pattern='^(cancel)$')],

            FORWARD_MESSAGE: [MessageHandler(Filters.text, forward_to_party),
                              CallbackQueryHandler(callback=forward_to_party, pattern='^(forward)$'),
                              CallbackQueryHandler(callback=cancel, pattern='^(cancel)$')]},

        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True
    )

    # dispatch the food convo handler
    dispatcher.add_handler(conv_handler)

    # logs all errors
    dispatcher.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
