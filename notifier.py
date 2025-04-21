import os
from dotenv import load_dotenv
from slack_sdk import WebClient
from twilio.rest import Client
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
    

load_dotenv()




def get_slack_user_id(username: str, client) -> str:
    """
    Fetch Slack user ID from a username like '@adesoji'.
    """
    try:
        response = client.users_list()
        for user in response["members"]:
            if not user.get("deleted") and user["name"] == username.lstrip("@"):
                return user["id"]
        raise ValueError(f"User {username} not found on Slack.")
    except Exception as e:
        raise ValueError(f"Error fetching user ID for {username}: {e}")


def send_slack_message(message: str, fallback_user: str = None):
   

    client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))

    channel = os.getenv("SLACK_CHANNEL", "#general")

    try:
        response = client.chat_postMessage(channel=channel, text=message)
        print(f"✅ Slack message sent to {channel}: {response['ts']}")
    except SlackApiError as e:
        print(f"⚠️ Failed to send to channel {channel}: {e.response['error']}")
        if fallback_user:
            try:
                user_id = get_slack_user_id(fallback_user, client)
                response = client.chat_postMessage(channel=user_id, text=f"DM fallback: {message}")
                print(f"✅ DM sent to {fallback_user}: {response['ts']}")
            except Exception as ex:
                print(f"❌ DM fallback failed: {str(ex)}")

def send_whatsapp_message(body: str):

    client = Client(os.getenv("TWILIO_SID"), os.getenv("TWILIO_AUTH"))
    message = client.messages.create(
        body=body,
        from_="whatsapp:+14155238886",  # Twilio sandbox number
        to=os.getenv("WHATSAPP_TO")
    )
    print(f"✅ WhatsApp message sent: SID = {message.sid}")
