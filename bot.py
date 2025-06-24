import os
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)
from telegram.error import Conflict
from config import TELEGRAM_BOT_TOKEN
from transcribe import transcribe_audio

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
WAITING_FOR_FILENAME = 1
user_data = {}

SUPPORTED_EXTENSIONS = ('.flac', '.m4a', '.mp3', '.mp4', '.mpeg', '.mpga', '.oga', '.ogg', '.wav', '.webm')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'Привет! Я бот для транскрибации аудио в текст. Отправь мне MP3 или M4A файл.'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'Как использовать бота:\n'
        '1. Отправь MP3 или M4A файл\n'
        '2. Укажи имя выходного файла (например: transcript.txt)'
    )

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    file_obj = None
    ext = None
    file_id = None
    file_name = None

    if update.message.audio:
        file_obj = await update.message.audio.get_file()
        file_name = update.message.audio.file_name or f"{update.message.audio.file_id}.mp3"
        ext = os.path.splitext(file_name)[1].lower() or '.mp3'
        file_id = update.message.audio.file_id
    elif update.message.document:
        file_obj = await update.message.document.get_file()
        file_name = update.message.document.file_name
        ext = os.path.splitext(file_name)[1].lower()
        file_id = update.message.document.file_id
    else:
        await update.message.reply_text("Пожалуйста, отправьте файл в формате MP3, M4A или другом поддерживаемом формате.")
        return ConversationHandler.END

    if ext not in SUPPORTED_EXTENSIONS:
        await update.message.reply_text(
            "Формат файла не поддерживается. Поддерживаются только: mp3, m4a, wav, ogg, webm, flac, mp4, mpeg, mpga, oga."
        )
        return ConversationHandler.END

    os.makedirs('temp', exist_ok=True)
    input_path = f"temp/{file_id}{ext}"
    await file_obj.download_to_drive(input_path)
    user_data[update.effective_user.id] = {'input_path': input_path}
    await update.message.reply_text('Файл получен! Укажите имя для выходного .txt файла.')
    return WAITING_FOR_FILENAME

async def handle_filename(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    if user_id not in user_data:
        await update.message.reply_text('Ошибка. Начните заново, отправив аудиофайл.')
        return ConversationHandler.END

    output_filename = update.message.text.strip()
    if not output_filename.lower().endswith('.txt'):
        output_filename += '.txt'
    output_path = f"temp/{output_filename}"

    try:
        await update.message.reply_text('Начинаю транскрибацию... Подождите.')
        transcribe_audio(user_data[user_id]['input_path'], output_path)
        with open(output_path, 'rb') as file:
            await update.message.reply_document(document=file, filename=output_filename)
        await update.message.reply_text('Готово!')
    except Exception as e:
        logger.error(f"Error transcribing: {e}")
        await update.message.reply_text('Произошла ошибка при транскрибации.')
    finally:
        # Clean up files
        for path in (user_data[user_id]['input_path'], output_path):
            if os.path.exists(path):
                os.remove(path)
        user_data.pop(user_id, None)

    return ConversationHandler.END

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    error = context.error
    if isinstance(error, Conflict):
        await context.bot.delete_webhook()
        return
    logger.error(f"Unexpected error: {error}", exc_info=True)

async def on_startup(app: Application) -> None:
    # Delete any existing webhook before polling
    await app.bot.delete_webhook()
    logger.info("Webhook deleted, ready for polling.")


def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is missing. Set it in .env.")

    # Use post_init to run on_startup after app is created
    application = (
        Application
        .builder()
        .token(TELEGRAM_BOT_TOKEN)
        .post_init(on_startup)
        .build()
    )

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    conv = ConversationHandler(
        entry_points=[MessageHandler(filters.AUDIO | filters.Document.ALL, handle_audio)],
        states={WAITING_FOR_FILENAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_filename)]},
        fallbacks=[CommandHandler("start", start)]
    )
    application.add_handler(conv)
    application.add_error_handler(error_handler)

    # Start polling (synchronous)
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )

if __name__ == '__main__':
    main()