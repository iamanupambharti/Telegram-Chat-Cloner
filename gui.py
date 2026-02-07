import subprocess
import sys
import os

def check_and_install_dependencies():
    """
    Checks for required dependencies and installs them if missing.
    Returns True if an installation was performed, False otherwise.
    """
    installed_something = False
    dependencies = {
        "customtkinter": "customtkinter",
        "telethon": "telethon"
    }
    
    for module, package in dependencies.items():
        try:
            __import__(module)
        except ImportError:
            print(f"ℹ️ {package} is not installed. Attempting to install...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✅ Successfully installed {package}.")
                installed_something = True
            except Exception as e:
                print(f"❌ Failed to install {package}: {e}")
                # If a crucial dependency fails, exit.
                sys.exit(1)
    
    return installed_something

# --- Main Application Logic ---

import customtkinter as ctk
import bot_backend
import threading
import asyncio
import queue

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Telegram Auto Forwarder")
        self.geometry("800x600")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Load config
        self.config = bot_backend.load_configuration()
        self.chats = []
        self.forwarding_thread = None

        # Placeholder for new asyncio thread management
        self.async_loop = None
        self.async_thread = None
        self.task_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self._start_async_thread()

        api_id = self.config.get("api_id")
        api_hash = self.config.get("api_hash")

        if api_id and api_hash:
            # Credentials exist, attempt auto-login and show main frame
            self.main_frame = MainApplicationFrame(self)
            self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
            self.run_async_task(
                self._async_auto_login(api_id, api_hash),
                callback=lambda client: self.main_frame.update_status("Auto-login successful."),
                error_callback=self._auto_login_failed
            )
        else:
            # No credentials, show login frame
            self.login_frame = LoginFrame(self, self.show_main_app)
            self.login_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

    async def _async_auto_login(self, api_id, api_hash):
        # These callbacks will raise an exception if telethon needs interactive input,
        # which is the desired behavior for a non-interactive auto-login.
        async def raise_exception_on_call(is_code=False):
            raise Exception("Auto-login requires a valid session. Please log out and log in again.")

        return await bot_backend.initialize_telegram_client(
            int(api_id),
            api_hash,
            on_phone_request=raise_exception_on_call,
            on_code_request=raise_exception_on_call,
            on_password_request=raise_exception_on_call
        )
    
    def _auto_login_failed(self, error):
        self.main_frame.update_status(f"Auto-login failed: {error}")
        self.main_frame.destroy()
        self.login_frame = LoginFrame(self, self.show_main_app)
        self.login_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.login_frame.status_label.configure(text=f"Auto-login failed. Please log in again.", text_color="red")

    def show_login_frame(self):
        if hasattr(self, 'main_frame') and self.main_frame.winfo_exists():
            self.main_frame.destroy()
        self.login_frame = LoginFrame(self, self.show_main_app)
        self.login_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")



    def _start_async_thread(self):
        self.async_thread = threading.Thread(target=self._run_async_loop, daemon=True)
        self.async_thread.start()
        # Start a periodic check for results from the async thread
        self.after(100, self._check_async_results)

    def _run_async_loop(self):
        self.async_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.async_loop)
        self.async_loop.run_forever()

    def _check_async_results(self):
        while not self.result_queue.empty():
            try:
                callback, args, kwargs = self.result_queue.get_nowait()
                callback(*args, **kwargs)
            except Exception as e:
                print(f"Error processing async result: {e}")
        self.after(100, self._check_async_results)

    def run_async_task(self, coro, callback=None, error_callback=None):
        future = asyncio.run_coroutine_threadsafe(coro, self.async_loop)

        def _on_done(f):
            try:
                result = f.result()
                if callback:
                    self.result_queue.put((callback, (result,), {}))
            except Exception as e:
                if error_callback:
                    self.result_queue.put((error_callback, (e,), {}))
                else:
                    print(f"Unhandled async task error: {e}")
        
        future.add_done_callback(_on_done)


    def show_main_app(self):
        self.login_frame.destroy()
        self.main_frame = MainApplicationFrame(self)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

    def on_closing(self):
        try:
            # Disconnect client first
            # The disconnect_client is an async function, needs to be run in the async loop
            self.run_async_task(bot_backend.disconnect_client())

            # Stop the async loop
            if self.async_loop and self.async_loop.is_running():
                self.async_loop.call_soon_threadsafe(self.async_loop.stop)
                if self.async_thread and self.async_thread.is_alive():
                    self.async_thread.join(timeout=5)
        except Exception as e:
            print(f"Error during graceful shutdown: {e}")
        self.destroy()

class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, on_success):
        super().__init__(parent)
        self.parent = parent
        self.on_success = on_success
        self.grid_columnconfigure(0, weight=1)
        self.label = ctk.CTkLabel(self, text="Telegram Login", font=("Arial", 20))
        self.label.grid(row=0, column=0, pady=20, padx=10)
        self.api_id_entry = ctk.CTkEntry(self, placeholder_text="API ID")
        self.api_id_entry.grid(row=1, column=0, pady=10, padx=10, sticky="ew")
        self.api_hash_entry = ctk.CTkEntry(self, placeholder_text="API Hash", show="*")
        self.api_hash_entry.grid(row=2, column=0, pady=10, padx=10, sticky="ew")
        self.login_button = ctk.CTkButton(self, text="Login", command=self.login)
        self.login_button.grid(row=3, column=0, pady=20, padx=10)
        self.status_label = ctk.CTkLabel(self, text="")
        self.status_label.grid(row=4, column=0, pady=10, padx=10)

    def login(self):
        api_id = self.api_id_entry.get()
        api_hash = self.api_hash_entry.get()
        if not api_id or not api_hash:
            self.status_label.configure(text="API ID and Hash are required.")
            return
        self.status_label.configure(text="Logging in...")
        self.login_button.configure(state="disabled")
        
        self.parent.run_async_task(
            self._async_login(api_id, api_hash),
            callback=self.login_success,
            error_callback=self.login_error
        )

    async def _async_login(self, api_id, api_hash):
        async def get_input_from_gui(prompt, title):
            future = asyncio.Future()
            # This runs on the main GUI thread via app.after(0, ...)
            def show_dialog():
                dialog = ctk.CTkInputDialog(text=prompt, title=title)
                user_input = dialog.get_input()
                self.parent.async_loop.call_soon_threadsafe(future.set_result, user_input)

            self.parent.after(0, show_dialog)
            # Wait for the result from the GUI thread
            return await future

        async def get_phone():
            return await get_input_from_gui("Enter your phone number:", "Phone Number")

        async def get_code():
            return await get_input_from_gui("Enter the code you received:", "Verification Code")

        async def get_password():
            return await get_input_from_gui("Enter your 2FA password:", "Password")

        # Save credentials to config for persistence
        self.parent.config['api_id'] = api_id
        self.parent.config['api_hash'] = api_hash
        bot_backend.save_configuration(self.parent.config)

        # Initialize the Telegram client
        await bot_backend.initialize_telegram_client(int(api_id), api_hash, get_phone, get_code, get_password)

    
    def login_success(self, client_obj):
        self.status_label.configure(text="Login Successful!", text_color="green")
        self.on_success()

    def login_error(self, error):
        self.status_label.configure(text=f"Login Failed: {error}", text_color="red")
        self.login_button.configure(state="normal")

class MainApplicationFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # === Mode Selection ===
        self.mode_label = ctk.CTkLabel(self, text="Forwarding Mode", font=("Arial", 16))
        self.mode_label.grid(row=0, column=0, columnspan=2, pady=10)
        self.mode_var = ctk.StringVar(value="1")
        self.original_mode_radio = ctk.CTkRadioButton(self, text="Original Caption", variable=self.mode_var, value="1", command=self.toggle_custom_caption_ui)
        self.original_mode_radio.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.custom_mode_radio = ctk.CTkRadioButton(self, text="Custom Caption", variable=self.mode_var, value="2", command=self.toggle_custom_caption_ui)
        self.custom_mode_radio.grid(row=1, column=1, padx=20, pady=10, sticky="w")

        # === Custom Caption Frame ===
        self.custom_caption_frame = ctk.CTkFrame(self)
        self.prefix_entry = ctk.CTkEntry(self.custom_caption_frame, placeholder_text="Caption Prefix")
        self.prefix_entry.pack(pady=10, padx=10, fill="x")
        self.prefix_entry.insert(0, self.parent.config.get("prefix", "Caption"))
        self.reset_counter_button = ctk.CTkButton(self.custom_caption_frame, text="Reset Counter", command=self.reset_counter)
        self.reset_counter_button.pack(pady=10, padx=10)
        
        # === Chats Frame ===
        self.chats_frame = ctk.CTkFrame(self)
        self.chats_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.chats_frame.grid_columnconfigure(0, weight=1)
        self.chats_frame.grid_columnconfigure(1, weight=1)
        self.fetch_chats_button = ctk.CTkButton(self.chats_frame, text="Fetch Chats", command=self.fetch_chats)
        self.fetch_chats_button.grid(row=0, column=0, columnspan=2, pady=10)
        self.source_chat_menu = ctk.CTkOptionMenu(self.chats_frame, values=["- Select Source -"], command=self.update_config)
        self.source_chat_menu.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.destination_chat_menu = ctk.CTkOptionMenu(self.chats_frame, values=["- Select Destination -"], command=self.update_config)
        self.destination_chat_menu.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # === Status & Control Frame ===
        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.control_frame.grid_columnconfigure(0, weight=1)
        self.start_button = ctk.CTkButton(self.control_frame, text="Start Forwarding", command=self.start_forwarding)
        self.start_button.grid(row=0, column=0, padx=5, pady=10)
        self.stop_button = ctk.CTkButton(self.control_frame, text="Stop Forwarding", state="disabled", command=self.stop_forwarding)
        self.stop_button.grid(row=0, column=1, padx=5, pady=10)
        self.logout_button = ctk.CTkButton(self.control_frame, text="Logout", command=self.logout)
        self.logout_button.grid(row=0, column=2, padx=5, pady=10)
        self.status_box = ctk.CTkTextbox(self.control_frame)
        self.status_box.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
        self.control_frame.grid_rowconfigure(1, weight=1)

        self.toggle_custom_caption_ui()

    def update_status(self, message):
        self.status_box.configure(state="normal")
        self.status_box.insert("end", message + "\n")
        self.status_box.yview_moveto(1.0)

    def toggle_custom_caption_ui(self):
        if self.mode_var.get() == "2":
            self.custom_caption_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
            self.chats_frame.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")
        else:
            self.custom_caption_frame.grid_remove()
            self.chats_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

    def fetch_chats(self):
        self.fetch_chats_button.configure(state="disabled", text="Fetching...")
        self.parent.run_async_task(
            self._async_fetch_chats(),
            callback=self.fetch_chats_success,
            error_callback=self.fetch_chats_error
        )

    async def _async_fetch_chats(self):
        return await bot_backend.get_chats()

    def fetch_chats_success(self, chats):
        self.parent.chats = chats
        chat_names = [chat['name'] for chat in chats]
        self.source_chat_menu.configure(values=chat_names)
        self.destination_chat_menu.configure(values=chat_names)
        self.fetch_chats_button.configure(state="normal", text="Fetch Chats")

    def fetch_chats_error(self, error):
        self.update_status(f"Error fetching chats: {error}")
        self.fetch_chats_button.configure(state="normal", text="Fetch Chats")

    def reset_counter(self):
        self.parent.config["count"] = 1
        bot_backend.save_configuration(self.parent.config)
        self.update_status("Counter reset to 1.")

    def update_config(self, _=None):
        pass

    def start_forwarding(self):
        src_name = self.source_chat_menu.get()
        dest_name = self.destination_chat_menu.get()

        if src_name == "- Select Source -" or dest_name == "- Select Destination -":
            self.update_status("Error: Please select both a source and a destination chat.")
            return
        if src_name == dest_name:
            self.update_status("Error: Source and destination chats cannot be the same.")
            return
            
        self.parent.config["source_name"] = src_name
        self.parent.config["source_channel"] = next(c['id'] for c in self.parent.chats if c['name'] == src_name)
        self.parent.config["destination_name"] = dest_name
        self.parent.config["destination_channel"] = next(c['id'] for c in self.parent.chats if c['name'] == dest_name)
        self.parent.config["prefix"] = self.prefix_entry.get()

        bot_backend.save_configuration(self.parent.config)
        self.update_status("Configuration saved.")

        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        
        self.parent.run_async_task(
            self._async_start_forwarding(),
            error_callback=lambda e: self.after(0, self.forwarding_error, e)
        )

    async def _async_start_forwarding(self):
        # The status_callback needs to post to the main thread for UI updates
        def gui_status_callback(msg):
            self.after(0, self.update_status, msg)
        
        try:
            await bot_backend.start_forwarding(self.parent.config, self.mode_var.get(), gui_status_callback)
        finally:
            self.after(0, self.forwarding_stopped)

    def forwarding_error(self, error):
        self.update_status(f"An error occurred during forwarding: {error}")
        self.forwarding_stopped()


    def stop_forwarding(self):
        self.update_status("Stopping forwarding...")
        self.stop_button.configure(state="disabled")
        self.parent.run_async_task(
            self._async_stop_forwarding(),
            error_callback=lambda e: self.after(0, self.update_status, f"Error stopping: {e}")
        )

    async def _async_stop_forwarding(self):
        await bot_backend.stop_forwarding()
        self.after(0, self.forwarding_stopped)

    def forwarding_stopped(self):
        self.update_status("Forwarding stopped.")
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")

    def logout(self):
        self.update_status("Logging out...")
        self.logout_button.configure(state="disabled")
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="disabled")
        self.parent.run_async_task(
            bot_backend.logout(),
            callback=self.handle_logout,
            error_callback=lambda e: self.update_status(f"Logout failed: {e}")
        )
    
    def handle_logout(self, _=None):
        self.parent.show_login_frame()


if __name__ == "__main__":
    if 'RELAUNCHED' not in os.environ:
        if check_and_install_dependencies():
            print("\n✅ Dependencies installed. Relaunching the application...")
            # Set an environment variable to prevent an infinite loop of relaunches
            os.environ['RELAUNCHED'] = 'true'
            os.execv(sys.executable, ['python'] + sys.argv)

    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()