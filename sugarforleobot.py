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

# Function to build buttons menu for every occasion
def build_menu(buttons, n_cols, header_buttons, footer_buttons):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu

CONSENT, PHOTO, LOCATION, BIO = range(4)

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
    logger.info("User %s of id %s: %s", user.first_name, user.id, update.message.text)
    update.message.reply_text('Thank you for your consent! To get Sugar for Leo started, please send me a photo of yourself, '
                              'so that your sugar parent knows what you look like, or send /skip if you don\'t want to.',
                              reply_markup=ReplyKeyboardRemove())

    return PHOTO


def photo(bot, update):
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('user_photo.jpg')
    logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')
    update.message.reply_text('Naise! Now, send me your location, '
                              'or send /skip if you don\'t want to.')

    return LOCATION


def skip_photo(bot, update):
    user = update.message.from_user
    logger.info("User %s did not send a photo.", user.first_name)
    update.message.reply_text('Looks like someone is having a bad hair day or is the lighting too dark for you to be seen?'
                              'Nevermind, send me your location please :), '
                              'or send /skip.')

    return LOCATION


def location(bot, update):
    user = update.message.from_user
    user_location = update.message.location
    logger.info("Location of %s: %f / %f", user.first_name, user_location.latitude,
                user_location.longitude)
    update.message.reply_text('Maybe I can visit your room sometime! '
                              'Last but not least, tell me something interesting about yourself.')

    return BIO


def skip_location(bot, update):
    user = update.message.from_user
    logger.info("User %s did not send a location.", user.first_name)
    update.message.reply_text('You seem a bit paranoid! But that was a wise choice.\n'
                              'Last but not least, tell me something interesting about yourself.')

    return BIO


def bio(bot, update):
    user = update.message.from_user
    logger.info("Bio of %s: %s", user.first_name, update.message.text)
    update.message.reply_text('Thank you you uninteresting creature! TTYL!!')

    return ConversationHandler.END


def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('You suck! But bye.',
                              reply_markup=ReplyKeyboardRemove())

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

            PHOTO: [MessageHandler(Filters.photo, photo),
                    CommandHandler('skip', skip_photo)],

            LOCATION: [MessageHandler(Filters.location, location),
                       CommandHandler('skip', skip_location)],

            BIO: [MessageHandler(Filters.text, bio)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
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









