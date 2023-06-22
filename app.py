import os
import json
# Use the package we installed
from slack_bolt import App
from websockets.sync.client import connect

# Initializes your app with your bot token and signing secret
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

# Add functionality here
@app.event("app_home_opened")
def update_home_tab(client, event, logger):
  try:
    # views.publish is the method that your app uses to push a view to the Home tab
    client.views_publish(
      # the user that opened your app's app home
      user_id=event["user"],
      # the view object that appears in the app home
      view={
        "type": "home",
        "callback_id": "home_view",

        # body of the view
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "*Welcome to your _App's Home_* :rev-up-those-fryers:"
            }
          },
          {
            "type": "divider"
          },
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "This button won't do much for now but you can set up a listener for it using the `actions()` method and passing its unique `action_id`. See an example in the `examples` folder within your Bolt app."
            }
          },
          {
            "type": "actions",
            "elements": [
              {
                "type": "button",
                "text": {
                  "type": "plain_text",
                  "text": "Click me!"
                }
              }
            ]
          }
        ]
      }
    )

  except Exception as e:
    logger.error(f"Error publishing home tab: {e}")

@app.event("message")
def handle_message_events(body, logger):
    message_body = body["event"]["text"]
    channel_id = body["event"]["channel"]
    response = None

    try:
        viagpt_object = {
           "id": 1,
           "prompt": message_body
        }
        # Pass the user message to VIAGPT
        with connect("wss://hns-viagpt.dev.platform-services.dev1.poweredbyvia.com/viagpt/documentation") as websocket:
            websocket.send(json.dumps(viagpt_object))
            websocket_response = json.loads(websocket.recv())
            if websocket_response:
                response = websocket_response["spec"]

        # Call the conversations.list method using the WebClient
        app.client.chat_postMessage(
            channel = channel_id,
            text = response if response else message_body 
            # You could also use a blocks[] array to send richer content
        )
    except Exception as e:
        app.client.chat_postMessage(
            channel = channel_id,
            text = f"Error posting chat message: {e}"
            # You could also use a blocks[] array to send richer content
        )
        logger.error(f"Error posting chat message: {e}")

# Start your app
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))