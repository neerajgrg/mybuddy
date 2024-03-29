# Define a simple text block template
simple_greeting_template = {
    "blocks": [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Get MyBuddy Up and Running!* :robot_face:\nTo configure, add these settings in your Slack Channel Description:"
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": "*Learning Mode*\nEnable or disable:\n`learning_mode: on/off`"
                },
                {
                    "type": "mrkdwn",
                    "text": "*Jira Integration*\nToggle Jira connection:\n`jira_integration: on/off`"
                },
                {
                    "type": "mrkdwn",
                    "text": "*Wiki Integration*\nActivate Wiki linkage:\n`wiki_integration: on/off`"
                },
            ]
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Just update these values to `on` or `off` as needed and then check again with `@test-slack-bot ready?`. :thumbsup:"
            }
        }
    ]
}



# Define a template with a button
button_template = {
    "type": "section",
    "text": {
        "type": "mrkdwn",
        "text": "Click the button below."
    },
    "accessory": {
        "type": "button",
        "text": {
            "type": "plain_text",
            "text": "Click Me"
        },
        "value": "click_me_123",
        "action_id": "button_click"
    }
}

processing_template = {
    "type": "section",
    "text": {
        "type": "mrkdwn",
        "text": "🔄 Processing your request... please hold on!"
    }
}



