import os
# Import necessary libraries:
from telegram import Update #upm package(python-telegram-bot)
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, InlineKeyboardMarkup, InlineKeyboardButton  

from db import Database

'''
d = {"auth_provider_x509_cert_url" : os.environ["auth_provider_x509_cert_url"],
"auth_uri" : os.environ["auth_uri"],
"client_email": os.environ["client_email"],
"client_id": os.environ["client_id"],
"client_x509_cert_url": os.environ["client_x509_cert_url"],
"private_key": os.environ["PRIVATE_KEY"].replace('\\n', '\n'),
"private_key_id": os.environ["private_key_id"],
"project_id": os.environ["project_id"],
"token_uri": os.environ["token_uri"],
"type": os.environ["type"]}

# Set your path:

# Set scope to use when authenticating:
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive.file',
         'https://www.googleapis.com/auth/drive']
# Authenticate using your credentials, saved in JSON in Step 1:
creds = ServiceAccountCredentials.from_json_keyfile_dict(keyfile_dict=d, scopes=scope)

# Initialize the client, and open the sheet by name:
client = gspread.authorize(creds)
sheet = client.open('suite').sheet1
# Get data from the sheet:
data = gspread_dataframe.get_as_dataframe(sheet)
df = data.drop(columns=[c for c in data.columns if "Unnamed" in c]).dropna(how="all")
'''
db = Database()
db.create_tables()

def start(update: Update, context: CallbackContext) -> None:
    """Sends a message with three inline buttons attached."""
    keyboard = [
        [InlineKeyboardButton("Track Exercise", callback_data='1')],
        [InlineKeyboardButton("Retrieve", callback_data='2')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose:', reply_markup=reply_markup)

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("shape is: ")

def log(update: Update, context: CallbackContext) -> None:
  db.insert_entry(update.message.from_user.username, update.message.text, 3, 2)

def get_one(update: Update, context: CallbackContext) -> None:
  update.message.reply_text(db.get_all())


def main():

    updater = Updater(os.getenv("TOKEN"))

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", help_command))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("add_entry", log))
    dispatcher.add_handler(CommandHandler("get_one", get_one))
    # dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, log))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()