import sys
import time
import requests
import json

class TelegramBot:
    def __init__(self, token):
        """Initialize the bot with your API token"""
        self.token = token
        self.api_url = f"https://api.telegram.org/bot{token}/"
        
    def get_updates(self, offset=None):
        """Get updates from Telegram"""
        url = self.api_url + "getUpdates"
        params = {'timeout': 100}
        if offset:
            params['offset'] = offset
        response = requests.get(url, params=params)
        return json.loads(response.content.decode('utf8'))
    
    def send_message(self, chat_id, text):
        """Send message to a specific chat"""
        url = self.api_url + "sendMessage"
        params = {'chat_id': chat_id, 'text': text}
        response = requests.post(url, params=params)
        return json.loads(response.content.decode('utf8'))
    
    def set_commands(self, commands):
        """Set commands for the bot"""
        url = self.api_url + "setMyCommands"
        params = {'commands': json.dumps(commands)}
        response = requests.post(url, params=params)
        return json.loads(response.content.decode('utf8'))

    def run(self):
        update_id = None
        while True:
            try:
                updates = self.get_updates(update_id)
                if updates.get("result"):
                    for update in updates["result"]:
                        update_id = update["update_id"] + 1
                        try:
                            message = update["message"]
                        except:
                            # Skip updates that don't have a message
                            continue
                        
                        chat_id = message["chat"]["id"]
                        if "text" in message:
                            text = message["text"]
                            print(f"Received: {text}")
                            
                            # Simple echo bot logic
                            if text.startswith('/start'):
                                self.send_message(chat_id, "Hello! I'm your Telegram bot.")
                            elif text.startswith('/chat_id'):
                                self.send_message(chat_id, f"This chat's id is {chat_id}")
                            else:
                                self.send_message(chat_id, f"You said: {text}")
                            
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(5)
            time.sleep(1)

if __name__ == "__main__":
    bot = TelegramBot(sys.argv[1])

    bot.run()