import logging
from datetime import datetime
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)
from firebase import Firebase

config = {
  "apiKey": "AIzaSyDVqjbQENcQObWM_6JRJQV2ykX9U3UHQrI",
  "authDomain": "timetrackerbot-f0ceb.firebaseapp.com",
  "databaseURL": "https://timetrackerbot-f0ceb-default-rtdb.firebaseio.com/",
  "storageBucket": "timetrackerbot-f0ceb.appspot.com"
}

firebase = Firebase(config)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

reply_keyboard1 = [
    ['Unpause'],
]

reply_keyboard2 = [
    ['Pause', 'Unpause'],
    ['Pause Schelude'],
]

markup1 = ReplyKeyboardMarkup(reply_keyboard1, one_time_keyboard=True)
markup2 = ReplyKeyboardMarkup(reply_keyboard2, one_time_keyboard=True)
userKey = 0
PauseKey = 'none'
PauseStart = 'none'
PauseState = 'none'
PauseAllKey = 'none'


def start(update: Update, context: CallbackContext) -> int:
    global PauseKey, PauseStart, PauseState, PauseAllKey, userKey
    timenow = datetime.now()
    auth = firebase.auth()
    userx = auth.sign_in_with_email_and_password('drux@mail.com', '12345678')
    db = firebase.database()
    chat_user_client = update.message.from_user.username
    all_users = db.child("users").get()
    user_status = "none"
    # data = {"name": chat_user_client, "chat_id": update.message.chat_id}
    # userKey = db.child("users").push(data)
    # text_back = "You was logged in, Welcome back "

    # for user in all_users.each():
    #     if user.val()["chat_id"]:
    #         if user.val()["chat_id"] == update.message.chat_id:
    #             user_status = "exist"
    #             userKey = user.key()

    # checker = db.child("users").child("ChatID").get()
    # for chatid in checker.each():
    #     if chatid ==

    for user in all_users.each():
        user_chat_id = db.child("users").child(user.key()).get()
        if user_chat_id.val()["chat_id"] == update.message.chat_id:
            user_status = "exist"

    if user_status == "none":
        data = {"name": chat_user_client, "chat_id": update.message.chat_id}
        userKey = db.child("users").push(data)
        # db.child("users").child("ChatID").push(update.message.chat_id)
        text_back = "Account was created, Welcome "
    else:
        text_back = "You was logged in, Welcome back "


    update.message.reply_text(
    f'{text_back}{update.message.from_user.username}',
    reply_markup=markup2
    )


    return CHOOSING


def regular_choice(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    context.user_data['choice'] = text
    update.message.reply_text(f'Your {text.lower()}? Yes, I would love to hear about that!')

    return TYPING_REPLY


def custom_choice(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        'Alright, please send me the category first, ' 'for example "Most impressive skill"'
    )

    return TYPING_CHOICE

def done(update: Update, context: CallbackContext) -> int:
    userKey = 0
    PauseKey = 'none'
    PauseStart = 'none'
    PauseState = 'none'
    PauseAllKey = 'none'
    return ConversationHandler.END

def pause_model(update: Update, context: CallbackContext) -> int:
    global PauseKey,PauseStart,PauseState,PauseAllKey
    auth = firebase.auth()
    user = auth.sign_in_with_email_and_password('drux@mail.com', '12345678')
    db = firebase.database()
    timenow = datetime.now()
    dt_string = timenow.strftime("%d/%m/%Y %H:%M:%S")
    dt_only = timenow.strftime("%d/%m/%Y")
    dt_time = timenow.strftime("%H:%M:%S")
    FMT = '%H:%M:%S'

    update.message.reply_text(
        f'Pause start at {dt_string}',
        reply_markup=markup1
    )
    chat_user_client = update.message.from_user.username
    data1 = {"Date": dt_only,"PauseStart": dt_time,"PauseEnd": "In Progress","PauseTime": "In Progress" }
    data2 = {"Date": dt_only, "Name": chat_user_client, "PauseStart": dt_time, "PauseEnd": "In Progress",
            "PauseTime": "In Progress"}
    PauseKey = db.child("users").child(userKey).child("PauseSchelude").push(data1)
    PauseKey = PauseKey["name"]
    PauseAllKey = db.child("AllPauses").push(data2)
    PauseAllKey = PauseAllKey["name"]
    return CHOOSING

def unpause_model(update: Update, context: CallbackContext) -> int:
    global PauseKey,PauseStart,PauseState,PauseAllKey
    auth = firebase.auth()
    user = auth.sign_in_with_email_and_password('drux@mail.com', '12345678')
    db = firebase.database()
    text = update.message.text
    context.user_data['choice'] = text
    timenow = datetime.now()
    dt_string = timenow.strftime("%d/%m/%Y %H:%M:%S")
    dt_only = timenow.strftime("%d/%m/%Y")
    dt_time = timenow.strftime("%H:%M:%S")
    FMT = '%H:%M:%S'
    dt_time_start = db.child("users").child(userKey).child("PauseSchelude").child(PauseKey).get()
    PauseStart = dt_time_start.val()["PauseStart"]
    PauseTime = datetime.strptime(dt_time, FMT) - datetime.strptime(PauseStart, FMT)
    data2 = {"PauseEnd": dt_time, "PauseTime":str(PauseTime) }
    db.child("users").child(userKey).child("PauseSchelude").child(PauseKey).update(data2)
    db.child("AllPauses").child(PauseAllKey).update(data2)
    update.message.reply_text(
        f'Pause end at {dt_string}',
        reply_markup=markup2
    )
    return CHOOSING
def PauseShelude_User(update: Update, context: CallbackContext) -> int:
    global PauseKey, PauseStart, PauseState, PauseAllKey
    auth = firebase.auth()
    user = auth.sign_in_with_email_and_password('drux@mail.com', '12345678')
    db = firebase.database()
    Schelude = db.child("users").child(userKey).child("PauseSchelude").get().val()
    timenow = datetime.now()
    dt_only = timenow.strftime("%d/%m/%Y")
    all_users = db.child("users").child(userKey).child("PauseSchelude").get()
    for user in all_users.each():
        if user.val()["Date"] == dt_only:
            update.message.reply_text(
                f'Data:{user.val()["Date"]}|Start:{user.val()["PauseStart"]}|End:{user.val()["PauseEnd"]}|Time:{user.val()["PauseTime"]}',
                reply_markup=markup2
            )
    return CHOOSING
def Admin_Panel(update: Update, context: CallbackContext) -> int:
    global PauseKey, PauseStart, PauseState, PauseAllKey
    auth = firebase.auth()
    user = auth.sign_in_with_email_and_password('drux@mail.com', '12345678')
    db = firebase.database()
    timenow = datetime.now()
    dt_only = timenow.strftime("%d/%m/%Y")
    update.message.reply_text(f'Retrieving Pauses Table for {dt_only} \n')
    all_users = db.child("AllPauses").get()
    for user in all_users.each():
        if user.val()["Date"] == dt_only:
            update.message.reply_text(
                f'{user.val()["Name"]}|Start:{user.val()["PauseStart"]}|End:{user.val()["PauseEnd"]}|Time:{user.val()["PauseTime"]}',
                reply_markup=markup2
            )
    return CHOOSING
def credits(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        f'Bot was made by DREDD | Insta: @dreeeeeedd',
        reply_markup=markup2
    )
    return CHOOSING

def main() -> None:
    auth = firebase.auth()
    user = auth.sign_in_with_email_and_password('drux@mail.com', '12345678')
    updater = Updater("1632932546:AAE-BXmsV11pGWQUjdPrB1vcMyKmr5yWMaw")

    dispatcher = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [
                MessageHandler(
                    Filters.regex('^(Pause)$'), pause_model
                ),
                MessageHandler(Filters.regex('^(Unpause)$'), unpause_model),
                MessageHandler(Filters.regex('^(Pause Schelude)$'), PauseShelude_User),
                MessageHandler(Filters.regex('^(day_table)$'), Admin_Panel),
                MessageHandler(Filters.regex('^(credits)$'), credits),
            ],

        },
        fallbacks=[MessageHandler(Filters.regex('^Done$'),done )],
    )

    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()