import json

from flask import Flask
from flask import request
import openai

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


@app.route('/', methods=['GET', 'POST'])
def hello_world():
    gpt_result = gpt_completion(request.values.get("content", type=str))
    return gpt_result[0]


if __name__ == '__main__':
    app.run()
