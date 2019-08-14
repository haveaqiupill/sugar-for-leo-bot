import json  # JSON lib
import requests  # HTTP lib
import os  # used to access env variables
import time
import urllib.parse  # lib that deals with urls
from dbhelper import *  # imports all user-defined functions to

TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
BASE_URL = "https://api.telegram.org/bot{}/".format(TOKEN)

# groups based on tolerance level, each player is assigned an 8-character unique alphanumeric identifier - game id
# 8 groups for RC4 Angel Mortal games: AM1, AM2, AM3, AM4, AM5, AM6, AM7, AM8
# index to the left: ANGEL | index to the right: MORTAL
AM = []
AM2 = []
AM3 = []
AM4 = []
AM5 = []
AM6 = []
AM7 = []
AM8 = []


# Using the admin id would allow you to send messages to everyone
ADMIN_ID = os.environ["ADMIN_PASSWORD"]

user_db = userdb()
am_db = amdb()
users = []  # list of users objects
am_participants = []  # list of player chat_ids

# EMOJI UNICODE
CAKE = u"\U0001F382"
WHALE = u"\U0001F40B"
ROBOT = u"\U0001F916"
SKULL = u"\U0001F480"
SMILEY = u"\U0001F642"
SPOUTING_WHALE = u"\U0001F433"
SPEECH_BUBBLE = u"\U0001F4AC"
THINKING_FACE = u"\U0001F914"
QUESTION_MARK = u"\U0001F64F"
MONKEY = u"\U0001F64A"

# TELEGRAM KEYBOARD KEYS
ABOUT_THE_BOT_KEY = u"About the Bot" + " " + SPOUTING_WHALE
ADMIN_KEY = u"/admin"
ANGEL_KEY = u"/angel"
ANONYMOUS_CHAT_KEY = u"Angel-Mortal Anonymous Chat" + " " + SPEECH_BUBBLE
HELP_KEY = u"Help" + " " + QUESTION_MARK
RULES_KEY = u"Rules" + " " + MONKEY
MENU_KEY = u"/mainmenu"
MORTAL_KEY = u"/mortal"
SEND_ALL_KEY = u"/Send_All"
SEND_ONE_KEY = u"/Send_One"
CHECK_REGIS_KEY = u"/Check_Player_Registration"

# TELEGRAM KEYBOARD OPTIONS
AM_KEYBOARD_OPTIONS = [ANGEL_KEY, MORTAL_KEY, MENU_KEY]
KEYBOARD_OPTIONS = [ANONYMOUS_CHAT_KEY, ABOUT_THE_BOT_KEY, HELP_KEY, RULES_KEY]
ADMIN_KEYBOARD = [SEND_ALL_KEY, SEND_ONE_KEY, CHECK_REGIS_KEY]

# GREETINGS
ABOUT_THE_BOT = SPOUTING_WHALE + " *About OrcaBot* " + SPOUTING_WHALE + "\n\n" + CAKE + " Birthday: June 2017\n\n" +\
                ROBOT + " Currently maintained by Shao Yi\n\n" + SKULL +\
                " Past Bot Developers: Bai Chuan, Fiz, Youkuan, Kang Ming, Zhi Yu\n\n"
AM_GREETING = "Hello there, {}!\n\n" +\
              "Click or type any of the following:\n" +\
              "/angel: Chat with your Angel\n" +\
              "/mortal: Chat with your Mortal\n" +\
              "/mainmenu: Exits the Chat feature, and returns to the Main Menu"

AM_LOGIN_GREETING = "Please enter your 8-character Game ID.\n\n" +\
                     "or click /mainmenu to exit the registration process"
INVALID_PIN = "You have entered the wrong 8-character Game ID. Please try again, or type /mainmenu to exit."
REDIRECT_GREETING = "Did you mean: /mainmenu"
REQUEST_ADMIN_ID = "Please enter your Admin ID to proceed."
SEND_ADMIN_GREETING = "Hello there, Administrator! What do you want to say to everyone?\n" +\
                      "Whatever you submit from now on will be broadcasted to all users, be CAREFUL!" +\
                      "Type /mainmenu to exit, once you have made your announcement."
SEND_CONNECTION_FAILED = u"This feature is unavailable now as he/she has yet to sign in to the game." +\
                         u" Please be patient and try again soon!" + SMILEY + "\n\nType /mainmenu to go back."
SUCCESSFUL_ANGEL_CONNECTION = "You have been connected with your Angel." +\
                            " Anything you type here will be sent anonymously to him/her.\n" +\
                            "To exit, type /mainmenu"
SUCCESSFUL_MORTAL_CONNECTION = "You have been connected with your Mortal." +\
                               " Anything you type here will be sent anonymously to him/her.\n" +\
                               "To exit, type /mainmenu"
HELLO_GREETING = "Hello there, {}! Oscar at your service! " + SPOUTING_WHALE
HELP_MESSAGE = "Hello there, {}!\n\n" +\
               "Orcabot is a homegrown telegram bot that allows you to anonymously chat with your Angel or Mortal.\n\n" +\
               "While in the Main Menu, click on:\n" +\
               ANONYMOUS_CHAT_KEY + ": To chat with your Angel or Mortal\n" +\
               ABOUT_THE_BOT_KEY + ": To view information about the bot\n" +\
               HELP_KEY + ": To explore this bot's functionality\n" +\
               RULES_KEY + ": To view the game rules\n\n" +\
               "While in the Chat feature, type any of the following to:\n" +\
               ANGEL_KEY + ": Chat with your Angel\n" +\
               MORTAL_KEY + ": Chat with your Mortal\n\n" +\
               "Type " + MENU_KEY + " at any point in time to exit the Chat feature, and return to the Main Menu\n\n" +\
               "Please message @shaozyi @amosaiden if you need technical assistance!\n" +\
               "Thank you and we hope you'll have fun throughout this game! :)"
GAME_RULES_MESSAGE = "How Discovering True Friends work\n\n" +\
                     "Each of you who participated will be assigned an Angel and a Mortal. " +\
                     "Of course, you will know the identity of your Mortal while your angel’s identity will be kept " +\
                     "from you. Throughout the course of the event, feel free to chat with both your angel and mortal " +\
                     "through OrcaBot where your identity will be kept secret, and take care of your mortal with " +\
                     "anonymous gift and pranks according to their indicated tolerance levels! " +\
                     "Of course, you can look forward to seeing what your own angel does for you as well!\n\n" +\
                     "Explanation for tolerance levels\n\n" +\
                     "Tolerance Levels\n" +\
                     "1: Gift Exchange, do nice things only!\n" +\
                     "2: Pranks are to be minimal, and no clean up required!\n" +\
                     "3: Pranks are fine, minimal clean up.\n" +\
                     "4: Minor inconveniences are encouraged!\n" +\
                     "5: I don’t mind my door taped up.\n" +\
                     "1 – 5 can’t come into room\n\n" +\
                     "Dos :)\n" +\
                     "• Observe the Tolerance Levels your mortals have indicated.\n" +\
                     "• Try to accommodate (if any) requests of your mortals e.g. avoid allergies\n" +\
                     "• Balance out the pranks with gifts - moderation is key!\n" +\
                     "• Try (your best) to keep your identity hidden.\n" +\
                     "• Be active in the event! :)\n" +\
                     "• Share your pranks and gifts throughout the event in the group chat!\n\n" +\
                     "Don'ts :(\n" +\
                     "• Cause major damage (eg. breaking a treasured object) even if they’ve indicated no boundaries.\n" +\
                     "• Flout other RC/NUS rules (e.g. theft, possession of alcohol *ahem ahem*).\n" +\
                     "• Cause major inconveniences, especially along the common corridor" +\
                     "(e.g. blockade the walkway, pranks involving powdered substances like flour or curry powder).\n" +\
                     "• Cause fire hazards and hinder evacuation routes.\n" +\
                     "• Write, draw or scribble any obscene/vulgar contents on doors/common area.\n\n" +\
                     "If you have any other questions, concerns or doubts, don’t be afraid to reach out to the" +\
                     " organizing comm! We hope you have fun and make new friends as well!\n\n" +\
                     "Best regards,\n" +\
                     "Your Organizing Committee"

# HELP_MESSAGE = "<User guide for bot features>\n\n"
# GAME_RULES_MESSAGE = "<Insert games rules>"

# # TELEGRAM KEYBOARD KEYS
# ABOUT_THE_BOT_KEY = u"About the Bot" + " " + SPOUTING_WHALE
# ADMIN_KEY = u"/admin"
# ANGEL_KEY = u"/angel"
# ANONYMOUS_CHAT_KEY = u"Angel-Mortal Anonymous Chat" + " " + SPEECH_BUBBLE
# HELP_KEY = u"/help"
# RULES_KEY = u"/rules"
# MENU_KEY = u"/mainmenu"
# MORTAL_KEY = u"/mortal"

# # TELEGRAM KEYBOARD OPTIONS
# AM_KEYBOARD_OPTIONS = [ANGEL_KEY, MORTAL_KEY, MENU_KEY]
# KEYBOARD_OPTIONS = [ANONYMOUS_CHAT_KEY, ABOUT_THE_BOT_KEY, HELP_KEY, RULES_KEY]



# Sends a HTTP GET request using the given url.
# Returns the response in utf8 format
def send_get_request(url):
    response = requests.get(url)
    decoded_response = response.content.decode("utf8")
    return decoded_response


# Converts the HTTP response to a JSON object
# Returns a JSON object that represents the telegram bot api response
def convert_response_to_json(response):
    return json.loads(response)


# Sends a GET request representing a getUpdates() method call to the Telegram BOT API
# and retrieves a JSON object that represents the response, that has an Array of Update objects
# URL used in GET request is appended to make a getUpdates() method call.
# If @param offset is not None, then it is appended to the URL.
def get_updates(offset=None):
    url = BASE_URL + "getUpdates?timeout=100"
    if offset:
        url += "&offset={}".format(offset)
    response = send_get_request(url)
    return convert_response_to_json(response)


# Gets the last updated id of the update results
def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


# Gets the text and chat id of the last update
# Returns a tuple containing the text and chat id of the last update
def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]

    return text, chat_id


# Converts a defined range of options for a one-time keyboard, represented by a dictionary, into a JSON string
# Returns a JSON string that represents a dictionary containing the keyboard options
def build_keyboard(items):
    keyboard = [[item] for item in items]
    reply_markup = {"keyboard": keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)


# Converts a defined range of keyboard options represented by a dictionary into a JSON string
# Returns a JSON string that triggers the keyboard removal
def remove_keyboard():
    reply_markup = {"remove_keyboard": True, "selective": True}
    return json.dumps(reply_markup)

# print() at end is the main logging feature of the program currently. Use `heroku logs --tail` to view
# the logs in real time
# Sends a text in a message to another telegram user, using the telegram sendMessage method
def send_message(text, recipient_chat_id, recipient_name, sender_name="OrcaBot", reply_markup=None):
    try:
        encoded_text = (text.encode("utf8"))  # newline characters in the string are escaped once encoded here
    except:
        pass
    request_text = urllib.parse.quote_plus(encoded_text) # converts url-reserved characters in encoded string
    request_url = BASE_URL + "sendMessage?text={}&chat_id={}".format(request_text, recipient_chat_id)
    if reply_markup:
        request_url += "&reply_markup={}".format(reply_markup)
    send_get_request(request_url)
    print("From: {0!s}\nTo: {1!s}\nMessage: {2!s}".format(sender_name, recipient_name, text))


# USER PROFILE DECISION MAKING
class User:
    # Instance variables
    def __init__(self, userid, username):
        self.id = userid
        self.name = username
        self.angel_name = None
        self.mortal_name = None
        self.angel_chat_id = 0
        self.mortal_chat_id = 0

    # Function to open up the main menu with keyboard options.
    def mainmenu(self, text, chat_id):
        formatted_hello_greeting = HELLO_GREETING.format(self.name)
        if text == MENU_KEY:
            keyboard = build_keyboard(KEYBOARD_OPTIONS)
            send_message(formatted_hello_greeting, chat_id, self.name, reply_markup=keyboard)

        elif text == ABOUT_THE_BOT_KEY:

            send_message(ABOUT_THE_BOT, chat_id, self.name)
            keyboard = build_keyboard(KEYBOARD_OPTIONS)
            send_message(formatted_hello_greeting, chat_id, self.name, reply_markup=keyboard)

        elif text == ANONYMOUS_CHAT_KEY:
            chat_ids = [records[2] for records in am_db.get_all_records()]
            if chat_id in chat_ids:       # ??? if 8 digit alphanumeric ID is in the list
                send_message(AM_GREETING, chat_id, self.name, reply_markup=remove_keyboard())
                self.stage = self.anonymous_chat
            else:
                send_message(AM_LOGIN_GREETING, chat_id, self.name, reply_markup=remove_keyboard())
                self.stage = self.register

        elif text == ADMIN_KEY:
            send_message(REQUEST_ADMIN_ID, chat_id, self.name, reply_markup=remove_keyboard())
            self.stage = self.admin_login

        elif text == HELP_KEY:
            send_message(HELP_MESSAGE, chat_id, self.name, reply_markup=remove_keyboard())

        elif text == RULES_KEY:
            send_message(GAME_RULES_MESSAGE, chat_id, self.name, reply_markup=remove_keyboard())

        # Reopen main menu if no keywords match.
        else:
            keyboard = build_keyboard(KEYBOARD_OPTIONS)
            send_message(formatted_hello_greeting, chat_id, self.name, reply_markup=keyboard)

    # A method pointer that is reassigned constantly.
    # Once reassigned to another method with same number of parameters, then the next user input will be directed
    # to the newly reassigned method.
    def stage(self, text, chat_id):
        self.mainmenu(text, chat_id)

    # Prompts the user for the admin password for login.
    # If valid password, then then admin is allowed to send a message to all users.
    def admin_login(self, text, chat_id):
        if text not in ADMIN_ID:
            send_message(INVALID_PIN, chat_id, self.name, reply_markup=remove_keyboard())
            return
        else:
            send_message(SEND_ADMIN_GREETING, chat_id, self.name, reply_markup=remove_keyboard())
            self.stage = self.send_all
        elif text == SEND_ONE_KEY:
            send_message("Please key in the Game ID of the participant", chat_id, self.name)
            self.stage = self.receive_game_id
        elif text == CHECK_REGIS_KEY:
            send_message("Reply 'Y' to check registration status, or 'N' to return to mainmenu.", chat_id, self.name)
            self.stage = self.check_registration

    # helper function that fetches chat_id from database using game_id and sends text to the chat_id
    def fetch_then_send(self, text, game_id):
        owner_data = am_db.get_user_record_from_game_id(game_id)
        recipient_data = owner_data.fetchone()
        if recipient_data is not None:
            send_message("From the Admin:\n" + text, recipient_data[2], self.name)

    # chat_id is required to match the number of parameters in stage()
    # Sends a message to all players if administrator credentials are approved.
    def send_all(self, text, chat_id):
        list_of_ids = AM1 + AM2 + AM3 + AM4 + AM5 + + COMM + ADMINS
        for game_id in list_of_ids:
            self.fetch_then_send(text, game_id)
        return

    # chat_id is required to match the number of parameters in stage()
    # Sends a message to all players if administrator credentials are approved.
    def send_all(self, text, chat_id):
        list_of_ids = AM + AM2 + AM3 + AM4 + AM6 + AM7 + AM8
        for person_id in list_of_ids:
            owner_data = am_db.get_user_record_from_game_id(person_id)
            recipient_data = owner_data.fetchone()
            if recipient_data is not None:
                am_participants.append(recipient_data[2])
        for cid in am_participants:  # gets the telegram chat_id each time
            send_message("From the Admin:\n" + text, cid, self.name)
        return

    # Registers a user.
    # Verifies the user PIN number first, then registers user in the angel mortal database
    def register(self, user_pin, chat_id):
        if user_pin not in AM and user_pin not in AM2 and user_pin not in AM3 and user_pin not in AM4:
            send_message(INVALID_PIN, chat_id, self.name, reply_markup=remove_keyboard())
            return
        else:
            am_db.register(user_pin, chat_id, self.name)
            send_message(AM_GREETING, chat_id, self.name, reply_markup=remove_keyboard())
            self.stage = self.anonymous_chat

    # user_record[0] = serial number
    # user_record[1] = unique identifier (game_id)
    # user_record[2] = user chat_id
    # user_record[3] = name on telegram
    # user_record[4] = isRegistered todo change to boolean
    # Initialises a chat with a user's angel or mortal.
    def anonymous_chat(self, text, chat_id):
        # returns the cursor that has executed the SQL statement in postgres
        user_record = am_db.get_user_record_from_user_chat_id(chat_id).fetchone()
        user_game_id = user_record[1]
        if text == ANGEL_KEY:
            if user_game_id in AM:
                angel_game_id = AM[(AM.index(user_game_id) - 1)]
            elif user_game_id in AM2:
                angel_game_id = AM2[(AM2.index(user_game_id) - 1)]
            elif user_game_id in AM3:
                angel_game_id = AM3[(AM3.index(user_game_id) - 1)]
            elif user_game_id in AM4:
                angel_game_id = AM4[(AM4.index(user_game_id) - 1)]
            elif user_game_id in AM5:
                angel_game_id = AM5[(AM5.index(user_game_id) - 1)]
            elif user_game_id in AM6:
                angel_game_id = AM6[(AM6.index(user_game_id) - 1)]
            elif user_game_id in AM7:
                angel_game_id = AM7[(AM7.index(user_game_id) - 1)]
            else:
                angel_game_id = AM8[(AM3.index(user_game_id) - 1)]

            angel_record = am_db.get_user_record_from_game_id(angel_game_id).fetchone()
            if angel_record is None:
                send_message(SEND_CONNECTION_FAILED, chat_id, self.name)
            else:
                self.angel_chat_id = angel_record[2]
                self.mortal_name = angel_record[3]
                send_message(SUCCESSFUL_ANGEL_CONNECTION, chat_id, self.name)
                self.stage = self.chatwithparent

        elif text == MORTAL_KEY:
            # circular list
            if user_game_id in AM:
                mortal_game_id = AM[(AM.index(user_game_id) + 1) % len(AM)]
            elif user_game_id in AM2:
                mortal_game_id = AM2[(AM2.index(user_game_id) + 1) % len(AM2)]
            elif user_game_id in AM3:
                mortal_game_id = AM3[(AM3.index(user_game_id) + 1) % len(AM3)]
            elif user_game_id in AM4:
                mortal_game_id = AM4[(AM4.index(user_game_id) + 1) % len(AM4)]
            elif user_game_id in AM5:
                mortal_game_id = AM5[(AM5.index(user_game_id) + 1) % len(AM5)]
            elif user_game_id in AM6:
                mortal_game_id = AM6[(AM6.index(user_game_id) + 1) % len(AM6)]
            elif user_game_id in AM7:
                mortal_game_id = AM7[(AM7.index(user_game_id) + 1) % len(AM7)]
            else:
                mortal_game_id = AM8[(AM3.index(user_game_id) + 1) % len(AM8)]

            mortal_record = am_db.get_user_record_from_game_id(mortal_game_id).fetchone()
            if mortal_record is None:
                send_message(SEND_CONNECTION_FAILED, chat_id, self.name)
            else:
                self.mortal_chat_id = mortal_record[2]
                self.mortal_name = mortal_record[3]
                send_message(SUCCESSFUL_MORTAL_CONNECTION, chat_id, self.name)
                self.stage = self.chatwithbaby

    # Sends a text message to a user's angel.
    def chatwithparent(self, text, chat_id):
        if self.angel_chat_id != 0:
            print("Angel to Mortal:")
            send_message("From your Mortal:\n\n" + text, self.angel_chat_id, self.angel_name, sender_name=self.name)
        else:
            send_message(SEND_CONNECTION_FAILED, chat_id, self.name)

    # Sends a text message to a user's mortal.
    def chatwithbaby(self, text, chat_id):
        if self.mortal_chat_id != 0:
            print("Mortal to Angel:")
            send_message("From your Angel:\n\n" + text, self.mortal_chat_id, self.mortal_name, sender_name=self.name)
        else:
            send_message(SEND_CONNECTION_FAILED, chat_id, self.name)


# Searches existing user list for a registered user and stages the user
def find_existing_user_then_stage(text, chat_id, user_list):
    for registered_user in user_list:  # in the user list
        if chat_id == registered_user.id:  # if there is an existing user
            if text == MENU_KEY:
                registered_user.stage = registered_user.mainmenu
                registered_user.stage(text, chat_id)
            else:
                registered_user.stage(text, chat_id)
            break
        else:
            continue


# Initialises a User object, adds it to the global list and the user database
def setup_user_then_stage(text, chat_id, name, user_list):
        new_user = User(chat_id, name)  # create a new User object
        user_list.append(new_user)  # add new user to the global user list
        user_db.add_user(chat_id, name)  # add user profile to the db
        if text == MENU_KEY:
            new_user.stage = new_user.mainmenu
            new_user.stage(text, chat_id)
        else:
            new_user.stage(text, chat_id)


# Entry point of telegram bot script
def main():
    last_update_id = None # represents offset to be sent in get_updates
    while True:
        updates = get_updates(last_update_id)
        try:
            if len(updates["result"]) > 0:  # accesses the Array object in the JSON response
                for update in updates["result"]:  # iterates through the updates Array
                    if "message" in update and "text" in update["message"]:  # check for text message by user
                            text = update["message"]["text"]  # get message sent by user
                            chat_id = update["message"]["chat"]["id"]  # get user chat id
                            name = update["message"]["from"]["first_name"]  # get user name
                            if chat_id > 0:
                                # todo can use dictionary to improve complexity
                                if chat_id not in [user.id for user in users]:  # new user
                                    setup_user_then_stage(text, chat_id, name, users)
                                else:
                                    find_existing_user_then_stage(text, chat_id, users)
                last_update_id = get_last_update_id(updates) + 1
        except KeyError:
            print("I got a KeyError!")
            last_update_id = get_last_update_id(updates) + 1
            pass
        time.sleep(0.5)


if __name__ == '__main__':
    print("Initialised....")
    user_db.setup()
    print("User database set up done.")
    am_db.setup()
    print("AM database set up done.")
    print("Starting main()...")
    main()


