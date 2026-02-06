
import asyncio
import json
import os
import sys
import subprocess

try:
    from telethon import TelegramClient, events
    from telethon.tl.functions.messages import DeleteMessagesRequest
    from telethon.errors import SessionPasswordNeededError
except ImportError:
    pass  # Defer handling to the dependency check

# === Constants & Configuration ===
VERSION = "2.0"
CONFIG_FILE = "bot_config.json"
SESSION_FILE = "forward_bot_session.session"

DEFAULT_CONFIG = {
    "prefix": "Caption",
    "count": 1,
    "source_channel": None,
    "destination_channel": None,
    "source_name": "Not Set",
    "destination_name": "Not Set"
}

# In-memory state
client = None
config = DEFAULT_CONFIG.copy()
changes_made = False

# === UI Helper Functions ===
def print_header(title):
    print("\n" + "="*50)
    print(f"""
 ❚ {title}
 ❚"""
)
    print("="*50)

def print_error(message):
    print(f"❌ ERROR: {message}")

def print_success(message):
    print(f"✅ SUCCESS: {message}")

def print_info(message):
    print(f"ℹ️ INFO: {message}")

def get_user_confirmation(prompt):
    while True:
        choice = input(f"🤔 {prompt} (y/n): ").strip().lower()
        if choice in ['y', 'n']:
            return choice == 'y'
    
def wait_for_enter():
    input("\nPress Enter to continue...")

# === Step 1: Welcome Screen ===
def display_welcome_screen():
    print_header(f"Telegram Auto Forwarder Bot v{VERSION}")
    print("Automatically forward Telegram messages from one chat to another.")
    print("\nPrerequisites:")
    print("  - A Telegram account")
    print("  - Your Telegram API ID and API Hash (from my.telegram.org)")
    wait_for_enter()

# === Step 2: System & Dependency Check ===
def check_system_requirements():
    print_header("Step 2: System & Dependency Check")
    all_ok = True
    
    # Check Python version
    if sys.version_info < (3, 8):
        print_error("Python 3.8+ is required. You are using Python {}.{}".format(*sys.version_info))
        all_ok = False
    else:
        print_success("Python version check passed (>= 3.8).")

    # Check Telethon installation
    try:
        __import__('telethon')
        print_success("Telethon library is installed.")
    except ImportError:
        print_error("Telethon library is not installed. Attempting to install...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "telethon"])
            print_success("Telethon installed successfully.")
            __import__('telethon') # Verify import after install
        except Exception as e:
            print_error(f"Failed to install Telethon: {e}")
            print_info("Please try installing it manually: pip install telethon")
            all_ok = False

    if not all_ok:
        print("\nPlease resolve the issues above and restart the tool.")
        sys.exit(1)
    
    wait_for_enter()

# === Step 3: Telegram Login & Session Handling ===
async def initialize_telegram_client():
    global client
    print_header("Step 3: Telegram Login")

    api_id = None
    api_hash = None

    if os.path.exists(SESSION_FILE):
        print_info("Existing session file found. Login will be skipped if the session is valid.")
        # Use dummy values if session exists, Telethon doesn't need them to connect
        api_id = 12345
        api_hash = "dummy"
    else:
        print_info("Login is required for the first time.")
        print_info("You can find your API credentials at my.telegram.org (App API ID and Hash).")
        print_info("NOTE: Your input will be visible as you type.")
        try:
            api_id = int(os.environ.get("TELEGRAM_API_ID", input("Enter your API ID: ")))
            api_hash = os.environ.get("TELEGRAM_API_HASH", input("Enter your API Hash: "))
        except (ValueError, TypeError):
            print_error("API ID must be an integer.")
            sys.exit(1)

    try:
        client = TelegramClient(SESSION_FILE, api_id, api_hash)
        await client.connect()

        if not await client.is_user_authorized():
            # This block will run if the session is invalid or first-time login
            print_info("Session invalid or expired. Please log in.")
            if not all([api_id, api_hash]) or api_id == 12345: # Re-ask for credentials if they were dummy
                print_info("Please provide your API credentials again (from my.telegram.org).")
                api_id = int(os.environ.get("TELEGRAM_API_ID", input("Re-enter your API ID: ")))
                api_hash = os.environ.get("TELEGRAM_API_HASH", input("Re-enter your API Hash: "))
                client = TelegramClient(SESSION_FILE, api_id, api_hash)
                await client.connect()

            phone_number = input("Enter your phone number (e.g., +1234567890): ").strip()
            await client.send_code_request(phone_number)
            try:
                await client.sign_in(phone_number, input("Enter the code you received: "))
            except SessionPasswordNeededError:
                password = input("Two-step verification is enabled. Please enter your password: ")
                await client.sign_in(password=password)
        
        print_success("Successfully connected to Telegram.")
        
    except Exception as e:
        print_error(f"Failed to login: {e}")
        print_info("Please ensure your API credentials and phone number are correct.")
        if os.path.exists(SESSION_FILE):
            print_info("You may need to delete the 'forward_bot_session.session' file and try again.")
        sys.exit(1)

    wait_for_enter()    
# === Step 4: Forwarding Mode Selection ===
def select_forwarding_mode():
    print_header("Step 4: Forwarding Mode Selection")
    print("1. 📖 Original Caption Mode")
    print("   - Forwards all message types (text, media, etc.).")
    print("   - Keeps original text and captions.")
    print("   - Best for chat backups or mirroring content.\n")

    print("2. 📝 Custom Caption Mode")
    print("   - Forwards only media files (videos, photos, documents).")
    print("   - Applies a custom caption: <PREFIX> <COUNTER>.")
    print("   - Skips text-only messages.")
    print("   - Best for structured content like study materials.\n")

    while True:
        choice = input("Select your desired mode [1/2]: ").strip()
        if choice in ['1', '2']:
            print_success(f"Mode '{'Original' if choice == '1' else 'Custom'}' selected.")
            wait_for_enter()
            return choice
        print_error("Invalid selection. Please enter 1 or 2.")
        
# === Step 5: Custom Caption Configuration ===
def configure_custom_captions():
    global changes_made
    print_header("Step 5: Custom Caption Configuration")
    
    if get_user_confirmation(f"Current prefix is '{config['prefix']}'. Do you want to change it?"):
        new_prefix = input("Enter new caption prefix: ").strip()
        if new_prefix:
            config["prefix"] = new_prefix
            changes_made = True
            print_success(f"Prefix updated to '{config['prefix']}'.")

    if get_user_confirmation(f"Current counter is {config['count']}. Do you want to reset it to 1?"):
        config["count"] = 1
        changes_made = True
        print_success("Counter has been reset to 1.")

    print("\nLive Preview Example:")
    print(f"  Caption: {config['prefix']} {config['count']}")
    
    wait_for_enter()
    
# === Step 6: Source & Destination Chat Selection ===
async def select_chats():
    global changes_made
    print_header("Step 6: Source & Destination Chat Selection")
    
    prompt = "Do you want to change the source and destination chats?"
    if not config.get("source_channel") or not config.get("destination_channel"):
        prompt = "You must set the source and destination chats. Continue?"
    
    if not get_user_confirmation(prompt):
        if not config.get("source_channel") or not config.get("destination_channel"):
            print_error("Source and destination must be set before proceeding.")
            sys.exit(1)
        return

    print_info("Fetching your chats... This may take a moment.")
    chats = []
    try:
        async for dialog in client.iter_dialogs():
            chat_type = "Channel" if dialog.is_channel else "Group" if dialog.is_group else "User"
            chats.append({"id": dialog.id, "name": dialog.name, "type": chat_type})
        
        print("\n--- Your Accessible Chats ---")
        for chat in chats:
            print(f"  - Name: {chat['name']} ({chat['type']})")
            print(f"    ID: {chat['id']}")
        print("---------------------------\n")

    except Exception as e:
        print_error(f"Could not fetch chats: {e}")
        return

    while True:
        try:
            src_id_str = input("Enter the SOURCE chat ID: ").strip()
            src_id = int(src_id_str)
            if any(c for c in chats if c['id'] == src_id):
                config["source_channel"] = src_id
                config["source_name"] = next(c['name'] for c in chats if c['id'] == src_id)
                break
            else:
                print_error("ID not found in your accessible chats. Please copy it exactly.")
        except ValueError:
            print_error("Invalid ID. It must be a number.")
            
    while True:
        try:
            dest_id_str = input("Enter the DESTINATION chat ID: ").strip()
            dest_id = int(dest_id_str)
            if dest_id == config["source_channel"]:
                print_error("Destination chat cannot be the same as the source chat.")
                continue
            if any(c for c in chats if c['id'] == dest_id):
                config["destination_channel"] = dest_id
                config["destination_name"] = next(c['name'] for c in chats if c['id'] == dest_id)
                changes_made = True
                break
            else:
                print_error("ID not found in your accessible chats. Please copy it exactly.")
        except ValueError:
            print_error("Invalid ID. It must be a number.")

    print_success("Chats selected.")
    print(f"  - Source: {config['source_name']} ({config['source_channel']})")
    print(f"  - Destination: {config['destination_name']} ({config['destination_channel']})")
    wait_for_enter()

# === Step 7: Configuration Summary Screen ===
def display_configuration_summary(mode):
    print_header("Step 7: Configuration Summary")
    print(f"  - Forwarding Mode:   {'Original Caption' if mode == '1' else 'Custom Caption'}")
    print(f"  - Source Chat:       {config['source_name']} ({config['source_channel']})")
    print(f"  - Destination Chat:  {config['destination_name']} ({config['destination_channel']})")
    if mode == '2':
        print(f"  - Caption Prefix:    '{config['prefix']}'")
        print(f"  - Next Counter Value:  {config['count']}")
    
    print("\n" + "-"*50)
    if not get_user_confirmation("Start forwarding with these settings?"):
        print_info("Operation cancelled by user.")
        sys.exit(0)

# === Step 8: Live Forwarding Status Screen ===
async def start_forwarding(mode):
    print_header("Step 8: Live Forwarding Status")
    print_info("Press CTRL + C to stop forwarding at any time.")
    
    forwarded_count = 0
    skipped_count = 0

    async def forward_message(message, is_new=False):
        nonlocal forwarded_count, skipped_count
        try:
            if mode == '1': # Original Caption
                await client.send_message(config["destination_channel"], message)
                forwarded_count += 1
                print(f"  [+] Forwarded message ID {message.id}. Total: {forwarded_count}")
            elif mode == '2' and message.media: # Custom Caption
                caption = f"{config['prefix']} {config['count']}"
                await client.send_file(config["destination_channel"], file=message.media, caption=caption)
                config["count"] += 1
                forwarded_count += 1
                print(f"  [+] Forwarded media with caption '{caption}'. Total: {forwarded_count}")
                # Save config frequently for counter
                if is_new: save_configuration(force=True)
            else:
                skipped_count += 1
                print(f"  [-] Skipped text-only message ID {message.id}. Total skipped: {skipped_count}")
            
            # Prevent rate limiting
            await asyncio.sleep(1)

        except Exception as e:
            print_error(f"Failed to forward message {message.id}: {e}")

    # Backfill old messages
    print_info(f"Starting backfill from '{config['source_name']}'...")
    try:
        async for message in client.iter_messages(config["source_channel"], reverse=True):
            await forward_message(message)
    except Exception as e:
        print_error(f"An error occurred during backfill: {e}")
        
    print_success(f"Backfill complete. Forwarded: {forwarded_count}, Skipped: {skipped_count}.")
    
    # Listen for new messages
    @client.on(events.NewMessage(chats=config["source_channel"]))
    async def new_message_handler(event):
        await forward_message(event.message, is_new=True)

    print_info("Listening for new messages...")
    await client.run_until_disconnected()

# === Step 9: Post-Forwarding Actions ===
async def handle_post_forwarding_actions():
    global changes_made
    print_header("Step 9: Post-Forwarding Actions")
    
    print_info("Forwarding has been stopped.")

    warning = "This action is IRREVERSIBLE and will permanently delete messages."
    print(f"\n⚠️ WARNING: {warning} ⚠️")
    
    if get_user_confirmation(f"Do you want to clear the source chat history from '{config['source_name']}'?"):
        await clear_chat(config["source_channel"])
        changes_made = True

    print(f"\n⚠️ WARNING: {warning} ⚠️")
    if get_user_confirmation(f"Do you want to clear the destination chat history from '{config['destination_name']}'?"):
        await clear_chat(config["destination_channel"])
        changes_made = True

async def clear_chat(chat_id):
    print_info(f"Attempting to clear chat ID: {chat_id}")
    try:
        message_ids = [msg.id async for msg in client.iter_messages(chat_id, limit=None)]
        if not message_ids:
            print_info("No messages found to delete.")
            return
            
        print(f"Found {len(message_ids)} messages to delete...")
        # Delete in chunks of 100, as per Telegram API limits
        for i in range(0, len(message_ids), 100):
            chunk = message_ids[i:i+100]
            await client(DeleteMessagesRequest(id=chunk, revoke=True))
            print(f"  - Deleted {len(chunk)} messages...")
        print_success(f"Successfully cleared chat.")
    except Exception as e:
        print_error(f"Failed to clear chat: {e}")

# === Step 10: Exit & Save State ===
def save_configuration(force=False):
    if changes_made or force:
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f, indent=2)
            print_success(f"Configuration saved to {CONFIG_FILE}.")
            print_info("Counter state and chat settings are preserved.")
        except Exception as e:
            print_error(f"Could not save configuration: {e}")

# === Main Execution Logic ===
async def main():
    try:
        # Load existing config
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                global config
                config.update(json.load(f))
        
        display_welcome_screen()
        check_system_requirements()
        await initialize_telegram_client()
        
        mode = select_forwarding_mode()
        
        if mode == '2':
            configure_custom_captions()
            
        await select_chats()
        
        display_configuration_summary(mode)
        
        await start_forwarding(mode)
        
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("\n" + "="*50)
        print_info("User interrupted the process.")
    finally:
        if client and client.is_connected():
            await handle_post_forwarding_actions()
            await client.disconnect()
            
        save_configuration()
        print_header("Step 10: Exit")
        print_info("You can restart the tool anytime using the same configuration.")
        print_success("Process finished.")

if __name__ == "__main__":
    # Wrap the main async function to be run
    asyncio.run(main())

