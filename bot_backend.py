import asyncio
import json
import os
import sys
import threading
import functools
import time

from telethon import TelegramClient, events
from telethon.tl.functions.messages import DeleteMessagesRequest
from telethon.errors import SessionPasswordNeededError

# === Constants & Configuration ===
CONFIG_FILE = "bot_config.json"
SESSION_FILE = "forward_bot_session.session"
DEFAULT_CONFIG = {
    "prefix": "Caption",
    "count": 1,
    "source_channel": None,
    "destination_channel": None,
    "source_name": "Not Set",
    "destination_name": "Not Set",
    "api_id": None,
    "api_hash": None
}

client = None


def load_configuration():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return DEFAULT_CONFIG.copy()

def save_configuration(config):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"Error saving configuration: {e}")

async def initialize_telegram_client(api_id, api_hash, on_phone_request, on_code_request, on_password_request):
    global client
    client = TelegramClient(SESSION_FILE, api_id, api_hash)
    await client.connect()

    if not await client.is_user_authorized():
        phone_number = await on_phone_request()
        await client.send_code_request(phone_number)
        try:
            code = await on_code_request()
            await client.sign_in(phone_number, code)
        except SessionPasswordNeededError:
            password = await on_password_request()
            await client.sign_in(password=password)
    
    return client

async def get_chats():
    if not client or not client.is_connected():
        raise ConnectionError("Client is not connected.")
    
    chats = []
    async for dialog in client.iter_dialogs():
        chat_type = "Channel" if dialog.is_channel else "Group" if dialog.is_group else "User"
        chats.append({"id": dialog.id, "name": dialog.name, "type": chat_type})
    return chats


async def start_forwarding(config, mode, status_callback):
    if not client:
        raise ConnectionError("Client not initialized.")

    forwarded_count = 0
    skipped_count = 0

    status_callback("Starting backfill of old messages...")

    try:
        async for message in client.iter_messages(config["source_channel"], reverse=True):
            if mode == '1': # Original Caption
                try:
                    await client.forward_messages(config["destination_channel"], message)
                    forwarded_count += 1
                    status_callback(f"Forwarded message ID {message.id}. Total: {forwarded_count}")
                except Exception as e:
                    status_callback(f"ERROR forwarding message ID {message.id}: {e}")
            elif mode == '2' and message.media: # Custom Caption
                caption = f"{config['prefix']} {config['count']}"
                await client.send_file(config["destination_channel"], file=message.media, caption=caption)
                config["count"] += 1
                forwarded_count += 1
                status_callback(f"Forwarded media with caption '{caption}'. Total: {forwarded_count}")
                save_configuration(config)
            else:
                skipped_count += 1
                status_callback(f"Skipped text-only message ID {message.id}. Total skipped: {skipped_count}")
            
            await asyncio.sleep(1) # Rate limiting
    except asyncio.CancelledError:
        status_callback("Backfill cancelled.")
        raise # Re-raise CancelledError to propagate it up
    except Exception as e:
        status_callback(f"Error during backfill: {e}")

    status_callback("Backfill complete. Listening for new messages...")

    @client.on(events.NewMessage(chats=config["source_channel"]))
    async def new_message_handler(event):
        nonlocal forwarded_count, skipped_count
        if mode == '1':
            try:
                await client.forward_messages(config["destination_channel"], event.message)
                forwarded_count += 1
                status_callback(f"Forwarded new message ID {event.message.id}. Total: {forwarded_count}")
            except Exception as e:
                status_callback(f"ERROR forwarding new message ID {event.message.id}: {e}")
        elif mode == '2' and event.message.media:
            caption = f"{config['prefix']} {config['count']}"
            await client.send_file(config["destination_channel"], file=event.message.media, caption=caption)
            config["count"] += 1
            forwarded_count += 1
            status_callback(f"Forwarded new media with caption '{caption}'. Total: {forwarded_count}")
            save_configuration(config)
        else:
            skipped_count += 1
            status_callback(f"Skipped new text-only message ID {event.message.id}. Total skipped: {skipped_count}")

    # Keep the event loop running to listen for new messages
    try:
        await client.run_until_disconnected()
    except asyncio.CancelledError:
        status_callback("Forwarding listener cancelled.")
        raise # Re-raise CancelledError to propagate it up

async def stop_forwarding():
    if client and client.is_connected():
        await client.disconnect()

async def clear_chat(chat_id):
    if not client:
        raise ConnectionError("Client not initialized.")
    
    message_ids = [msg.id async for msg in client.iter_messages(chat_id, limit=None)]
    if not message_ids:
        return "No messages to delete."
        
    for i in range(0, len(message_ids), 100):
        chunk = message_ids[i:i+100]
        await client(DeleteMessagesRequest(id=chunk, revoke=True))
    
    return f"Successfully deleted {len(message_ids)} messages."

async def logout():
    """
    Disconnects the client, clears credentials from config, and deletes session file.
    """
    await disconnect_client()
    
    # Clear credentials from config
    config = load_configuration()
    config['api_id'] = None
    config['api_hash'] = None
    save_configuration(config)

    # Delete session file
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
    
    print("Successfully logged out and cleared session.")


async def disconnect_client():
    global client
    if client and client.is_connected():
        await client.disconnect()
    client = None
