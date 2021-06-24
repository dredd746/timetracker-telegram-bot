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



def start(update: Update, context: CallbackContext) -> int:

    update.message.reply_text(
        f'You was logged in , welcome {update.message.from_user.username}',
        reply_markup=markup2
    )

    return CHOOSING

def done(update: Update, context: CallbackContext) -> int:
    return ConversationHandler.END

def pause_model(update: Update, context: CallbackContext) -> int:
    auth = firebase.auth()
    user = auth.sign_in_with_email_and_password('drux@mail.com', '12345678')
    db = firebase.database()
    timenow = datetime.now()
    dt_string = timenow.strftime("%d/%m/%Y %H:%M:%S")
    dt_only = timenow.strftime("%d/%m/%Y")
    dt_time = timenow.strftime("%H:%M:%S")

    data = {"Date": dt_only, "Name": update.message.from_user.username, "PauseStart": dt_time, "PauseEnd": "In Progress",
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
    timenow = datetime.now()
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
        PauseTime = PauseTime = datetime.strptime(dt_time, FMT) - datetime.strptime(time_start, FMT)
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
    timenow = datetime.now()
    dt_only = timenow.strftime("%d/%m/%Y")
    data = "none"
    all_pauses = db.child("AllPauses").get()

    if all_pauses is None:
        update.message.reply_text(
            "No data yet , maybe you should try Pause button",
            reply_markup=markup2
        )
    else:
        for record in all_pauses.each():
            if (record.val()["Date"] == dt_only) and (record.val()["chatid"] == update.message.chat_id):
                update.message.reply_text(
                    f'Data:{record.val()["Date"]}|Start:{record.val()["PauseStart"]}|End:{record.val()["PauseEnd"]}|Time:{record.val()["PauseTime"]}',
                    reply_markup=markup2
                )
                data = "exist"
        if data == "none":
            update.message.reply_text(
                "No data yet , maybe you should try Pause button",
                reply_markup=markup2
            )
    return CHOOSING
def Admin_Panel(update: Update, context: CallbackContext) -> int:
    auth = firebase.auth()
    user = auth.sign_in_with_email_and_password('drux@mail.com', '12345678')
    db = firebase.database()
    timenow = datetime.now()
    dt_only = timenow.strftime("%d/%m/%Y")
    update.message.reply_text(f'Retrieving Pauses Table for {dt_only} \n')
    all_pauses = db.child("AllPauses").get()
    for record in all_pauses.each():
        if record.val()["Date"] == dt_only:
            update.message.reply_text(
                f'{record.val()["Name"]}|Start:{record.val()["PauseStart"]}|Time:{record.val()["PauseTime"]}',
                reply_markup=markup2
            )
            data = "exist"
    if data == "none":
         update.message.reply_text(
            "No data yet",
            reply_markup=markup2
        )
    return CHOOSING


def credits(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        f'Bot was made by DREDD | @dredd768',
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