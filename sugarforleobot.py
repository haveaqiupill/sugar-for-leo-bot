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

#CHAT IDS

#CHAT IDS

#KERYIN
JINGYING = 508423467
PRISCILIA = 181854022
AQILAH = 130512569
YINGQI = 523934057
ZHENGYI = 151469558
JAMESLEE = 200746779
FELICIA = 812786550
SHAOCONG = 496252190
MINGHUI = 337212258
SHAE = 227790070
THERESA = 21522066
JUIN = 840529952
CAROLINE = 679916735
HUIKUN = 430632313
HUAIZHE = 277147326
JEFFREY = 109868357
HAOYU = 234003591
GLEN = 234003591
TJIONGHANN = 399175561
RACHELPOO = 420224700
YUCHEN = 682117474
JIANING = 757529011
SHRUTI = 338314088
HANWEI = 215406286
BLAKE = 559780833
BENJAMIN = 131897486
GALEN = 616268913
ANTHONY = 35152427
YAOYUAN = 791579048
IAN = 101418203
KANGLE = 263136369
JIAWEI = 147500398
YIFEI = 521885722
MINGZHE = 145596779
ZHENLIN = 47189409
JEDREK = 252149740
MICHELLE = 682105725
ADARSH = 259448748



#JINGYING
CALISTA = 818462650
KERYIN = 384865431
SHAHEEL = 99260110
ESTHER = 523411732
AMI = 972858978
GERALD = 231696047
LIONEL = 605977490
BRIAN = 209469386
NICHOLAS = 540825566
MARISA = 685572314
JAMESCHUA = 277020493
POR = 218893278
ZESS = 218893278
CHLOE = 141677603
COLIN = 806781370
LAURENCE = 677265725
JULIET = 264065267
RACHELONG = 254309071
YINGJIA = 23566998
DELWYN = 579685716
HAZEL = 728554302
JAY = 311062244
YIEWMIN = 638231981
DANIEL = 200078083
YUXIN = 262247353
JONATHON = 226517276
AMANDA = 136288892
DOREEN = 511807034
BRYSON = 42529268
GORDON = 167144451
YANKAI = 344514961
JEANETTE = 215766001
JINGWEN = 633397811
KENNEDY = 480200240
ZHIJIN = 126510110
RAYSON = 333832536
VIVIAN = 369647832
BELLA = 221093044
DAPHNE = 248976073


#USER ASSIGNMENT (KEYNAME, sugarparent, sugarbaby, likes, dislikes, remarks, unit, tolerance level, name)
keryin = User(KERYIN, JAMESCHUA, JINGYING,
              "bbt bbt bbt bbt bbt bbt food green tea seaweed",
              "no creatures please",
              "no living/dead/fake creatures, animals etc etc. please dont take my stuff out too :(", "#14-12F",
              "4",
              "Yeo Ker Yin")

jingying = User(JINGYING, KERYIN, BRYSON, "Bubble tea (liho brown sugar fresh milk w pearls), erm im ok w anything actually", "Idk but not too extreme pranks please D:",
                "Please dont touch my things in my room (expensive stuffz!!) And no hair removal cream!!",
                "#14-12A",
                "3",
                "Qiu Jing Ying")

shaheel = User(SHAHEEL, JEDREK, JAMESCHUA,
               "I like snacks yEy",
               "I dislike slimy things...",
               "Please do not touch my captain America popart and my decorations that are hanging on my wall, "
               "I really put a lot of effort into making them and I dont want to see them missing/destroyed",
               "#13-18",
               "5",
               "Shaheel")

yingqi = User(YINGQI, CHLOE, DANIEL,
              "nice stuff outside my door thx, easy to clean up pranks thx :))", "up to u ;) don wreck my room",
              "no flour, no red beans/green beans/ granular stuff",
              "#14-12C",
              "3",
              "Tay Ying Qi")

priscilia = User(PRISCILIA, MICHELLE, MINGZHE, "i like cute stationery hehe, and i have a sweet tooth so, good food :-)",
                 "wah i dont like bananas, durians AND I CANNOT TAKE SPICY FOOD, no mala for me",
                 "please dont prank anything that requires much clean up or ruin my stuff haha (no dirty stuff on my bed!!) "
                 "and i seriously hate rodents and lizards so please dont put any fakes in my vicinity D:",
                 "#12-14",
                 "4",
                 "Priscilia Chow")

jameslee = User(JAMESLEE, GERALD, ZHENGYI, "A new friend! (optional teh peng)", "nothing in particular",
                "dont enter my room and nothing hard to clean up thx :D", "#13-16",
                "2",
                "James Lee")

jameschua = User(JAMESCHUA, SHAHEEL, KERYIN, "...cooking supplies? Tools? Sauces?",
                 "Oh no... I guess rlly dont like wasabi",
                 "Please nothing that takes more than an hr to reset my room",
                 "#14-01C",
                 "4",
                 "James Chua")

laurence = User(LAURENCE, JAMESLEE, COLIN,
                "Anything that is useful like snacks and stationary",
                "Anything that is useless, too wasteful to throw away and takes up space like photo frame, soft toys etc",
                "Do not enter my room. Do not prank things which are difficult to clean up (like spreading slime on the door). Ive very little bandwidth this sem and may have a short temper.",
                "#13-04",
                "2",
                "Laurence Lu")

colin = User(COLIN, LAURENCE, JEFFREY,
             "Floppy Discs... Orca themed stuff...",
             "Anything messy, be it liquid or powder",
             "Do not dig through my belongings",
             "#13-11C",
             "2",
             "Colin Ng")

jeffrey = User(JEFFREY, COLIN, YUCHEN, "Real life Pokemon", "Celery", "No smelly things",
               "#14-01B",
               "2",
               "Jeffrey Ng")

yuchen = User(YUCHEN, JEFFREY, DELWYN, "Things that help with cable management", "Scratching noises", "Dont destroy anything",
              "#13-24",
              "2",
              "Wang Yuchen")

delwyn = User(DELWYN, YUCHEN, KENNEDY, "Fruits (Preferably easy to eat)", "High sugar stuff", "Preferably nothing with too much clean up, and please dont remove anything from my room",
              "#14-08",
              "2",
              "Delwyn")

kennedy = User(KENNEDY, DELWYN, DOREEN, "Impress me (-:", "Nothing in particular!", "No no to pranks that make me have to clean up the entire room pls, minor ones r fine or live pests or rodents",
               "#14-09",
               "3",
               "Kennedy Wong")

doreen = User(DOREEN, KENNEDY, JINGWEN, "Coke, junk food, meat, food basically cos Im always hungry", "lizards and similar gross stuff",
              "Please dont make me spend a lot of time cleaning up cos I dont have time for that kinda thing",
              "#12-01E",
              "3",
              "Doreen Poh")

jingwen = User(JINGWEN, DOREEN, YUXIN, "BUBBLE TEA IS LIFE :)", "I cannot with jumpscares", "Pls dont put a lizard or gecko in my room",
               "#14-16",
               "3",
               "Jing Wen")

yuxin = User(YUXIN, JINGWEN, YIFEI,
             "ICEBEAR, help in decorating my room AESTHETICALLY pls ",
             "cucumber", "anything that will take a lot of time to clean:-( #respectandconsent #safecampus",
             "#12-11E",
             "3",
             "Yip Yuxin")

yifei = User(YIFEI, YUXIN, AMANDA, "Soft toy, stationery and food.",
             "Gory things, insects and slime", "Please do not vandalise anything or create mess that is difficult to clean up:)",
             "#12-12A",
             "3",
             "Xiang Yifei")

amanda = User(AMANDA, YIFEI, ZESS, "0% sugar drinks LOL.......",
              "Money",
              "Pls dont do anything that requires me to have to spend more than 10 min cleaning up.....",
              "#14-27",
              "3",
              "Amanda Xue")

zess = User(ZESS, AMANDA, HUIKUN, "anything ahhaha",
            "bad pranks",
            "bad ppranks",
            "#12-10",
            "2",
            "Zess Tan")

huikun = User(HUIKUN, ZESS, CHLOE,
                   "Snacks like chips/instant noodles, cards/handmade stuff, oolong milk tea (30% sugar HAHAHA). And hit me up with some bad jokes/puns I live for them",
                   "Asymmetrical stuff, having my unglams discovered",
               "Please dont move anything out of my room thank you!! :)",
               "#12-03",
               "2",
               "Yeo Hui Kun")

chloe = User(CHLOE, HUIKUN, YINGQI,
             "cute and pretty stationery, snacks, accessories etc",
             "ugly stationary",
             "dont spoil my things",
             "#12-12D",
             "2",
             "Chloe Seah")

daniel = User(DANIEL, YINGQI, JIAWEI,
              "Pokemon related stuff, plushies",
              "Any form of hentai",
              "DO NOT MOVE MY BELONGINGS, can put stuff in my room but please dont move my stuff",
              "#13-10",
              "3",
              "Daniel Phoon")

jiawei = User(JIAWEI, DANIEL, BENJAMIN, "starbucks!", "vegetables", "Please do not touch my bed",
              "#13-01E",
              "3",
              "Ho Jia Wei")

benjamin = User(BENJAMIN, JIAWEI, KANGLE, "Anything", "Slimes", "Dont dirty my bed/clothes",
                "#13-01B",
                "3",
                "Benjamin Chua")

kangle = User(KANGLE, BENJAMIN, ZHIJIN, "Milk Tea, Tehbing or any kind of food!",
              "Stickers", "Do what you want but dont mess up the room too much HAHAHA",
              "#13-15",
              "3",
              "Lim Kang Le")

zhijin = User(ZHIJIN, KANGLE, ANTHONY,
              "Anything useful",
              "I dont know",
              "Dont misplace my personal belongings",
              "#13-17",
              "3",
              "Lou Zhi Jin")

anthony = User(ANTHONY, ZHIJIN, HANWEI,
               "Sugar baby, please give me a Rolex or BMW. Either will be fine",
               "Please dont put girls around me. Im scared of them...",
               "My limit is anything that requires more than 10 mins to clean up. Thanks.",
               "#14-04",
               "3",
               "Anthony Poon")

hanwei = User(HANWEI, ANTHONY, HAOYU, "Surprise Me :)", "Supper, Adityas Jokes, FOMO",
              "Stuff to not touch: Router, Computers, Computer Chargers, Photos, Vacuum Cleaner",
              "#14-01F",
              "3",
              "Koh Han Wei")

haoyu = User(HAOYU, HANWEI, SHRUTI, "Anything is fine. Pls dun spend too much on the gift :))",
             "Pls dun shift my room out again TT Im no longer hse head help",
             "Pls dun move my room layout or move my room out plox pls prease",
             "#13-13",
             "2",
             "Zhao Haoyu")

shruti = User(SHRUTI, HAOYU, GORDON, "I like rocks of different shapes and materials and minerals",
              "I dont like talking dolls, and i dont want chocolates that "
              "have NUTS because it ruinnnssss the texture of the choco",
              "Pls do not trash my room or move anyway from its position. Also pls keep my windows closed i cant stand insects",
              "#12-12F but honestly you can also prank at #13-11B",
              "3",
              "Shruti")
gordon = User(GORDON, SHRUTI, GERALD,
              "Koi green tea macchiato and LOL (lots of laughter/love whichever ure feeling)",
              "amins, mcd jk HAHAHA um insects i guess just not alive",
              "no flour/glitter and my monitor and laptop and shoes they are new :)",
              "#13-20",
              "3",
              "Gordon Ng")

gerald = User(GERALD, GORDON, JAMESLEE, "Churros, Donuts, Cookies, Chocolates",
              "Broccoli", "Please dont move my furniture out of my room :(",
              "#13-03",
              "3",
              "Gerald Ng")

zhengyi = User(ZHENGYI, JAMESLEE, GALEN,
               "Hard Liquor, Nintendo Switch, New Mahjong Set",
               "dolls",
               "dont touch my desktop or pc or monitor setup thanks",
               "#13-11D",
               "3",
               "Wong Zhengyi")

galen = User(GALEN, ZHENGYI, JAY, "Gummy sweets! Sour power or yupi :)",
             "No glitter, slime or raw fish pls",
             "Pls dont touch my valuables or pillow TY",
             "#13-08",
             "3",
             "Galen Cheung")

jay = User(JAY, GALEN, YIEWMIN, "snacks",
           "sneks",
           "Dont make a big mess. I have little time to clean.",
           "#13-12A",
           "2",
           "Jay")

yiewmin = User(YIEWMIN, JAY, YANKAI,
               "Bubble tea 50% sugar level pls, packet drinks, canned drinks, snacks",
               "Beans, bugs(but seriously dont put real bugs fake ones are bad enough), peas, cleaning up messes",
               "Nothing that is difficult to remove pls ie FLOUR "
               "(I realised this is a very bad idea last year dont do it, it seems harmless but "
               "it actually isnt once it blows into the room, even through under the door), RAW FISH (or raw anything this is just damn disgusting and the smell is really a no-go). Im OK with things that are troublesome to clean up but pls nothing that is impossible to remove apart from time"
               " (ie really pungent smells or flour). Only these 2 come to mind but Im sure youll think of a lot of other stuff to do to me,"
               "please have fun and I cant wait to see how creative youll be. CYA SOON SUGAR PARENT!!!!",
               "#13-01D",
               "3",
               "Yiew Min")

yankai = User(YANKAI, YIEWMIN, IAN, "Food and boardgames", "Work. And insects.",
              "No room movement please", "#13-11B",
              "3",
              "Choo Yan Kai")

ian = User(IAN, YANKAI, HUAIZHE, "Meat, free condoms", "I hate sweat",
           "Please try not to interrupt my sleep. I have pretty bad insomnia as is, "
           "so additional interruptions will make it harder for me to ever sleep.", "#14-01E",
           "3",
           "Ian Chan")

huaizhe = User(HUAIZHE, IAN, BLAKE, "anything possible",
               "glue",
               "Dont dirty my bed please", "#13-11E",
               "2",
               "Yeo Huai Zhe")

blake = User(BLAKE, HUAIZHE, JONATHON,
             "Nintendo switch accessories, koi, salted egg yolk flavoured stuff, gummies, milk (or milk flavoured stuff)",
             "Horror / gore stuff, oreo / coke / rootbeer(legit)",
             "Dont dirty my plushies!!", "#13-11F",
             "3",
             "Blake Wang")

jonathon = User(JONATHON, BLAKE, GLEN, "food", "small pranks", "Insects / unhygienic stuff", "#14-05",
                "3",
                "Jonathon")

glen = User(GLEN, JONATHON, TJIONGHANN, "Soft toys, decorations, food", "Anything to do with bananas: (or things that smell bad", "Just do not spoil anything hahaha",
            "# 13-09",
            "2",
            "Glen Mun")

tjionghann = User(TJIONGHANN, GLEN, HAZEL, "food", "mess", "not too much clean up",
                  "# 14-15",
                  "2",
                  "Lim Tjiong Hann")

hazel = User(HAZEL, TJIONGHANN, JIANING, "dark choco/food/bbt", "messy stuff",
             "dont touch my music stuff (bc its ex :< )",
             "#14-12B",
             "2",
             "Hazel Pak")

jianing = User(JIANING, HAZEL, YINGJIA,
               "Plushies / practical stuff to use in school",
               "anything related to horror films", "so long my room is safe :)",
               "#14-19",
               "2",
               "Jianing")

yingjia = User(YINGJIA, JIANING, JULIET,
               "Project Acai (not an acai affair dat shit no gud), Koi (hazelnut milk tea 30% with pearls tq), cash works too, chalk my door nice nice if youre artistic HAHAHAH, idm some room deco (not weird/gross ones if youre thinking of a prank) e.g. plants and what not",
               "Please dont make it hard for me to get out of bed / "
               "my room I have 8:30ams every day and I dont even leave enough leeway to eat a proper breakfast.Also anything that "
               "involves a lot of clean up (a bit is fine) or dirties my room significantly.",
               "Insects, things that fly, gross or bad smelling stuff", "#12-06",
               "2",
               "Zhang Yingjia")

juliet = User(JULIET, YINGJIA, RACHELPOO, "KOI and pls be my friend", "Useless Freebees and bugs",
              "Dont dirty until very hard to wash pls I like cleaniless", "#12-22",
              "2",
              "Juliet Teoh")

rachelpoo = User(RACHELPOO, JULIET, CAROLINE,
                 "decorative stuff, cute stuff, food, bbt, useful essentials",
                 "vegetables, sharp objects, useless stuff, sour food",
                 "dont spoil, steal or hide my stuff (beyond finding)", "#14-23",
                 "2",
                 "Rachel Poo")

caroline = User(CAROLINE, RACHELPOO, JEANETTE, "nice things",
                "things that will make me sad",
                "anything that requires cleaning up", "#14-22",
                "2",
                "Caroline Leung")

jeanette = User(JEANETTE, CAROLINE, RACHELONG, "can I have a kitten", "Institutionalisation, streamlining, and patriarchy",
                "There is a bunch of tech stuff in my room sometimes please PLease do not destroy it bc pls preserve my job I am old. Please also dont plant one of my exes in my room.",
                "#14-17",
                "3",
                "Jeanette")

rachelong = User(RACHELONG, JEANETTE, NICHOLAS, "I would like to anything useful or soft toys hehehe",
                 "I dont like insects please dont bring any insects if not ill cry spare a child",
                 "I hope the pranks wont be to hard to clean up and i dont want my room anywhere else hehehe thank you :""))))",
                 "#12-09",
                 "2",
                 "Rachel Ong")

nicholas = User(NICHOLAS, RACHELONG, RAYSON,
                "gifts and harmless pranks", "food mess",
                "nothing that requires clean up haha",
                "#14-01A",
                "2",
                "Nicholas Nge")

rayson = User(RAYSON, NICHOLAS, ADARSH, "bbt",
              "I dislike snacks",
              "no live or recently deceased animals pls, also no glitter or anything like that pls,"
              "and pls leave the expensive personal stuff in da room pls",
              "#13-22",
              "3",
              "Rayson Lau")

adarsh = User(ADARSH, RAYSON, VIVIAN, "Money. Real money stop giving me chocolate",
              "The entire lounge in my room",
              "I sometimes leave my door unlocked. "
              "Please do not move my furniture/ move furniture into my room. "
              "Thanks. That was fun in Year 1 Im in y4 now old alr.",
              "#13-12F",
              "4",
              "Adarsh")

vivian = User(VIVIAN, ADARSH, YAOYUAN,
              "A cute companion, tied up, and wrapped in newspapers, stored in a fridge.",
              "Pen pineapple apple pen",
              "1) pls dont judge the mess of my room. My hair drops like a shedding dog so... "
              "2) i have sensitive skin and i dont like to inhale small particles AKA NO GLITTER ON FAN PLS "
              "3) Any mess created shld not take more than 10 hours+++ to clean up plz.",
              "#12-25",
              "4",
              "Vivian")

yaoyuan = User(YAOYUAN, VIVIAN, AQILAH,
               "love", "human snake",
               "horror stuff ( ghost, zombie, Annabelle, clown...)",
               "#12-01D",
               "3",
               "Yao Yuan")

aqilah = User(AQILAH, YAOYUAN, BELLA,
              "sweets. and chocolates:)",
              "bubble tea. green tea. any kind of tea. pls no gongcha/liho/MATCHA",
              "dont touch my bear and any nursing stuffs thanks:)",
              "#12-20",
              "3",
              "Aqilah")
bella = User(BELLA, AQILAH, MICHELLE,
             "Anything unexpected/fun",
             "My room to be messed up >< I am lazy af. Also I dislike Shaheel",
             "Please dont do anything irreversible to my stuff >< "
             "Also take note: the random strips of gel thingys "
             "pasted on my walls/floor are ant baits, please dont touch them theyre poisonous",
             "#12-11D",
             "5",
             "Bella Zhang")

michelle = User(MICHELLE, BELLA, PRISCILIA,
                "food/drinks, anything small/cute actually",
                "had my room furniture turned upside down last year "
                "(just to make sure that the prank doesnt get repeated this year lmao), "
                "i have 8.30 am on tues and fri and i will be inconvenienced if sth funny happens then",
                "be nice to the bear on my bed, no horror stuff pls i have the heart of an old man, "
                "dont remove furniture from my room, nothing alive/used to be alive, "
                "nothing too hard to clean up (eg glitter, oil, FISH, egg) :-)", "#12-18",
                "4", "Michelle Lee")


mingzhe = User(MINGZHE, PRISCILIA, BRIAN,
               "Thoughtful gifts! (handwritten notes, DIY stuff cus I cant do arts for nuts)",
               "Slanderous stuff I guess", "Stuff that cant be wiped off/destroys my electronics",
               "#13-07",
               "5",
               "Wang Ming Zhe")

brian = User(BRIAN, MINGZHE, JEDREK,
             "Japanese snacks! Or anything really!",
             "MONEY. Jkjk I dont really have any major dislikes, "
             "just the standard stuff like cockroaches I guess?",
             "Nothing that would leave permanent damage in my room / to my stuff please!",
             "#14-03",
             "4",
             "Brian")

jedrek = User(JEDREK, BRIAN, SHAHEEL,
              "I like to have a CAP 5.0", "humans",
              "Please dont put anything that will attract insects as my room is near the rubbish chute",
              "#14-10",
              "5",
              "Jedrek Loo")



bryson = User(BRYSON, JINGYING, ZHENLIN, "Teh bing or Teh O bing pls", "Not falling for this trick question",
              "Please dont destroy my personal stuff :) I dont really care if you rekt the college property",
              "#14-06",
              "3",
              "Bryson Tan")

zhenlin = User(ZHENLIN, BRYSON, DAPHNE,
               "food", "tomatoes",
               "pls dont trash my room",
               "#14-01D",
               "5",
               "Zhen Lin")

daphne = User(DAPHNE, ZHENLIN, ZHENGYI, "Anything with yakult, plants (jokes), food, cattos, fruits",
              "im terrified of clean rooms (so pls dont clean my room for me aaahh), "
              "i hate mayo, im sked of the nun (valak) and plastic disposables (but rlly dont waste ok)",
              "Please dont do anything to my plant i love it his name is bitcoin. "
              "Wreck my room but not me yay thanks :) "
              "Also dont do anything that will affect my suitemates i cant lose my only friends thanks.",
              "#12-21",
              "5",
              "Daphne Lim")

calista = User(CALISTA, JUIN, FELICIA,
               "notes, food and wholesome stuff",
               "If u want to prank me also can but no messy stuff pls!!",
               "messy hard to clean up stuff!!", "#14-12D",
               "1",
               "Calista Loh")

felicia = User(FELICIA, CALISTA, ESTHER, "pretty stationary and notebooks :)",
               "8am anything, paiseh, dairy products",
               "no insects/creatures in my room please! and if my door is "
               "locked just put like a post it etc. to remind me to unlock if needed :)", "#12-17",
               "1",
               "Felicia")

esther = User(ESTHER, FELICIA, SHAOCONG,
              "food food and more food pls :> I love milo and ribena and chips!!",
              "pRANKS!! (ive got no time to clean up so pls let me off :) tyvvm)",
              "idw to clean up any mess HHAHA TENKYOU", "#12-20",
              "1",
              "Esther Tay")

shaocong = User(SHAOCONG, ESTHER, AMI, "A new friend:) Jk jk chocolate/handwritten cards are nice",
                "-", "Please dont enter my room :) hahaha",
                "#13-19",
                "1",
                "Shao Cong")

ami = User(AMI, SHAOCONG, MINGHUI,
           "chocolate and snacks", "smt spicy",
           "anything happens inside my room...",
           "#12-12E",
           "1",
           "Ami")

minghui = User(MINGHUI, AMI, LIONEL,
               "fun!", "too much mess haha",
               "please dont wear shoes into my room",
               "#12-11A",
               "1",
               "Ming Hui")

lionel = User(LIONEL, MINGHUI, SHAE, "anything", "nil", "Dont move/hide my stuff",
              "#13-25",
              "1",
              "Lionel Lee")

shae = User(SHAE, LIONEL, MARISA, "Matcha stuff, anything with a sense of humour, BTS LOL",
            "???? Pls be a nice and mild sugar parent I have a weak heart "
            "and not a lot of cleaning materials :(",
            "SERIOUS AH PLS NO SLIME THIS YEAR OR ANYTHING NASTY LIKE THAT HAHAHA WAH NO GO",
            "#14-26",
            "1",
            "Shae")

marisa = User(MARISA, SHAE, THERESA,
              "healthy snacks, gym towels, cool stickers, cool iron-on patches, "
              "cool keychains, anything related to coldplay, anything retro/70s "
              "80s themed, anything related to art and music!",
              "nothing too girly, sweets or chocolates (i love dark chocolate only hehe), "
              "anything unhealthy", "-", "#12-11F",
              "1",
              "Marisa")

theresa = User(THERESA, MARISA, POR,
               "Anything but lizards",
               "LIZARDS? What do u mean can be used against me",
               "Lizards", "#14-21",
               "1",
               "Theresa")

por = User(POR, THERESA, JUIN,
               "Memorable/Personalized stuff, handicraft, stationary "
               "like journey books or planner (I usually collect for my collection but not for use)",
               "scary pictures", "Any of my stuffs being moved; this would make me anxious", "#12-19",
               "1",
               "Seak Por")

juin = User(JUIN, POR, CALISTA, "anything", "things other than anything",
            "Dont disturb me sleeping :-)", "#13-11A",
            "1",
            "Juin Hwaye")


#KEY-VALUE PAIR
ASSIGN = {KERYIN:keryin,
JINGYING:jingying, SHAHEEL:shaheel, YINGQI:yingqi, PRISCILIA:priscilia, JAMESLEE:jameslee, JAMESCHUA:jameschua,
BLAKE:blake, AQILAH:aqilah, ZHENGYI:zhengyi, FELICIA:felicia, SHAOCONG:shaocong, MINGHUI:minghui, SHAE:shae,
THERESA:theresa, JUIN:juin, CAROLINE:caroline, HUIKUN:huikun, HUAIZHE:huaizhe, JEFFREY:jeffrey, HAOYU:haoyu, GLEN:glen,
TJIONGHANN:tjionghann, RACHELPOO:rachelpoo, YUCHEN:yuchen, JIANING:jianing, SHRUTI:shruti, HANWEI:hanwei, BENJAMIN:benjamin,
GALEN:galen, ANTHONY:anthony, YAOYUAN:yaoyuan, IAN:ian, KANGLE:kangle, JIAWEI:jiawei, YIFEI:yifei, MINGZHE:mingzhe,
ZHENLIN:zhenlin, JEDREK:jedrek, MICHELLE:michelle, ADARSH:adarsh, CALISTA:calista, ESTHER:esther, AMI:ami, GERALD:gerald,
LIONEL:lionel, BRIAN:brian, NICHOLAS:nicholas, MARISA:marisa, POR:por, ZESS:zess, CHLOE:chloe, COLIN:colin, LAURENCE:laurence,
JULIET:juliet, RACHELONG:rachelong, YINGJIA:yingjia, DELWYN:delwyn, HAZEL:hazel, JAY:jay, YIEWMIN:yiewmin, DANIEL:daniel,
YUXIN:yuxin, JONATHON:jonathon, AMANDA:amanda, DOREEN:doreen, BRYSON:bryson, GORDON:gordon, YANKAI:yankai, JEANETTE:jeanette,
JINGWEN:jingwen, KENNEDY:kennedy, ZHIJIN:zhijin, RAYSON:rayson, VIVIAN:vivian, BELLA:bella, DAPHNE:daphne}



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

        # appends message sent by bot itself - the very first message: start message
        INFOSTORE[user.id]["BotMessageID"].append(msgsent['message_id'])

        return AFTER_CONSENT


def send_to_parent(bot, update):
    query = update.callback_query
    user = query.from_user
    logger.info("User {} has just chose to talk to the sugar parent".format(user.username if user.username else user.first_name))

    sendtext = "<b>What do you want to tell your sugar parent?</b>" + "\n\nType and send me your message below:"

    bot.send_message(chat_id=user.id, text=sendtext, parse_mode=ParseMode.HTML)

    #INFOSTORE[user.id]["BotMessageID"] = update.message.chat_id

    return FORWARD_BABY

def send_to_baby(bot, update):
    query = update.callback_query
    user = query.from_user
    logger.info("User {} has just chose to talk to the sugar baby".format(user.username if user.username else user.first_name))

    babyID = ASSIGN.get(user.id).get_babyid()
    baby = ASSIGN.get(babyID)

    sendtext = "<b>Your sugar baby is</b> " + baby.get_name() + ", staying in " + baby.get_unit() + "\n\n"
    sendtext += "<b>Tolerance level:</b> " + baby.get_tolerance_level() + "\n\n"
    sendtext += HEART + "<b>Here are the likes of your sugar baby:</b>" + HEART + "\n" + baby.get_likes()  + "\n\n"
    sendtext += CROSS + "<b>Here are the dislikes of your sugar baby:</b>" + CROSS + "\n"  + baby.get_dislikes()  + "\n\n"
    sendtext += "<b>Please take these remarks seriously!!:</b> \n" + baby.get_remarks() + "\n\n"
    sendtext += "<b>What do you want to tell your sugar baby?</b>" + "\n\nType and send me your message below:"

    bot.send_message(chat_id=user.id, text=sendtext, parse_mode=ParseMode.HTML)

    #INFOSTORE[user.id]["BotMessageID"] = update.message.chat_id

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

    logger.info("Message of %s: %s", user.first_name, changedMessage)

    sendtext = "&quot " + INFOSTORE[user.id] + " &quot" +  "\n\n"
    sendtext += 'Thank you! Your message has been forwarded. \n\n<b>Press /start to send again!</b>'

    messagefromparent = '<b>Hello! Your sugar parent wants to say:</b>\n\n' + INFOSTORE[user.id]
    messagetoadmin = user.first_name + " of username " + (user.username if user.username else user.first_name) + " sent this to the sugar baby: \n\n" + INFOSTORE[user.id]

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

    #bot.delete_message(chat_id=update.message.chat_id, message_id=INFOSTORE[user.id]["BotMessageID"])

    logger.info("Message of %s: %s", user.first_name, changedMessage)

    sendtext = "&quot " + INFOSTORE[user.id] + " &quot" + "\n\n"
    sendtext += 'Thank you! Your message has been forwarded. \n\n<b>Press /start to send again!</b>'

    messagefrombaby = '<b>Hello! Your sugar baby wants to say:</b>\n\n' + INFOSTORE[user.id]
    messagetoadmin = user.first_name + " of username " + (user.username if user.username else user.first_name) + " sent this to the sugar parent: \n\n" + INFOSTORE[user.id]

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









