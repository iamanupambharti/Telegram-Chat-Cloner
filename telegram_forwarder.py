from telethon import TelegramClient, events
from telethon.tl.functions.messages import DeleteMessagesRequest
import asyncio
import json
import os

# === Your Telegram API Credentials ===
api_id =  0000000 # Replace with your actual API ID
api_hash = ''  # Replace with your actual API Hash

# === Config File ===
config_file = "bot_config.json"
default_config = {
    "prefix": "Captions",
    "count": 1,
    "source_channel": None,
    "destination_channel": None
}

# === Load or Initialize Config ===
if os.path.exists(config_file):
    with open(config_file, "r") as f:
        config = json.load(f)
else:
    config = default_config.copy()

client = TelegramClient("forward_bot_session", api_id, api_hash)


# === Ask User to Select Mode ===
async def select_mode():
    print("\nHow do you want to forward messages?")
    print("1. Forward with original captions (all types, including text)")
    print("2. Forward media with custom captions + counter (skip text-only)")
    while True:
        choice = input("Select mode [1/2]: ").strip()
        if choice in ['1', '2']:
            return choice
        print("Invalid input. Please enter 1 or 2.")


# === Ask to Change Source/Destination Chat ===
async def setup_source_destination():
    global config

    change_chats = input("Do you want to change source/destination channel/group? (y/n): ").strip().lower()
    if change_chats == 'y':
        print("\nFetching your Telegram chats...\n")
        async for dialog in client.iter_dialogs():
            print(f"{dialog.name} - ID: {dialog.id}")
        print("\nAbove are your accessible groups/channels.")

        while True:
            try:
                src = input("Enter the SOURCE chat ID: ").strip()
                config["source_channel"] = int(src)
                break
            except ValueError:
                print("Invalid ID. Try again.")

        while True:
            try:
                dest = input("Enter the DESTINATION chat ID: ").strip()
                config["destination_channel"] = int(dest)
                break
            except ValueError:
                print("Invalid ID. Try again.")


# === Ask to Set or Reset Caption Prefix and Counter ===
def setup_custom_caption_config():
    global config
    change_prefix = input(f"Current prefix is '{config['prefix']}'. Do you want to change it? (y/n): ").strip().lower()
    if change_prefix == 'y':
        new_prefix = input("Enter new caption prefix: ").strip()
        if new_prefix:
            config["prefix"] = new_prefix

    reset_counter = input(f"Current counter is {config['count']}. Reset to 1? (y/n): ").strip().lower()
    if reset_counter == 'y':
        config["count"] = 1


# === Save Config ===
def save_config():
    with open(config_file, "w") as f:
        json.dump(config, f)


# === Forward with Original Captions (All Messages) ===
async def forward_with_original_captions():
    print("🔁 Starting original caption bulk forwarding...")
    async for message in client.iter_messages(config["source_channel"], reverse=True):
        try:
            await client.send_message(config["destination_channel"], message)
            print(f"Forwarded message (ID: {message.id})")
            await asyncio.sleep(1)
        except Exception as e:
            print(f"Error forwarding message ID {message.id}: {e}")

    print("✅ Done. Now listening for new messages...")

    @client.on(events.NewMessage(chats=config["source_channel"]))
    async def original_handler(event):
        try:
            await client.send_message(config["destination_channel"], event.message)
            print(f"Forwarded new message (ID: {event.id})")
        except Exception as e:
            print(f"Error forwarding new message: {e}")

# === Forward with Custom Captions (Media Only) === 
async def forward_with_custom_captions():
    print("🎯 Starting custom caption bulk forwarding (media only)...")
    async for message in client.iter_messages(config["source_channel"], reverse=True):
        if message.media:
            caption = f"{config['prefix']} {config['count']}"
            try:
                await client.send_file(
                    config["destination_channel"],
                    file=message.media,
                    caption=caption
                )
                print(f"Forwarded with custom caption: {caption}")
                config["count"] += 1
                save_config()
                await asyncio.sleep(1)
            except Exception as e:
                print(f"Error forwarding media: {e}")
        elif message.message:
            print(f"Skipping text-only message ID {message.id}")

    print("✅ Bulk custom forwarding done.")

    # 🆕 CLEAR CHAT OPTION — INSIDE THE ASYNC FUNCTION
    clear_source = input("Do you want to clear the SOURCE chat after forwarding? (y/n): ").strip().lower()
    if clear_source == 'y':
        await clear_chat(config["source_channel"])

    clear_dest = input("Do you want to clear the DESTINATION chat after forwarding? (y/n): ").strip().lower()
    if clear_dest == 'y':
        await clear_chat(config["destination_channel"])

    print("✅ Now listening for new media messages...")

    @client.on(events.NewMessage(chats=config["source_channel"]))
    async def custom_handler(event):
        if event.media:
            caption = f"{config['prefix']} {config['count']}"
            try:
                await client.send_file(
                    config["destination_channel"],
                    file=event.media,
                    caption=caption
                )
                print(f"Forwarded new media with custom caption: {caption}")
                config["count"] += 1
                save_config()
            except Exception as e:
                print(f"Error forwarding new media: {e}")
        else:
            print("Skipped text-only message")



# === Main Function ===
async def main():
    mode = await select_mode()

    await setup_source_destination()

    if mode == '2':
        setup_custom_caption_config()

    save_config()

    if mode == '1':
        await forward_with_original_captions()
    else:
        await forward_with_custom_captions()

    await client.run_until_disconnected()


# === Run the Bot ===
with client:
    client.loop.run_until_complete(main())


#Added Later to code
async def clear_chat(chat_id):
    print(f"\nAttempting to clear chat: {chat_id}")
    message_ids = []
    async for msg in client.iter_messages(chat_id, limit=1000):
        message_ids.append(msg.id)

    if message_ids:
        try:
            await client(DeleteMessagesRequest(id=message_ids, revoke=True))
            print(f"✅ Deleted {len(message_ids)} messages from {chat_id}")
        except Exception as e:
            print(f"❌ Failed to delete messages: {e}")
    else:
        print(f"ℹ️ No messages found in chat {chat_id}")

