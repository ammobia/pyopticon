import requests
import json
import time
from collections import defaultdict
from threading import Lock

class SlackHelper:
    """ This widget allows your Python code to send messages to a Slack webhook with duplicate message limiting.
    It's mainly useful for sending notifications after an interlock is tripped, e.g. if the dashboard 
    detects that an instrument went offline partway through an automation script.
    
    Rate limiting only applies to duplicate messages - different messages can be sent without restriction.
    Duplicate messages that exceed the rate limit will be dropped with a warning printed to console.
    
    :param webhook_url: The Webhook URL provided by Slack for sending a message to a channel.
    :type webhook_url: str
    :param dupes_per_minute: Maximum number of duplicate messages allowed per minute (default: 1)
    :type dupes_per_minute: int
    :param window_seconds: Time window for duplicate checking in seconds (default: 180)
    :type window_seconds: int
    """

    def __init__(self, webhook_url, dupes_per_minute=1, window_seconds=180):
        """The constructor for a SlackHelper object"""
        self.webhook_url = webhook_url
        self.dupes_per_minute = dupes_per_minute
        self.window_seconds = window_seconds
        
        # Dictionary to track message history: {message_body: [timestamp1, timestamp2, ...]}
        self.message_history = defaultdict(list)
        
        # Lock for thread safety
        self.lock = Lock()

    def _clean_old_messages(self, current_time):
        """Remove message timestamps that are outside the current time window"""
        cutoff_time = current_time - self.window_seconds
        
        # Create a list of messages to remove (to avoid modifying dict during iteration)
        messages_to_remove = []
        
        for message, timestamps in self.message_history.items():
            # Remove old timestamps for this message
            while timestamps and timestamps[0] < cutoff_time:
                timestamps.pop(0)
            
            # If no timestamps remain, mark message for removal
            if not timestamps:
                messages_to_remove.append(message)
        
        # Remove messages with no recent timestamps
        for message in messages_to_remove:
            del self.message_history[message]

    def send_message(self, message_body):
        """Send a Slack message to the webhook used when this helper was created.
        If the message is a duplicate and exceeds the rate limit, it will be dropped.
        Different messages are not rate-limited.
        
        :param message_body: The text of the message to send.
        :type message_body: str
        :return: True if message was sent, False if it was rate limited or failed
        :rtype: bool
        """
        with self.lock:
            current_time = time.time()
            
            # Clean up old message history
            self._clean_old_messages(current_time)
            
            # Check if this specific message is being sent too frequently
            if len(self.message_history[message_body]) >= self.dupes_per_minute:
                print(f"Duplicate message rate limit exceeded ({self.dupes_per_minute} per {self.window_seconds} seconds). Message dropped: {message_body[:50]}...")
                return False
            
            # Add current timestamp to message history
            self.message_history[message_body].append(current_time)
            
            try:
                payload = {"text": message_body}
                r = requests.post(self.webhook_url, json=payload)
                if r.status_code != 200:
                    print(f"Slack webhook failed with status code {r.status_code}")
                    return False
                return True
                
            except Exception as e:
                print("Slack webhook failed, error: " + str(e))
                return False
