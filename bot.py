import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from transcribe import transcribe_audio
from config import TELEGRAM_BOT_TOKEN

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# States for conversation
WAITING_FOR_FILENAME = 1

# Dictionary to store user states and data
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        'Привет! Я бот для превращения аудио в текст. '
        'Просто отправь мне MP3 файл, и я помогу тебе получить его текстовую версию.'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        'Как использовать бота:\n'
        '1. Отправь мне MP3 файл\n'
        '2. Укажи желаемое имя для текстового файла\n'
        '3. Получи готовый текстовый файл с транскрипцией'
    )

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the audio file and ask for the output filename."""
    # Get the audio file
    audio_file = await update.message.audio.get_file()
    
    # Create a temporary directory if it doesn't exist
    if not os.path.exists('temp'):
        os.makedirs('temp')
    
    # Download the file
    input_path = f"temp/{update.message.audio.file_id}.mp3"
    await audio_file.download_to_drive(input_path)
    
    # Store the input path in user data
    user_data[update.effective_user.id] = {'input_path': input_path}
    
    # Ask for the output filename
    await update.message.reply_text(
        'Файл получен! Пожалуйста, укажи желаемое имя для текстового файла '
        '(например: transcript.txt)'
    )
    
    return WAITING_FOR_FILENAME

async def handle_filename(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the filename and process the transcription."""
    user_id = update.effective_user.id
    
    if user_id not in user_data:
        await update.message.reply_text(
            'Произошла ошибка. Пожалуйста, начни сначала, отправив новый аудиофайл.'
        )
        return ConversationHandler.END
    
    # Get the output filename from user
    output_filename = update.message.text.strip()
    if not output_filename.endswith('.txt'):
        output_filename += '.txt'
    
    # Create output path
    output_path = f"temp/{output_filename}"
    
    try:
        # Process the transcription
        await update.message.reply_text('Начинаю транскрибацию... Это может занять некоторое время.')
        
        # Get the stored input path
        input_path = user_data[user_id]['input_path']
        
        # Transcribe the audio
        transcribe_audio(input_path, output_path)
        
        # Send the text file
        with open(output_path, 'rb') as file:
            await update.message.reply_document(
                document=file,
                filename=output_filename
            )
        
        # Clean up
        os.remove(input_path)
        os.remove(output_path)
        del user_data[user_id]
        
        await update.message.reply_text('Готово! Транскрипция успешно создана.')
        
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        await update.message.reply_text(
            'Произошла ошибка при обработке файла. Пожалуйста, попробуй еще раз.'
        )
    
    return ConversationHandler.END

def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.AUDIO, handle_audio)],
        states={
            WAITING_FOR_FILENAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_filename)],
        },
        fallbacks=[CommandHandler('start', start)]
    )

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(conv_handler)

    # Start the Bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main() 