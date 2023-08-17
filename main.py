import os
from typing import Annotated

import openai
from dotenv import load_dotenv
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from openai import InvalidRequestError
from mangum import Mangum

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY
app = FastAPI()
handler = Mangum(app)

templates = Jinja2Templates(directory='templates')
chat_log: list = [{
    'role': 'system',
    'content': 'You are a Python AI tutor. Provide clear answers for a beginner software developers.'
}]

chat_responses: list = []
image_url: str = ''


@app.get('/', response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse('home.html', {'request': request, 'chat_responses': chat_responses[::-1]})


@app.post('/', response_class=HTMLResponse)
async def chat_response(request: Request, user_chat_input: Annotated[str, Form()]):
    chat_log.append({'role': 'user', 'content': user_chat_input})
    chat_responses.append(user_chat_input)
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=chat_log,
        temperature=0.6
    )
    bot_response = response['choices'][0]['message']['content']
    chat_log.append({'role': 'assistant', 'content': bot_response})
    chat_responses.append(bot_response)
    return templates.TemplateResponse('home.html', {'request': request, 'chat_responses': chat_responses[::-1]})


@app.get('/image', response_class=HTMLResponse)
async def image_page(request: Request):
    return templates.TemplateResponse('image.html', {'request': request, 'image_url': image_url})


@app.post('/image', response_class=HTMLResponse)
async def image_response(request: Request, user_image_input: Annotated[str, Form()]):
    global image_url
    try:
        response = openai.Image.create(
            prompt=user_image_input,
            n=1,
            size="256x256"
        )
        image_url = response['data'][0]['url']
        msg = ''
    except InvalidRequestError as e:
        msg = str(e)
    return templates.TemplateResponse('image.html', {'request': request, 'image_url': image_url,
                                                     'user_image_input': user_image_input, 'msg': msg})
