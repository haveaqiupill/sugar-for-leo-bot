from time import sleep
import logging
import os
import html
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler, CallbackQueryHandler

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

# EMOJI UNICODE
CAKE = u"\U0001F382"
LION = u"\U0001F981"
SMILEY = u"\U0001F642"

# Function to build buttons menu for every occasion
def build_menu(buttons, n_cols, header_buttons, footer_buttons):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu

CONSENT, AFTER_CONSENT, FORWARD_MESSAGE = range(3)

# set up temporary store of info
INFOSTORE = {}

def start(bot, update):
    reply_keyboard = [['I consent']]
    user = update.message.from_user
    chatid = update.message.chat.id

    mainmenutext = "<b>Hello {}!</b>\n\n".format(user.username if user.username else user.first_name)
    mainmenutext += LION + " Welcome to Sugar for Leo! " + LION + "\n\n"
    bot.send_message(text=mainmenutext,
                     parse_mode=ParseMode.HTML,
                     chat_id=chatid)

    update.message.reply_text(
        'Firstly, please gimme consent for data collection thankiew\n\n' 
        'I consent to providing my personal data for the purpose of Leo House Events. '
        'I would also agree to receive important updates pertaining to matters contained in this survey. '
        'All personal information will be kept confidential and be used only for the purpose of Leo House Events. '
        'I understand that should I wish to withdraw my consent for the organising committee to contact me for the purposes stated above, '
        'I could notify Qiu Jing Ying, Residential College 4, Leo House Committee Secretary, in writing to e0323887@u.nus.edu. '
        'The organising committee will then remove my personal information from their database, and I allow 7 business days for my withdrawal of consent to take effect.',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return CONSENT


def consent(bot, update):
    user = update.message.from_user
    chatid = update.message.chat.id

    button_list = [InlineKeyboardButton(text='Talk to my sugar parent', callback_data='toparent'),
                   InlineKeyboardButton(text='Talk to my sugar baby', callback_data='tobaby'),
                   InlineKeyboardButton(text='Cancel', callback_data='cancel')]

    update.message.reply_text(
        'Thank you for your consent! ',
        reply_markup=ReplyKeyboardRemove())
    logger.info("User %s of id %s: %s", user.first_name, user.id, update.message.text)

    menu = build_menu(button_list, n_cols=1, header_buttons=None, footer_buttons=None)

    bot.send_message(text='Now, what do you want to do?',
                     chat_id=chatid,
                     reply_markup=InlineKeyboardMarkup(menu),
                     parse_mode=ParseMode.HTML)

    return AFTER_CONSENT


def send_to_parent(bot, update):
    query = update.callback_query
    user = query.from_user
    logger.info("User {} has just chose to talk to the sugar parent".format(user.username if user.username else user.first_name))

    button_list = [InlineKeyboardButton(text='Cancel', callback_data='cancel')]
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
    logger.info("User {} has just chose to talk to the sugar baby".format(user.username if user.username else user.first_name))

    button_list = [InlineKeyboardButton(text='Cancel', callback_data='cancel')]
    menu = build_menu(button_list, n_cols=1, header_buttons=None, footer_buttons=None)

    sendtext="<b>What do you want to tell your sugar baby?</b>" + "\n\nType and send me your message below:"

    bot.editMessageText(text=sendtext,
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id,
                        reply_markup=InlineKeyboardMarkup(menu),
                        parse_mode=ParseMode.HTML)



    return FORWARD_MESSAGE

def _forward_to_party(bot, update):
    

    user = update.message.from_user
    logger.info("Message of %s: %s", user.first_name, update.message.text)
    update.message.reply_text('Thank you! I hope we can talk again some day.')

    return ConversationHandler.END


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


def error(bot, update):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TELEGRAM_TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states CONSENT, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            CONSENT: [RegexHandler('^(I consent)$', consent)],



            AFTER_CONSENT: [CallbackQueryHandler(callback = send_to_parent, pattern = '^(toparent)$'),
                                CallbackQueryHandler(callback = send_to_baby, pattern = '^(tobaby)$'),
                                CallbackQueryHandler(callback = cancel, pattern = '^(cancel)$')],

            FORWARD_MESSAGE: [MessageHandler(Filters.text, _forward_to_party),
                              CallbackQueryHandler(callback=cancel, pattern='^(cancel)$')]},

        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True

    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()









