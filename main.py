import os
import shutil
import string
import filetype

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

import logging
logging.basicConfig(level=logging.INFO)

# from dotenv import load_dotenv
# load_dotenv()

ORIG_FOLDER = '/origin'
DEST_FOLDER = '/destination'

UID = os.environ.get('UID', 1001)
GID = os.environ.get('GID', 988)
PERMISSIONS = 0o766

def format_filename(s):
    valid_chars = "-_(). %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in s if c in valid_chars)
    filename = ' '.join(filename.split())
    name, ext = os.path.splitext(filename)
    filename = name.replace('.', '_') + ext
    filename = filename.replace(' ','_')
    return filename


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Waiting for content!")
    print(update.effective_user.username)


async def file_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_msg = await update.effective_message.reply_text("\u23F2\uFE0F File received")
    try:
        logging.info(update.message)
        if update.message.photo:
            file = await update.message.effective_attachment[-1].get_file()
        else:
            file = await update.message.effective_attachment.get_file()
        logging.info(f"File: {file}")
        orig_filename = "/".join(file.file_path.split('/')[-3:])
        ext = os.path.splitext(orig_filename)[1] if os.path.splitext(orig_filename)[1] else filetype.guess(f"{ORIG_FOLDER}/{orig_filename}").extension
        logging.info(f"File caption: {update.effective_message.caption}")
        # TODO file_name field
        dest_filename = f"{format_filename(update.effective_message.caption)}{ext}" if update.effective_message.caption else orig_filename.split('/')[-1]
        # logging.info(f"File destination: {dest_filename}")
        move_file_docker(orig_filename, dest_filename)
        await reply_msg.edit_text(f"\u2714\uFE0F File moved to Jellyfin as: {dest_filename}")
    except:
        await reply_msg.edit_text(f"\u274C An error occurred!")


def move_file_docker(orig_file_path, dest_file_path):
    shutil.move(f"{ORIG_FOLDER}/{orig_file_path}", f"{DEST_FOLDER}/{dest_file_path}")
    logging.info(f"File moved: {dest_file_path}")
    # Change ownership to the current user
    os.chown(f"{DEST_FOLDER}/{dest_file_path}", UID, GID)
    os.chmod(f"{DEST_FOLDER}/{dest_file_path}", PERMISSIONS)
    logging.info(f"Changed ownership of {dest_file_path} to {UID}:{GID}, permissions: {PERMISSIONS}")


def main():
    app = ApplicationBuilder() \
        .read_timeout(100) \
        .write_timeout(100) \
        .token(os.environ["TG_BOT_TOKEN"]) \
        .base_url(os.environ["TG_BOT_API_SERVER"]+'/bot') \
        .base_file_url(os.environ["TG_BOT_API_SERVER"]+'/file/bot') \
        .local_mode(True) \
        .build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO | filters.PHOTO | filters.Document.IMAGE, file_received))
    app.add_handler(MessageHandler(~(filters.VIDEO | filters.Document.VIDEO | filters.PHOTO | filters.Document.IMAGE), lambda u, c: c.bot.send_message(chat_id=u.effective_chat.id, text="\u274C Filetype unsupported!\nPlease send a video or an image!")))

    app.run_polling()


if __name__ == '__main__':
    main()
