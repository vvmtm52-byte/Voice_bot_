import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Convert voice → text using OpenAI
def transcribe_voice(file_path):
    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    files = {"file": open(file_path, "rb")}
    data = {"model": "gpt-4o-mini-tts"} 

    r = requests.post(url, headers=headers, files=files, data=data)
    return r.json().get("text", "Transcription failed.")

# Convert text → female voice using OpenAI
def text_to_voice(text, output="output.mp3"):
    url = "https://api.openai.com/v1/audio/speech"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "gpt-4o-mini-tts",
        "voice": "alloy",  
        "input": text
    }

    r = requests.post(url, headers=headers, json=data)
    with open(output, "wb") as f:
        f.write(r.content)
    return output

# When user sends voice message
async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.voice.get_file()
    file_path = "voice.ogg"
    await file.download_to_drive(file_path)

    text = transcribe_voice(file_path)
    audio = text_to_voice(text)

    await update.message.reply_voice(voice=open(audio, "rb"))

# App Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a voice message and I will convert it to a female voice 😊")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.VOICE, voice_handler))
    app.add_handler(MessageHandler(filters.COMMAND, start))
    app.run_polling()

if __name__ == "__main__":
    main()
