📄 Telegram Auto Forwarder Bot

📌 Overview
This Python bot allows you to automatically forward messages from one Telegram chat/group/channel to another. It is built using the `telethon` library for Telegram API interaction and `customtkinter` for the Graphical User Interface (GUI).

The bot offers two main ways to interact:

1.  **Graphical User Interface (GUI):** A user-friendly windowed application for easy setup and management.
2.  **Command Line Interface (CLI):** A console-based script (`telegram_forwarder.py`) for direct terminal interaction.

Both versions support two forwarding modes:
*   **Original Caption Mode:** Forwards all messages exactly as-is (including text, media, and their original captions).
*   **Custom Caption Mode:** Forwards only media files (videos, photos, PDFs, etc.) and applies a custom caption composed of a user-defined prefix and an incrementing counter.

Configuration details such as source/destination chat IDs, custom caption prefixes, and the current counter are persisted in a `bot_config.json` file. The script also creates a `forward_bot_session.session` file to manage the user's Telegram session, avoiding the need to log in on every run.

---

⚙️ Setup & Installation

### Prerequisites

*   Python 3.8 or newer.
*   Your own Telegram `api_id` and `api_hash`. You can obtain these by following the instructions at [my.telegram.org](https://my.telegram.org).

### Installation

1.  **Download the Project:**
    Clone this repository or download the project files to your local machine.
    Navigate to the project directory in your terminal.

2.  **Install Dependencies:** The project relies on `telethon` and `customtkinter` libraries. Run the `requirements.py` script to install them:
    ```bash
    python requirements.py
    ```
    *Note: The GUI application (`gui.py`) might attempt to install missing dependencies automatically on first run, but it's recommended to run `python requirements.py` for consistency.*

---

🧾 Get Your Telegram API Credentials
To use the Telegram API, you need your own `api_id` and `api_hash`.

Steps:
1.  Go to: https://my.telegram.org.
2.  Log in with your phone number.
3.  Click "API Development Tools".
4.  Fill the form with your app name and a short description.

You'll receive:
*   `api_id` → a number (usually 6–7 digits)
*   `api_hash` → a long alphanumeric string

These credentials are essential for the bot to connect to your Telegram account.

---

🗃️ Configuration & Session Management

**Providing API Credentials:**
The bot needs your Telegram API ID and API Hash to work. You can provide them in three ways:
1.  **Environment Variables (Recommended):** Set `TELEGRAM_API_ID` and `TELEGRAM_API_HASH` environment variables. The bot will automatically use them.
2.  **Interactive Prompt/GUI Input:** If you haven't set environment variables, the bot will prompt you to enter your credentials (via terminal for CLI, or a dedicated login screen for GUI) the first time you run it.
3.  **Session File:** After you log in once, the bot creates a `forward_bot_session.session` file. This file securely stores your session, so you don't have to log in every time.

**Configuration File (`bot_config.json`):**
The bot will automatically create a `bot_config.json` file to save:
*   Caption prefix & Counter
*   Source & destination channel/group IDs
*   Your `api_id` and `api_hash` (if entered via prompt/GUI)

This ensures your settings are persistent across runs.

---

🚀 How to Run the Program

### Running the GUI Application (Recommended)

This is the easiest way to use the bot.

1.  Open your terminal or command prompt in the project directory.
2.  Run the GUI script:
    ```bash
    python gui.py
    ```
3.  **First Run Experience:**
    *   If dependencies are missing, it will automatically install them. The application might relaunch itself after installation.
    *   You will be presented with a login screen to enter your `api_id` and `api_hash`.
    *   Follow the on-screen prompts for phone number, verification code, and 2FA password (if enabled).

### Running the CLI Application

For terminal-only interaction.

1.  Ensure you have installed dependencies (see "Setup & Installation" above).
2.  Open your terminal or command prompt in the project directory.
3.  Run the CLI script:
    ```bash
    python telegram_forwarder.py
    ```
    The first time you run it, you will be prompted to enter your phone number and a login code sent to you via Telegram. It will then guide you through an interactive setup process for selecting the mode and a source/destination chats.

---

🤖 Using the Bot

### Login Process
Whether you use the GUI or CLI, the bot will guide you through the Telegram login process if a session file (`forward_bot_session.session`) doesn't exist or is invalid. You will be asked for your phone number, the verification code sent to your Telegram app, and optionally your 2FA password.

### Mode Selection
*   **GUI:** Use the radio buttons on the main screen to select "Original Caption" or "Custom Caption" mode.
*   **CLI:** The bot will prompt you in the terminal to choose between the two modes.

### Custom Caption Settings (for Custom Caption Mode)
*   **GUI:** Enter your desired prefix in the "Caption Prefix" field. You can reset the counter using the "Reset Counter" button.
*   **CLI:** The bot will ask if you want to change the caption prefix or reset the counter.

### Source/Destination Chat Selection
*   **GUI:** Click "Fetch Chats" to populate the dropdown menus. Then, select your "Source" and "Destination" chats from the respective dropdowns.
*   **CLI:** The bot will display a list of your chats with their IDs and ask you to input the source and destination chat IDs.

---

📦 What Gets Forwarded
| Mode              | Media Files (Videos, Photos, Docs) | Text-Only Messages | Captions                     |
| :---------------- | :--------------------------------- | :----------------- | :--------------------------- |
| Original Caption  | ✅ All forwarded                   | ✅ All forwarded   | Original                     |
| Custom Caption    | ✅ Only media with prefix + counter | ❌ Skipped         | Custom (`<prefix> <counter>`) |

---

💾 What’s Stored in `bot_config.json`
Example:
```json
{
  "prefix": "UNIT AND DIMENSIONS",
  "count": 5,
  "source_channel": -10015455555,
  "destination_channel": -100987554545,
  "api_id": 1234567,
  "api_hash": "your_api_hash_here"
}
```
This ensures:
*   The counter picks up where it left off.
*   Your channel settings are saved.
*   Your `api_id` and `api_hash` are remembered (encrypted in `forward_bot_session.session` and optionally in `bot_config.json`).

Only updated if you choose to change them or enter new API credentials.

---

🛑 Stop the Bot

*   **GUI:** Click the "Stop Forwarding" button. You can also close the application window normally.
*   **CLI:** Press `CTRL + C` in the terminal to stop the forwarding process.

---

🧰 Advanced Notes

*   **Clearing Chat History:** After forwarding is completed (or stopped), the bot will offer options to permanently delete ALL messages from the SOURCE and/or DESTINATION chats. Use with extreme caution!
*   **Platform Compatibility:** The bot can run on Windows, Linux, macOS, or even a Raspberry Pi.

---

🧪 Example Use Cases
| Scenario                                  | Mode to Use           |
| :---------------------------------------- | :-------------------- |
| Backing up chat history                   | Original Caption Mode |
| Publishing study materials in order       | Custom Caption Mode   |
| Auto-forwarding notes from a group        | Original Caption Mode |
| Posting structured lessons/files to a channel | Custom Caption Mode   |

---

You can now:
*   **For GUI:** Run `python gui.py` and follow the on-screen instructions.
*   **For CLI:** Run `python telegram_forwarder.py` and follow the terminal prompts.

Enjoy automated Telegram forwarding!
