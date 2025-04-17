import customtkinter as ctk
from tkinter import messagebox
import json
import requests
import time
import threading
import random

RATE_LIMIT_INTERVAL = 1.2
RATE_LIMIT_WARNING_THRESHOLD = 1.0
REGIONS = [
    "brazil", "hongkong", "india", "japan", "rotterdam", "russia",
    "singapore", "south-korea", "southafrica", "sydney",
    "us-central", "us-east", "us-south", "us-west"
]


class DiscordTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Discord Group Disconnector")
        self.root.geometry("500x500")
        self.root.resizable(False, False)

        ctk.set_appearance_mode("dark")

        self.is_running = False

        self.token_entry = ctk.CTkEntry(root, placeholder_text="Discord Token", width=400)
        self.token_entry.pack(pady=10)

        self.group_id_entry = ctk.CTkEntry(root, placeholder_text="Group Id", width=400)
        self.group_id_entry.pack(pady=10)

        self.region_combobox = ctk.CTkComboBox(root, values=REGIONS, width=400)
        self.region_combobox.set("hongkong")
        self.region_combobox.pack(pady=10)

        self.mix_mode_var = ctk.BooleanVar()
        self.mix_mode_checkbox = ctk.CTkCheckBox(root, text="Activate Mix-Mode (Random Region)", variable=self.mix_mode_var)
        self.mix_mode_checkbox.pack(pady=10)

        self.interval_slider = ctk.CTkSlider(root, from_=0.1, to=5.0, number_of_steps=50, width=400, command=self.update_slider_label)
        self.interval_slider.set(RATE_LIMIT_INTERVAL)
        self.interval_slider.pack(pady=10)

        self.slider_label = ctk.CTkLabel(root, text=f"Interval: {RATE_LIMIT_INTERVAL:.1f} Seconds")
        self.slider_label.pack(pady=5)

        # Buttons
        self.start_button = ctk.CTkButton(root, text="Start Disconnecting", command=self.start_region_change)
        self.start_button.pack(pady=10)

        self.stop_button = ctk.CTkButton(root, text="Stop", command=self.stop_region_change, fg_color="red")
        self.stop_button.pack(pady=10)
        self.stop_button.pack_forget()  # Stop-Button zunächst ausblenden

        self.save_button = ctk.CTkButton(root, text="Save Token", command=self.save_token)
        self.save_button.pack(pady=10)

        self.load_button = ctk.CTkButton(root, text="Load Token", command=self.load_token)
        self.load_button.pack(pady=10)

        self.rate_limit_status = ctk.CTkLabel(root, text="Rate-Limit: Not Active", text_color="green")
        self.rate_limit_status.pack(pady=10)

    def update_slider_label(self, value):
        self.slider_label.configure(text=f"Interval: {float(value):.1f} Seconds")

    def save_token(self):
        token = self.token_entry.get()
        if token:
            with open("token.json", "w") as f:
                json.dump({"token": token}, f)
            messagebox.showinfo("Success", "Token Saved!")
        else:
            messagebox.showwarning("Error", "Input your Token!")

    def load_token(self):
        try:
            with open("token.json", "r") as f:
                data = json.load(f)
                self.token_entry.delete(0, "end")
                self.token_entry.insert(0, data["token"])
            messagebox.showinfo("Success", "Token loaded!")
        except FileNotFoundError:
            messagebox.showwarning("Error", "No saved tokens found!")

    def change_region(self, group_id, token, interval, region=None):
        url = f"https://discord.com/api/v9/channels/{group_id}/call"
        headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }
        self.is_running = True

        while self.is_running:
            try:
                if self.mix_mode_var.get():
                    region = random.choice(REGIONS)

                data = {"region": region}
                response = requests.patch(url, headers=headers, json=data)
                if response.status_code == 200:
                    print(f"Region changed to: {region}.")
                elif response.status_code == 429:
                    self.rate_limit_status.configure(text="Rate-Limit: Active!", text_color="red")
                    retry_after = response.json().get("retry_after", 1.0)
                    time.sleep(retry_after)
                else:
                    print(f"Error: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"Error: {e}")

            time.sleep(interval)

    def start_region_change(self):
        group_id = self.group_id_entry.get()
        token = self.token_entry.get()
        interval = self.interval_slider.get()
        region = self.region_combobox.get()

        if not group_id or not token:
            messagebox.showwarning("Error", "Type in Group Id and Token")
            return

        self.rate_limit_status.configure(text="Rate-Limit: Not Active", text_color="green")
        self.stop_button.pack(pady=10)

        threading.Thread(
            target=self.change_region, args=(group_id, token, interval, region), daemon=True
        ).start()

    def stop_region_change(self):
        self.is_running = False
        self.rate_limit_status.configure(text="Rate-Limit: Not Active", text_color="green")
        self.stop_button.pack_forget()
        print("Disconnecting Stopped!")


if __name__ == "__main__":
    root = ctk.CTk()
    app = DiscordTool(root)
    root.mainloop()
