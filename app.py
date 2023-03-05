import json

from flask import Flask
from flask import request
import openai
import requests

app_config = None

app = Flask(__name__)


def get_config(key):
    global app_config
    if not app_config:
        with open('config.json') as fd:
            app_config = json.load(fd)
            openai.api_key = app_config['api_key']
    return app_config[key]


def gpt_completion(content):
    response = openai.ChatCompletion.create(
        model=get_config('model'),
        messages=[
            {'role': 'system', 'content': get_config('bot_desc')},
            {'role': 'user', 'content': content}
        ],
        temperature=float(get_config('temperature')),
        top_p=float(get_config('top_p')),
        max_tokens=int(get_config('max_tokens'))
    )
    # print(response)
    choices = response.get('choices', None)
    model = response.get('model', 'N/A')
    usage = response.get('usage', None)

    if choices:
        choice = choices[0].get('message', {}).get('content', 'N/A')
    else:
        choice = 'N/A'
    if usage:
        total_token = usage.get('total_tokens', -1)
    else:
        total_token = -1

    return choice, model, total_token


def send_simple_text_to_ding(webhook_url, msg):
    if webhook_url and msg:
        body = {
            'msgtype': 'text',
            'text': {'content': msg}
        }
        requests.post(webhook_url, json=body)
    else:
        print('[send_simple_text_to_ding] `webhook_url` or `msg` is empty.')


def format_current_config():
    return '''
    model: %s
    bot_desc: %s
    temperature: %s
    top_p: %s
    max_tokens: %s
    ''' % (get_config('model'), get_config('bot_desc'), get_config('temperature'), get_config('top_p'),
           get_config('max_tokens'))


@app.route('/', methods=['GET', 'POST'])
def completion():
    gpt_result = gpt_completion(request.values.get('content', type=str))
    return gpt_result[0]


@app.route('/ding', methods=['POST'])
def ding_completion():
    request_body = request.json
    content = request_body.get('text', {}).get('content', '').strip()
    session_webhook = request_body.get('sessionWebhook', None)

    if content:
        if len(content) > get_config('max_tokens'):
            send_simple_text_to_ding(session_webhook, 'text is too long.')
        else:
            gpt_result = gpt_completion(content)
            send_simple_text_to_ding(session_webhook, gpt_result)
    else:
        send_simple_text_to_ding(session_webhook, format_current_config)


if __name__ == '__main__':
    app.run()
