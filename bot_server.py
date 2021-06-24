import logging
from datetime import datetime
import datetime as dt
from datetime import timedelta
from pytz import timezone

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

reply_keyboard_admin = [
    ['day_table', 'day_times'],
    ['credits','user_panel'],
]

markup1 = ReplyKeyboardMarkup(reply_keyboard1, one_time_keyboard=True)
markup2 = ReplyKeyboardMarkup(reply_keyboard2, one_time_keyboard=True)
markup_admin = ReplyKeyboardMarkup(reply_keyboard_admin, one_time_keyboard=True)
all_uid = []
all_userx = []


def start(update: Update, context: CallbackContext) -> int:

    update.message.reply_text(
        f'You was logged in , welcome {update.message.from_user.username}',
        reply_markup=markup2
    )
    print(f'New user {update.message.from_user.username} in system')
    all_uid.append(update.message.chat_id)
    all_userx.append(update.message.from_user.username)
    return CHOOSING

def done(update: Update, context: CallbackContext) -> int:
    return ConversationHandler.END

def pause_model(update: Update, context: CallbackContext) -> int:
    auth = firebase.auth()
    user = auth.sign_in_with_email_and_password('drux@mail.com', '12345678')
    db = firebase.database()
    timenow = datetime.now(timezone("Europe/Chisinau"))
    dt_string = timenow.strftime("%d/%m/%Y %H:%M:%S")
    dt_only = timenow.strftime("%d/%m/%Y")
    dt_time = timenow.strftime("%H:%M:%S")
    if update.message.from_user.username is None:
        name = "Unnammed"
    else:
        name = update.message.from_user.username
    data = {"Date": dt_only, "Name": name, "PauseStart": dt_time, "PauseEnd": "In Progress",
             "PauseTime": "In Progress", "chatid":update.message.chat_id }
    db.child("AllPauses").push(data)
    update.message.reply_text(
        f'Pause start at {dt_string}',
        reply_markup=markup1
    )

    return CHOOSING

def unpause_model(update: Update, context: CallbackContext) -> int:
    auth = firebase.auth()
    user = auth.sign_in_with_email_and_password('drux@mail.com', '12345678')
    db = firebase.database()
    text = update.message.text
    context.user_data['choice'] = text
    timenow = datetime.now(timezone("Europe/Chisinau"))
    dt_string = timenow.strftime("%d/%m/%Y %H:%M:%S")
    dt_only = timenow.strftime("%d/%m/%Y")
    dt_time = timenow.strftime("%H:%M:%S")
    FMT = '%H:%M:%S'
    pause = "none"
    all_pauses = db.child("AllPauses").get()
    for record in all_pauses.each():
        if( record.val()["PauseEnd"] == "In Progress") and (record.val()["chatid"] == update.message.chat_id ):
            record_key  = record.key()
            time_start = record.val()["PauseStart"]
            pause = "exist"
    if pause == "exist":
        PauseTime = datetime.strptime(dt_time, FMT) - datetime.strptime(time_start, FMT)
        data = {"PauseEnd": dt_time, "PauseTime": str(PauseTime)}
        db.child("AllPauses").child(record_key).update(data)
        update.message.reply_text(
            f'Pause end at {dt_string}',
            reply_markup=markup2
        )
        pause = "none"
    else:
        update.message.reply_text(
            "I cant find any data , maybe u're not in pause",
            reply_markup=markup2
        )
    return CHOOSING
def PauseShelude_User(update: Update, context: CallbackContext) -> int:
    auth = firebase.auth()
    user = auth.sign_in_with_email_and_password('drux@mail.com', '12345678')
    db = firebase.database()
    timenow = datetime.now(timezone("Europe/Chisinau"))
    dt_only = timenow.strftime("%d/%m/%Y")
    data = "none"
    all_pauses = db.child("AllPauses").get()
    time_list = []
    PauseNumber = 0
    if all_pauses is None:
        update.message.reply_text(
            "No data yet , you should try Pause button at first",
            reply_markup=markup2
        )
    else:
        for record in all_pauses.each():
            if (record.val()["Date"] == dt_only) and (record.val()["chatid"] == update.message.chat_id):
                update.message.reply_text(
                    f'Data:{record.val()["Date"]}|Start:{record.val()["PauseStart"]}|End:{record.val()["PauseEnd"]}|Time:{record.val()["PauseTime"]}',
                    reply_markup=markup2
                )
                time_list.append(record.val()["PauseTime"])
                PauseNumber = PauseNumber + 1
                data = "exist"
        if data == "none":
            update.message.reply_text(
                "No data yet , you should try Pause button at first",
                reply_markup=markup2
            )
        else:
            total = time_sum(time_list)
            update.message.reply_text(
                f'Total time:{total} | PauseNumber: {PauseNumber}',
                reply_markup=markup2
            )
    return CHOOSING
def day_table(update: Update, context: CallbackContext) -> int:
    auth = firebase.auth()
    user = auth.sign_in_with_email_and_password('drux@mail.com', '12345678')
    db = firebase.database()
    timenow = datetime.now(timezone("Europe/Chisinau"))
    dt_only = timenow.strftime("%d/%m/%Y")
    update.message.reply_text(f'Retrieving Pauses Table for {dt_only} \n')
    all_pauses = db.child("AllPauses").get()
    for record in all_pauses.each():
        if record.val()["Date"] == dt_only:
            update.message.reply_text(
                f'{record.val()["Name"]}|Start:{record.val()["PauseStart"]}|Time:{record.val()["PauseTime"]}',
                reply_markup=markup_admin
            )
            data = "exist"
    if data == "none":
         update.message.reply_text(
            "No data yet",
            reply_markup=markup_admin
        )
    return CHOOSING
def credits(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        f'Bot was made by DREDD | @dredd768',
        reply_markup=markup_admin
    )
    return CHOOSING

def time_sum(time:[str]) -> timedelta:
    """
    Calculates time from list of time hh:mm:ss format
    """

    return sum(
        [
            timedelta(hours=int(ms[0]), minutes=int(ms[1]), seconds=int(ms[2]))
            for t in time
            for ms in [t.split(":")]
        ],
        timedelta(),
    )

def day_times(update: Update, context: CallbackContext) -> int:
    global all_uid
    auth = firebase.auth()
    user = auth.sign_in_with_email_and_password('drux@mail.com', '12345678')
    db = firebase.database()
    timenow = datetime.now(timezone("Europe/Chisinau"))
    dt_only = timenow.strftime("%d/%m/%Y")
    update.message.reply_text(f'Retrieving Pauses Table for {dt_only} \n')
    all_pauses = db.child("AllPauses").get()
    time_list = []
    numerator = -1
    for id in all_uid:
        PauseNumber = 0
        for record in all_pauses.each():
            if record.val()["chatid"] == id and record.val()["Date"] == dt_only:
                time_list.append(record.val()["PauseTime"])
                PauseNumber = PauseNumber + 1
        numerator = numerator + 1
        total = time_sum(time_list)
        if PauseNumber != 0:
            update.message.reply_text(
                f'{all_userx[numerator]}|PauseNumber:{PauseNumber}|Time:{total}',
                 reply_markup=markup_admin
            )
        time_list = []

    return CHOOSING

def admin_panel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        f'Starting admin panel',
        reply_markup=markup_admin
    )
    return CHOOSING
def user_panel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        f'Starting user panel',
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
                MessageHandler(Filters.regex('^(day_table)$'), day_table),
                MessageHandler(Filters.regex('^(credits)$'), credits),
                MessageHandler(Filters.regex('^(day_times)$'), day_times),
                MessageHandler(Filters.regex('^(admin)$'), admin_panel),
                MessageHandler(Filters.regex('^(user_panel)$'), user_panel),
            ],

        },
        fallbacks=[MessageHandler(Filters.regex('^Done$'),done )],
    )

    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()