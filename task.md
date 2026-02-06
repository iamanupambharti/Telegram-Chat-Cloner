You are designing a **user-friendly interface** for a **Telegram Auto Forwarder Bot** built in Python using the Telethon library.

The tool allows users to forward messages from one Telegram **source chat/group/channel** to a **destination chat/group/channel** using two modes:

1. **Original Caption Mode** – forwards everything exactly as-is.
2. **Custom Caption Mode** – forwards only media files with a custom caption prefix and an auto-increment counter.

The target users are **non-technical or semi-technical**, so the interface must be extremely **clear, guided, and error-proof**.

Your responsibility is to design the **complete UI/UX flow step by step**, ensuring the user can configure and run the tool confidently without confusion.

---

## 🎯 Core UX Goals (Must Follow)

* Step-by-step wizard-style flow
* Clear explanations before every input
* Minimal technical jargon
* Safe defaults with confirmations
* Friendly, human-readable messages
* Validation and error handling at every step

---

## 🧭 COMPLETE STEP-BY-STEP UI FLOW

### STEP 1: Welcome & Introduction Screen

* Display tool name and version
* Show a simple one-line description:
  "Automatically forward Telegram messages from one chat to another with optional custom captions."
* Clearly list prerequisites:

  * Telegram account
  * Telegram API ID & API Hash
* Show a **Continue** option

---

### STEP 2: System & Dependency Check

* Automatically check:

  * Python version (must be ≥ 3.8)
  * Telethon installation
* UI behavior:

  * Show ✅ for satisfied requirements
  * Show ❌ with exact install command if missing
* Do not allow continuation until all checks pass

---

### STEP 3: Telegram Login & Session Handling

* Explain clearly:

  * Login is required only the first time
  * A code will be sent via Telegram
* Prompt user for:

  * Phone number
  * OTP / login code
* On success:

  * Confirm session saved locally
* If session already exists:

  * Display: "Existing session found. Login skipped."

---

### STEP 4: Forwarding Mode Selection

Present two clearly separated options:

#### Option 1: Original Caption Mode

* Forwards all message types
* Keeps original text and captions
* Best for chat backup or mirroring

#### Option 2: Custom Caption Mode

* Forwards only media files (videos, photos, PDFs, documents)
* Applies custom caption format: `<PREFIX> <COUNTER>`
* Skips text-only messages
* Best for structured content like study materials

User must explicitly select one mode to continue.

---

### STEP 5: Custom Caption Configuration (Only for Custom Caption Mode)

* Ask:

  1. Do you want to change the caption prefix?

     * Show current prefix
     * Allow editing
  2. Do you want to reset the counter?

     * Show current counter value
* Display a live preview example:

  * Example: `UNIT AND DIMENSIONS 6`
* Save changes only after confirmation

---

### STEP 6: Source & Destination Chat Selection

* Ask:
  "Do you want to change the source and destination chat/channel?"

If YES:

* Display all joined chats with:

  * Chat name
  * Chat type (Group / Channel)
  * Chat ID
* Allow user to copy IDs and paste them into input fields

Validation rules:

* Source and destination must be different
* IDs must be valid and accessible

Show a confirmation summary before proceeding.

---

### STEP 7: Configuration Summary Screen

Display a clean, read-only summary:

* Selected forwarding mode
* Source chat name & ID
* Destination chat name & ID
* Caption prefix (if applicable)
* Current counter value

Ask for final confirmation:
"Start forwarding with these settings?"

---

### STEP 8: Live Forwarding Status Screen

* Show real-time status messages:

  * Listening for new messages
  * Number of messages/media forwarded
  * Number of skipped messages (if any)
* Display instruction:
  "Press CTRL + C to stop forwarding"

---

### STEP 9: Post-Forwarding Actions

After stopping the bot:

* Ask clearly:

  1. Do you want to clear the source chat history? (Y/N)
  2. Do you want to clear the destination chat history? (Y/N)
* Display strong warnings for irreversible actions
* Perform deletion only after explicit confirmation

---

### STEP 10: Exit & Save State

* Save configuration only if changes were made
* Confirm:

  * Settings saved successfully
  * Counter state preserved
* Show a friendly exit message:
  "You can restart the tool anytime using the same configuration."

---

## 🧠 Development Rules (Non-Negotiable)

* Every input must have:

  * Explanation
  * Example
  * Validation
* Never assume technical knowledge
* Handle errors gracefully with helpful messages
* Keep the UI modular for future GUI or web expansion

---

### ✅ Expected Outcome

A complete, beginner-friendly interface that allows any user to:

* Configure the bot correctly
* Understand what each step does
* Use the tool confidently without documentation

Let's make it production ready I want that when a user will use this Python code They don't have work too much Think like they didn't install any dependencies yet I want that user have to just run it all the dependency will automatically installed and the program will run successfully without any type of effort from user side for the first time also.

