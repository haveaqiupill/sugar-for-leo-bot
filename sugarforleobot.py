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
LION = u"\U0001F981"
SMILEY = u"\U0001F642"

#CHAT IDS
JINGYING = 508423467
KERYIN = 384865431
SHAHEEL = 99260110
PRISCILIA = 181854022
BLAKE = 559780833
GERALD = 231696047
AQILAH = 130512569
BRIAN = 209469386
NICHOLAS = 540825566
YINGQI = 523934057
ZHENGYI = 151469558
JAMESCHUA = 277020493
JAMESLEE = 200746779



# Function to build buttons menu for every occasion
def build_menu(buttons, n_cols, header_buttons, footer_buttons):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu

AFTER_CONSENT, FORWARD_PARENT, FORWARD_BABY= range(3)

# set up temporary store of info
INFOSTORE = {}

class User:
    def __init__(self, userid, sugarparentid, sugarbabyid):
        self.id = userid
        self.parentid = sugarparentid
        self.babyid = sugarbabyid

    def get_parentid(self):
        return self.parentid

    def get_babyid(self):
        return self.babyid

#USER ASSIGNMENT
keryin = User(KERYIN, JINGYING, SHAHEEL)
jingying = User(JINGYING, SHAHEEL, KERYIN)
shaheel = User(SHAHEEL, KERYIN, JINGYING)
yingqi = User(YINGQI, PRISCILIA, JAMESLEE)
priscilia = User(PRISCILIA, SHAHEEL, YINGQI)
jameslee = User(JAMESLEE, YINGQI, JINGYING)


#KEY-VALUE PAIR
ASSIGN = {KERYIN:keryin, JINGYING:jingying, SHAHEEL:shaheel, YINGQI:yingqi, PRISCILIA:priscilia, JAMESLEE:jameslee}


def start(bot, update):
    user = update.message.from_user
    chatid = update.message.chat.id

    mainmenutext = "<b>Hello {}!</b>\n\n".format(user.username if user.username else user.first_name)
    mainmenutext += LION + " Welcome to Sugar for Leo! " + LION + "\n" + 'What do you want to do? \n\nTake note: you can only send one text message per time via this bot! If you want to send another message, press /start again.'

    button_list = [InlineKeyboardButton(text='Talk to my sugar parent', callback_data='toparent'),
                   InlineKeyboardButton(text='Talk to my sugar baby', callback_data='tobaby'),
                   InlineKeyboardButton(text='Cancel', callback_data='cancel')]

    logger.info("User %s of id %s: %s", user.first_name, user.id, update.message.text)

    menu = build_menu(button_list, n_cols=1, header_buttons=None, footer_buttons=None)

    # set up INFOSTORE
    INFOSTORE[user.id] = {}
    INFOSTORE[user.id]["BotMessageID"] = []

    msgsent = bot.send_message(text=mainmenutext,
                               chat_id=chatid,
                               reply_markup=InlineKeyboardMarkup(menu),
                               parse_mode=ParseMode.HTML)

    # appends message sent by bot itself - the very first message: start message
    INFOSTORE[user.id]["BotMessageID"].append(msgsent['message_id'])

    return AFTER_CONSENT


def send_to_parent(bot, update):
    query = update.callback_query
    user = query.from_user
    logger.info("User {} has just chose to talk to the sugar parent".format(user.username if user.username else user.first_name))

    sendtext = "<b>What do you want to tell your sugar parent?</b>" + "\n\nType and send me your message below:"
    sendText.replace('<', '\\<')
    bot.send_message(chat_id=user.id, text=sendtext, parse_mode=ParseMode.HTML)

    #INFOSTORE[user.id]["BotMessageID"] = update.message.chat_id

    return FORWARD_BABY

def send_to_baby(bot, update):
    query = update.callback_query
    user = query.from_user
    logger.info("User {} has just chose to talk to the sugar baby".format(user.username if user.username else user.first_name))

    sendtext="<b>What do you want to tell your sugar baby?</b>" + "\n\nType and send me your message below:"
    bot.send_message(chat_id=user.id, text=sendtext, parse_mode=ParseMode.HTML)

    #INFOSTORE[user.id]["BotMessageID"] = update.message.chat_id

    return FORWARD_PARENT


def _forward_from_parent(bot, update):
    user = update.message.from_user
    chatid = update.message.chat.id
    INFOSTORE[user.id] = update.message.text

    #bot.delete_message(chat_id=update.message.chat_id, message_id=INFOSTORE[user.id]["BotMessageID"])

    logger.info("Message of %s: %s", user.first_name, update.message.text)

    sendtext = INFOSTORE[user.id] +  "\n\n"
    sendtext += 'Thank you! Your message has been forwarded. Type /start to send again'

    messagefromparent = '<b>Hello! Your sugar parent wants to say:</b>\n\n' + INFOSTORE[user.id]
    messagetoadmin = user.first_name + " of username " + user.username + " sent this to the sugar baby: \n\n" + INFOSTORE[user.id]

    bot.send_message(
        text=messagefromparent,
        chat_id=ASSIGN.get(user.id).get_babyid(),
        message_id=update.message.message_id,
        parse_mode=ParseMode.HTML)

    bot.send_message(
        text=messagetoadmin,
        chat_id=admin_group_id,
        message_id=update.message.message_id,
        parse_mode=ParseMode.HTML)

    update.message.reply_text(sendtext)
    return ConversationHandler.END

def _forward_from_baby(bot, update):
    user = update.message.from_user
    chatid = update.message.chat.id
    INFOSTORE[user.id] = update.message.text

    #bot.delete_message(chat_id=update.message.chat_id, message_id=INFOSTORE[user.id]["BotMessageID"])

    logger.info("Message of %s: %s", user.first_name, update.message.text)

    sendtext = INFOSTORE[user.id] + "\n\n"
    sendtext += 'Thank you! Your message has been forwarded. Type /start to send again'

    messagefrombaby = '<b>Hello! Your sugar baby wants to say:</b>\n\n' + INFOSTORE[user.id]
    messagetoadmin = user.first_name + " of username " + user.username + " sent this to the sugar parent: \n\n" + INFOSTORE[user.id]

    bot.send_message(
        text=messagefrombaby,
        chat_id=ASSIGN.get(user.id).get_parentid(),
        message_id=update.message.message_id,
        parse_mode=ParseMode.HTML)

    bot.send_message(
        text=messagetoadmin,
        chat_id=admin_group_id,
        message_id=update.message.message_id,
        parse_mode=ParseMode.HTML)

    update.message.reply_text(sendtext)
    return ConversationHandler.END


# for user cancelling
def cancel(bot, update):
    query = update.callback_query
    user = query.from_user
    logger.info("User {} cancelled the conversation.".format(user.username if user.username else user.first_name))


    bot.send_message(text="Bye bye!" + SMILEY + "\n\n" + "Hope to hear from you soon!\n\n" + "Press /start again to continue the convo!",
                     chat_id=user.id,
                     message_id=None,
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
            AFTER_CONSENT: [CallbackQueryHandler(callback = send_to_parent, pattern = '^(toparent)$'),
                                CallbackQueryHandler(callback = send_to_baby, pattern = '^(tobaby)$'),
                                CallbackQueryHandler(callback = cancel, pattern = '^(cancel)$'),
                            MessageHandler(Filters.text, _forward_from_parent),
                            MessageHandler(Filters.text, _forward_from_baby)],

            FORWARD_PARENT: [MessageHandler(Filters.text, _forward_from_parent)],

            FORWARD_BABY: [MessageHandler(Filters.text, _forward_from_baby)]
        },

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









