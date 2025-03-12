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