📄 Telegram Auto Forwarder Bot 

📌 Overview
This Python bot allows you to automatically forward messages from one Telegram chat/group/channel to another. It supports two modes:

1.Original Caption Mode — forwards all messages exactly as-is.
2.Custom Caption Mode — forwards only media files (videos, photos, PDFs, etc.) with a custom caption prefix + counter.


It also saves settings like:
>>Source/destination chat IDs
>>Caption prefix
>>Counter for custom captions

⚙️1. Pre-configuration (Python & Libraries)
✅Step 1: Install Python
Make sure you have Python 3.8+ installed. You can check with:

bash
python --version

If not installed, download from:
🔗 https://www.python.org/downloads/

✅ Step 2: Install Required Library
Install Telethon, the Telegram API wrapper used in the bot:

pip install telethon
🧾 2. Get Your Telegram API Credentials
To use the Telegram API, you need your own api_id and api_hash.

Steps:
1>Go to: https://my.telegram.org.
2>Log in with your phone number.
3>Click API Development Tools.
4>Fill the form with app name and description

You'll get:
api_id → a number (usually 6–7 digits)
api_hash → a long alphanumeric string

🗃️ 3. Folder & File Setup
File:
Save the full bot code into a file like telegram_forwarder.py

Providing API Credentials:
The bot needs your Telegram API ID and API Hash to work. You can provide them in three ways:
1. Environment Variables (Recommended): Set the TELEGRAM_API_ID and TELEGRAM_API_HASH environment variables. The bot will automatically use them.
2. Interactive Prompt: If you haven't set environment variables, the bot will prompt you to enter your credentials the first time you run it.
3. Session File: After you log in once, the bot creates a forward_bot_session.session file. This file stores your session, so you don't have to log in every time.

Config file:
The bot will automatically create a bot_config.json file to save:
>Caption prefix & Counter
>Source & destination channel/group IDs

🚀 4. How to Run the Program
Run this from your terminal or command prompt:
python telegram_forwarder.py

🤖 5. Mode Selection (At Runtime)
On running, the bot asks:

"How do you want to forward messages?"

Option 1: Forward with original captions
Forwards all message types exactly as-is (including plain text)

Useful for mirroring chat/group content

Option 2: Forward with custom captions
Forwards only media messages.

Caption format: <prefix> <counter>

Example: Caption 1, Caption 2, etc.
Skips text-only messages

You will be asked:
i. Do you want to change the caption prefix?

ii. Do you want to reset the counter?

🔄 6. Source/Destination Setup
You are asked every time:

"Do you want to change source/destination group/channel?"

If yes:
The bot will display all your joined Telegram groups/channels with their names and IDs.
You copy the ID of the source and destination chats from the list and input them.

📦 7. What Gets Forwarded
Mode	               Media Files (Videos, Photos, Docs)	Text-Only Messages	Captions
Original Caption	✅ All forwarded	                ✅ All forwarded	Original
Custom Caption   	✅ Only media with prefix + counter	❌ Skipped	         Custom

💾 8. What’s Stored in bot_config.json
Example:
{
  "prefix": "UNIT AND DIMENSIONS",
  "count": 5,
  "source_channel": -10015455555,
  "destination_channel": -100987554545
}
This ensures:
i. The counter picks up where it left off
ii. Your channel settings are saved

Only updated if you choose to change them.

🔒 9. Session Management
The first time you run the script, you'll be asked to log in using your Telegram account (code sent via Telegram).

A local file forward_bot_session.session is saved, so you don’t need to log in every time.

🛑 10. Stop the Bot
To stop the bot (especially when it's listening for new messages):
>>Press CTRL + C in the terminal

>>This stops the real-time message handler

🧰 12. Advanced Notes
i. If you need to clear the chat history of source or destination channel/group, you will get two options after forwarding is completed, if you want to clear the source or destination group/channel, Choose 'Y' otherwise 'N'  .   
ii. You can run the bot on Windows, Linux, macOS or even a Raspberry Pi.

🧪Example Use Cases
      Scenario	                           	            Mode to Use
Backing up chat history	          			 Original Caption Mode
Publishing study materials in order			 Custom Caption Mode
Auto-forwarding notes from a group                  	Original Caption Mode
Posting structured lessons/files to a channel		Custom Caption Mode


You can now:
i. Start the bot with python telegram_forwarder.py
ii. Select your preferred mode
iii. Set up source/destination
iv. Sit back and let the bot handle the rest!