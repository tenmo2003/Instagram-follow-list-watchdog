from getpass import getpass
import sys
import time
import os
import json
from datetime import datetime
from instagrapi import Client

from bot import TelegramBot


class InstagramFollowingTracker:
    def __init__(self, username, password, bot, target_username=None):
        """
        Initialize the Instagram following tracker.

        Args:
            username (str): Your Instagram username for login
            password (str): Your Instagram password for login
            target_username (str, optional): Username to track. If None, tracks the authenticated user.
        """
        self.username = username
        self.password = password
        self.target_username = target_username
        self.client = Client()
        self.bot = bot
        self.data_folder = "following_data"
        self.latest_file = os.path.join(self.data_folder, "latest_followings.json")
        self.history_file = os.path.join(self.data_folder, "following_history.json")

        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)

    def login(self):
        """Login to Instagram"""
        try:
            print(f"Logging in as {self.username}...")
            self.client.login(self.username, self.password)
            print("Login successful!")
            return True
        except Exception as e:
            print(f"Login failed: {e}")
            return False

    def get_user_id(self):
        """Get the user ID of the target account"""
        if self.target_username:
            user = self.client.user_info_by_username(self.target_username)
            return user.pk
        else:

            return self.client.user_id

    def get_followings(self):
        """Get the followings of the target account"""
        user_id = self.get_user_id()
        print(f"Fetching followings for user ID: {user_id}")

        followings = self.client.user_following(user_id, amount=0)

        following_usernames = [user.username for user in followings.values()]
        return following_usernames

    def save_followings(self, followings):
        """Save the current followings to a file"""
        timestamp = datetime.now().isoformat()
        data = {"timestamp": timestamp, "followings": followings}

        with open(self.latest_file, "w") as f:
            json.dump(data, f)

        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as f:
                history = json.load(f)
        else:
            history = []

        history.append(data)
        with open(self.history_file, "w") as f:
            json.dump(history, f)

        print(f"Saved {len(followings)} followings to {self.latest_file}")
        return True

    def load_previous_followings(self):
        """Load the previously saved followings"""
        if os.path.exists(self.latest_file):
            with open(self.latest_file, "r") as f:
                data = json.load(f)
            return data.get("followings", [])
        return []

    def compare_followings(self, current_followings):
        """Compare current followings with previous followings"""
        previous_followings = self.load_previous_followings()

        if not previous_followings:
            print("No previous following data found. This is the first run.")
            return None, None

        current_set = set(current_followings)
        previous_set = set(previous_followings)

        new_followings = list(current_set - previous_set)
        unfollowings = list(previous_set - current_set)

        return new_followings, unfollowings

    def track_changes(self):
        """Track changes in followings"""
        if not self.login():
            return False

        current_followings = self.get_followings()
        new_followings, unfollowings = self.compare_followings(current_followings)

        self.save_followings(current_followings)

        print(f"\nTotal followings: {len(current_followings)}")

        if new_followings is not None:
            new_following_str = "\n".join(new_followings)
            unfollowing_str = "\n".join(unfollowings)

            print(
                f"\n--- New followings ({len(new_followings)}) ---\n{new_following_str}"
            )
            print(f"\n--- Unfollowings ({len(unfollowings)}) ---\n{unfollowing_str}")

            bot.send_message(
                chat_id,
                f"--- Total followings: {len(current_followings)} ---\n\n"
                f"--- New followings ({len(new_followings)}) ---\n{new_following_str}\n\n"
                f"--- Unfollowings ({len(unfollowings)}) ---\n{unfollowing_str}",
            )

        return True

    def schedule_tracking(self, interval_hours=24):
        """Schedule regular tracking of followings"""
        print(
            f"Starting scheduled tracking every {interval_hours} hours. Press Ctrl+C to stop."
        )
        try:
            while True:
                print(
                    f"\n=== Tracking at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ==="
                )
                self.track_changes()
                print(f"Next check in {interval_hours} hours.")
                time.sleep(interval_hours * 3600)
        except KeyboardInterrupt:
            bot.send_message(
                chat_id, "Stopped tracking followings of user " + target_account
            )
            print("Tracking stopped.")


if __name__ == "__main__":
    username = input("Enter your Instagram username: ")
    password = getpass(prompt="Enter your Instagram password: ")
    target_account = input(
        "Enter the username of the account to track (leave blank to track yourself): "
    )

    bot_token = sys.argv[1]
    chat_id = sys.argv[2]
    check_interval = 12

    bot = TelegramBot(bot_token)


    tracker = InstagramFollowingTracker(username, password, bot, target_account)

    bot.send_message(
        chat_id=chat_id,
        text="Started tracking followings of user " + target_account,
    )

    tracker.schedule_tracking(check_interval)
