import asyncio
import os
import sys
import subprocess
import bot_backend

def clear_credentials(config):
    if get_user_confirmation("Are you sure you want to clear saved API credentials and session file? This will require re-logging in."):
        config["api_id"] = None
        config["api_hash"] = None
        bot_backend.save_configuration(config)
        if os.path.exists(bot_backend.SESSION_FILE):
            os.remove(bot_backend.SESSION_FILE)
            print_success("Session file removed.")
        else:
            print_info("No session file found to remove.")
        print_success("API credentials cleared.")
    wait_for_enter()

# === UI Helper Functions ===
def print_header(title):
    print("\n" + "="*50)
    print(f" ❚ {title}")
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

# === CLI Specific Implementations ===

def display_welcome_screen():
    print_header("Telegram Auto Forwarder Bot v2.0 (CLI)")
    print("Automatically forward Telegram messages from one chat to another.")
    print("\nPrerequisites:")
    print("  - A Telegram account")
    print("  - Your Telegram API ID and API Hash (from my.telegram.org)")
    wait_for_enter()

def check_system_requirements():
    print_header("Step 2: System & Dependency Check")
    all_ok = True
    if sys.version_info < (3, 8):
        print_error("Python 3.8+ is required.")
        all_ok = False
    else:
        print_success("Python version check passed.")

    try:
        __import__('telethon')
        print_success("Telethon library is installed.")
    except ImportError:
        print_info("Telethon is not installed. Attempting to install...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "telethon"])
            print_success("Telethon installed successfully.")
        except Exception as e:
            print_error(f"Failed to install Telethon: {e}")
            all_ok = False
    
    if not all_ok:
        sys.exit(1)
    wait_for_enter()

async def cli_login(config):
    print_header("Step 3: Telegram Login")
    
    # 1. Try to get API ID/Hash from environment variables
    api_id_env = os.environ.get("TELEGRAM_API_ID")
    api_hash_env = os.environ.get("TELEGRAM_API_HASH")

    # 2. If not in environment, try to get from config
    api_id_config = config.get("api_id")
    api_hash_config = config.get("api_hash")

    api_id = api_id_env if api_id_env else api_id_config
    api_hash = api_hash_env if api_hash_env else api_hash_config
    
    # 3. If still not found, prompt user
    if not all([api_id, api_hash]):
        print_info("API ID and Hash not found in environment variables or saved configuration.")
        api_id = input("Enter your API ID: ")
        api_hash = input("Enter your API Hash: ")
        
        # Save to config for persistence
        config["api_id"] = api_id
        config["api_hash"] = api_hash
        bot_backend.save_configuration(config)
    else:
        print_success("Using API ID and Hash from configuration or environment variables.")


    async def get_phone():
        return input("Enter your phone number: ")

    async def get_code():
        return input("Enter the code you received: ")

    async def get_password():
        return input("Enter your 2FA password: ")

    try:
        # Pass the obtained api_id and api_hash to the backend
        await bot_backend.initialize_telegram_client(int(api_id), api_hash, get_phone, get_code, get_password)
        print_success("Successfully connected to Telegram.")
    except Exception as e:
        print_error(f"Failed to login: {e}")
        sys.exit(1)
    wait_for_enter()

def select_forwarding_mode():
    print_header("Step 4: Forwarding Mode Selection")
    print("1. Original Caption Mode")
    print("2. Custom Caption Mode")
    while True:
        choice = input("Select your desired mode [1/2]: ").strip()
        if choice in ['1', '2']:
            return choice
        print_error("Invalid selection.")

async def configure_chats(config):
    print_header("Step 6: Source & Destination Chat Selection")
    if not get_user_confirmation("Do you want to change the source/destination chats?"):
        if not config.get("source_channel") or not config.get("destination_channel"):
            print_error("Source and destination must be set.")
            sys.exit(1)
        return config

    print_info("Fetching your chats...")
    try:
        chats = await bot_backend.get_chats()
        for chat in chats:
            print(f"  - Name: {chat['name']} ({chat['type']}), ID: {chat['id']}")
    except Exception as e:
        print_error(f"Could not fetch chats: {e}")
        sys.exit(1)

    while True:
        try:
            src_id = int(input("Enter the SOURCE chat ID: "))
            if any(c for c in chats if c['id'] == src_id):
                config["source_channel"] = src_id
                config["source_name"] = next(c['name'] for c in chats if c['id'] == src_id)
                break
            else:
                print_error("ID not found.")
        except ValueError:
            print_error("Invalid ID.")

    while True:
        try:
            dest_id = int(input("Enter the DESTINATION chat ID: "))
            if dest_id == config["source_channel"]:
                print_error("Destination cannot be the same as source.")
                continue
            if any(c for c in chats if c['id'] == dest_id):
                config["destination_channel"] = dest_id
                config["destination_name"] = next(c['name'] for c in chats if c['id'] == dest_id)
                break
            else:
                print_error("ID not found.")
        except ValueError:
            print_error("Invalid ID.")
    
    bot_backend.save_configuration(config)
    print_success("Chats selected.")
    return config

async def main():
    display_welcome_screen()
    check_system_requirements()
    
    config = bot_backend.load_configuration()

    if get_user_confirmation("Do you want to clear previously saved API credentials and session?"):
        clear_credentials(config)
    
    await cli_login(config)
    
    mode = select_forwarding_mode()
    
    if mode == '2':
        if get_user_confirmation(f"Current prefix is '{config['prefix']}'. Change it?"):
            config["prefix"] = input("Enter new prefix: ").strip()
        if get_user_confirmation(f"Current counter is {config['count']}. Reset to 1?"):
            config["count"] = 1
        bot_backend.save_configuration(config)

    config = await configure_chats(config)
    
    print_header("Step 7: Configuration Summary")
    print(f"  - Mode: {'Original' if mode == '1' else 'Custom'}")
    print(f"  - Source: {config['source_name']}")
    print(f"  - Destination: {config['destination_name']}")
    if not get_user_confirmation("Start forwarding?"):
        sys.exit(0)

    def status_callback(message):
        print_info(message)

    try:
        print_header("Step 8: Live Forwarding Status")
        print_info("Press CTRL + C to stop.")
        await bot_backend.start_forwarding(config, mode, status_callback)
    except KeyboardInterrupt:
        print_info("\nKeyboardInterrupt detected. Stopping forwarding...")
        await bot_backend.stop_forwarding() # Explicitly call stop_forwarding
    except asyncio.CancelledError: # This might be caught if task is cancelled externally
        print_info("\nForwarding task cancelled.")
    finally:
        print_info("\nForwarding stopped.")
        if get_user_confirmation("WARNING: This will permanently delete ALL messages from the SOURCE chat. Continue?"):
            print_info("Clearing source chat history...")
            await bot_backend.clear_chat(config["source_channel"])
        if get_user_confirmation("WARNING: This will permanently delete ALL messages from the DESTINATION chat. Continue?"):
            print_info("Clearing destination chat history...")
            await bot_backend.clear_chat(config["destination_channel"])
        
        await bot_backend.disconnect_client()
        print_success("Process finished.")

if __name__ == "__main__":
    asyncio.run(main())