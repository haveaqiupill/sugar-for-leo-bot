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
admin_user_ids = []  # jingying, keryin

# Set up logging
logging.basicConfig(
    format='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO)

logger = logging.getLogger(__name__)

# EMOJI UNICODE
LION = u"\U0001F981"
SMILEY = u"\U0001F642"
HEART = u"\u2764"
CROSS = u"\u274C"


# Function to build buttons menu for every occasion
def build_menu(buttons, n_cols, header_buttons, footer_buttons):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu

# set up states
AFTER_CONSENT, FORWARD_PARENT, FORWARD_BABY= range(3)

# set up temporary store of info
INFOSTORE = {}

class User:
    def __init__(self, userid, sugarparentid, sugarbabyid, likes, dislikes, remarks, unit, tolerance_level, name):
        self.id = userid
        self.parentid = sugarparentid
        self.babyid = sugarbabyid
        self.likes = likes
        self.dislikes = dislikes
        self.remarks = remarks
        self.unit = unit
        self.tolerance_level = tolerance_level
        self.name = name

    def get_parentid(self):
        return self.parentid

    def get_babyid(self):
        return self.babyid

    def get_likes(self):
        return self.likes

    def get_dislikes(self):
        return self.dislikes

    def get_remarks(self):
        return self.remarks

    def get_unit(self):
        return self.unit

    def get_tolerance_level(self):
        return self.tolerance_level

    def get_name(self):
        return self.name
        

        

#KEY-VALUE PAIR
ASSIGN = {}



def start(bot, update):
    user = update.message.from_user
    chatid = update.message.chat.id

    if ASSIGN.get(user.id) is None:

        bot.send_message(text="Sorry you are not registered yet!",
                         chat_id=user.id,
                        message_id=None,
                        parse_mode=ParseMode.HTML)

        return ConversationHandler.END

    else:
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

        return AFTER_CONSENT


def send_to_parent(bot, update):
    query = update.callback_query
    user = query.from_user

    sendtext = "<b>What do you want to tell your sugar parent?</b>" + "\n\nType and send me your message below:"

    bot.send_message(chat_id=user.id, text=sendtext, parse_mode=ParseMode.HTML)

    return FORWARD_BABY


def send_to_baby(bot, update):
    query = update.callback_query
    user = query.from_user

    babyID = ASSIGN.get(user.id).get_babyid()
    baby = ASSIGN.get(babyID)

    sendtext = "<b>Your sugar baby is</b> " + baby.get_name() + ", staying in " + baby.get_unit() + "\n\n"
    sendtext += "<b>Tolerance level:</b> " + baby.get_tolerance_level() + "\n\n"
    sendtext += HEART + "<b>Here are the likes of your sugar baby:</b>" + HEART + "\n" + baby.get_likes()  + "\n\n"
    sendtext += CROSS + "<b>Here are the dislikes of your sugar baby:</b>" + CROSS + "\n"  + baby.get_dislikes()  + "\n\n"
    sendtext += "<b>Please take these remarks seriously!!:</b> \n" + baby.get_remarks() + "\n\n"
    sendtext += "<b>What do you want to tell your sugar baby?</b>" + "\n\nType and send me your message below:"

    bot.send_message(chat_id=user.id, text=sendtext, parse_mode=ParseMode.HTML)

    return FORWARD_PARENT


def markdown(string):
    edited = string.replace("<", "&lt;")
    edited.replace("&", "&amp")
    edited.replace("\"", "&quot")
    edited.replace("\'", "&#39;")
    return edited


def _forward_from_parent(bot, update):
    user = update.message.from_user
    chatid = update.message.chat.id

    changedMessage = markdown(update.message.text)
    INFOSTORE[user.id] = changedMessage

    #bot.delete_message(chat_id=update.message.chat_id, message_id=INFOSTORE[user.id]["BotMessageID"])
    
    sendtext = "&quot " + INFOSTORE[user.id] + " &quot" +  "\n\n"
    sendtext += 'Thank you! Your message has been forwarded. \n\n<b>Press /start to send again!</b>'

    messagefromparent = '<b>Hello! Your sugar parent wants to say:</b>\n\n' + INFOSTORE[user.id]

    bot.send_message(
        chat_id=ASSIGN.get(user.id).get_babyid(),
        text=messagefromparent,
        message_id=update.message.message_id,
        parse_mode=ParseMode.HTML)
        
    update.message.reply_text(text=sendtext, parse_mode=ParseMode.HTML)
    return ConversationHandler.END

def _forward_from_baby(bot, update):
    user = update.message.from_user
    chatid = update.message.chat.id

    changedMessage = update.message.text.replace("<", "&lt;")
    INFOSTORE[user.id] = changedMessage
    
    sendtext = "&quot " + INFOSTORE[user.id] + " &quot" + "\n\n"
    sendtext += 'Thank you! Your message has been forwarded. \n\n<b>Press /start to send again!</b>'

    messagefrombaby = '<b>Hello! Your sugar baby wants to say:</b>\n\n' + INFOSTORE[user.id]

    bot.send_message(
        chat_id=ASSIGN.get(user.id).get_parentid(),
        text=messagefrombaby,
        message_id=update.message.message_id,
        parse_mode=ParseMode.HTML)

    update.message.reply_text(text=sendtext, parse_mode=ParseMode.HTML)
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

    # Add conversation handler with the states AFTER_CONSENT, FORWARD_PARENT, FORWARD_BABY
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









