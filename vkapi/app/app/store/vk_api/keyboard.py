keyboard_close = {
    "buttons": [],
    "one_time": True
}
keyboard_game_start = {
    "buttons": [
        [
            {
                "action": {
                    "type": "text",
                    "payload": "{\"command\": \"start_game\"}",
                    "label": "Старт"
                },
                "color": "positive"
            },
            {
                "action": {
                    "type": "callback",
                    "payload": "{\"command\": \"info_game\"}",
                    "label": "Инфо"
                },
                "color": "secondary"
            }
        ]
    ]
}
keyboard_game_join = {
    "buttons": [
        [
            {
                "action": {
                    "type": "text",
                    "payload": "{\"command\": \"join_game\"}",
                    "label": "Присоединиться"
                },
                "color": "primary"
            },
            {
                "action": {
                    "type": "callback",
                    "payload": "{\"command\": \"info_game\"}",
                    "label": "Инфо"
                },
                "color": "secondary"
            }
        ]
    ]
}
keyboard_game_stop = {
    "buttons": [
        [
            {
                "action": {
                    "type": "text",
                    "payload": "{\"command\": \"stop_game\"}",
                    "label": "Стоп"
                },
                "color": "negative"
            },
            {
                "action": {
                    "type": "callback",
                    "payload": "{\"command\": \"info_game\"}",
                    "label": "Инфо"
                },
                "color": "secondary"
            }
        ]
    ]
}
keyboard_responder = {
    "buttons": [
        [
            {
                "action": {
                    "type": "text",
                    "payload": "{\"command\": \"responder\"}",
                    "label": "Ответить"
                },
                "color": "positive"
            }
        ]
    ]
}