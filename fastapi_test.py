# from functools import wraps
import asyncio
import datetime
import hashlib
import hmac
import json
import secrets
import sys
import time

import aiohttp

from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder

# import requests

# import threading

# import codecs

from pydantic import BaseModel

import uvicorn

i = 0

COLOR_MAGENTA = '\033[95m'
COLOR_GREEN = '\033[92m'
COLOR_BLUE = '\033[94m'
COLOR_RED = '\033[91m'
COLOR_YELLOW = '\033[93m'
COLOR_END = '\033[0m'
BOLD_START = '\033[1m'
BOLD_END = '\033[0m'

HMAC_ALGORITHM = 'HmacSHA256'
API_KEY = 'HDE57e65ff1960c11ed92a'
API_SECRET = '57e66018960c11ed92a802b67259d33a'


class Hyundai_EV_api:

    def __init__(self):
        return

    def make_header(self):

        headerDict = {}

        # 발급받은 apiKey 값
        key_ = API_KEY
        api_secret = API_SECRET

        # API 호출 일시 (yyyy-MM-dd:mm:ss.SSSX)
        timestamp_now = self.getTimeStamp()

        # 16 Byte 난수
        nonce_hex_ = secrets.token_hex(16)

        # 발급받은 api secret 조합
        signature_ = self.getSignature(
            key=api_secret, data=key_,
            timestamp=timestamp_now, nonce=nonce_hex_)

        # Authorization property
        Authorization_param = \
            'apiKey={0},ts={1},nonce={2},signature={3}'.format(
             key_, timestamp_now, nonce_hex_, signature_)
        Authorization_ = HMAC_ALGORITHM+' '+Authorization_param

        headerDict.setdefault('Authorization', Authorization_)
        headerDict.setdefault('apiKey', key_)
        headerDict.setdefault('ts', timestamp_now)
        headerDict.setdefault('nonce', nonce_hex_)
        headerDict.setdefault('signature', signature_)
        return headerDict

    def getHash_1(self, data, key):
        key_bytes = bytes.fromhex(key)
        data_bytes = bytes.fromhex(data)
        hash = hmac.new(
            key_bytes, msg=data_bytes, digestmod=hashlib.sha256).hexdigest()
        return hash

    def getHash_2(self, data, key):
        key_bytes = bytes.fromhex(key)
        data_bytes = bytes(data, 'utf-8')
        hash = hmac.new(
            key_bytes, msg=data_bytes, digestmod=hashlib.sha256).hexdigest()
        return hash

    def getSignature(self, data, key, timestamp, nonce):
        encryptedNonce = self.getHash_1(nonce, key)
        encryptedTimestamp = self.getHash_2(timestamp, encryptedNonce)
        signature = self.getHash_2(data, encryptedTimestamp)
        return signature

    def getTimeStamp(self):
        now = str(datetime.datetime.utcnow())
        time_zone = 'Z'  # UTC time
        timestamp = now[0:10]+'T'+now[11:23]+time_zone
        return timestamp


class Dummy(BaseModel):
    data: str


class GeneralCallBody(BaseModel):
    lineId: str
    callType: str
    sourceFloor: str
    direction: str
    destinationFloor: str
    elId: str


class RobotCallBody(BaseModel):
    lineId: str
    callType: str
    sourceFloor: str
    direction: str
    destinationFloor: str
    thingInfo: str


class EventPushRobotBody(BaseModel):
    messageId: str
    thingInfo: str
    lineId: str
    elId: str
    serviceStatus: str


class EventPushElBody(BaseModel):
    messageId: str
    lineId: str
    elId: str
    mode: str
    currentFloor: str
    direction: str
    doorStatus: str
    registedUpHallCall: str
    registedDnHallCall: str


class EventPushResponse(BaseModel):
    result: str


approved_ip_dict = {
    '13.125.50.47': 'api_server',
    '172.0.0.1': 'robot1',
    '127.0.0.1': 'localhost_ip',
    '223.171.146.77': 'G18-0009'

}

app = FastAPI()

hd = Hyundai_EV_api()

# base_url = 'http://127.0.0.1:8000'
base_url = 'http://13.125.50.47:8080'

robot_ip_dict = {}  # {messageId : robot_ip_addr}
robot_ip_doorhold_dict = {}  # {messageId : robot_ip_addr}


def get_call_function():
    return sys._getframe(7).f_code.co_name


def client_ip_check(ip_addr):
    return True if ip_addr in approved_ip_dict else False


async def async_sleep(t):
    await asyncio.sleep(t)


async def async_get(url):
    async with aiohttp.ClientSession(headers=hd.make_header()) as session:
        try:
            async with session.get(url) as response:
                json = await asyncio.wait_for(response.json(content_type=None),
                                              timeout=10)
                if response.status != 200:
                    print(COLOR_RED + 'GET ERROR API Status Code ' +
                          str(response.status) + ' /' + get_call_function() +
                          COLOR_END)
                return json
        except Exception as error: # noqa
            print(COLOR_RED + 'GET_ERROR / ' + str(error) + '/' +
                  get_call_function() + COLOR_END)
            return False


async def async_post(url, data):
    async with aiohttp.ClientSession(headers=hd.make_header()) as session:
        try:
            async with session.post(url, json=data) as response:
                json = await asyncio.wait_for(response.json(content_type=None),
                                              timeout=10)
                if response.status != 200:
                    print(COLOR_RED + 'POST ERROR API Status Code ' +
                          str(response.status) + ' /' + get_call_function() +
                          COLOR_END)
                return json
        except Exception as error: # noqa
            print(COLOR_RED + 'POST_ERROR / ' + str(error) + '/' +
                  get_call_function() + COLOR_END)
            return False


async def async_put(url):
    async with aiohttp.ClientSession(headers=hd.make_header()) as session:
        try:
            async with session.put(url) as response:
                json = await asyncio.wait_for(response.json(content_type=None), # noqa
                                              timeout=10)
                if response.status != 200:
                    print(COLOR_RED + 'PUT ERROR API Status Code ' +
                          str(response.status) + ' /' + get_call_function() +
                          COLOR_END)
                return
        except Exception as error: # noqa
            print(COLOR_RED + 'PUT_ERROR / ' + str(error) + '/' +
                  get_call_function() + COLOR_END)
            return False


async def async_delete(url):
    async with aiohttp.ClientSession(headers=hd.make_header()) as session:
        try:
            async with session.delete(url) as response:
                json = await asyncio.wait_for(response.json(content_type=None), # noqa
                                              timeout=10)
                if response.status != 200:
                    print(COLOR_RED + 'DELETE ERROR API Status Code ' +
                          str(response.status) + ' /' + get_call_function() +
                          COLOR_END)
                return
        except Exception as error: # noqa
            print(COLOR_RED + 'DELETE_ERROR / ' + str(error) + '/' +
                  get_call_function() + COLOR_END)
            return False


# def a():
#     text = 'a'
#     future = asyncio.run_coroutine_threadsafe(async_get(), loop)
#     future.add_done_callback(callback)


# @app.get('/test3')
# def test():
#     # params = request.get_json()
#     # print("받은 Json 데이터 ", params)
#     print('aa')
#     global i
#     a = 'test1/' + str(i)
#     # url = 'http://13.125.50.47:8080/api/v1/el/lineid/L00025754/status'
#     #header_ = hd.make_header()
#     # res = requests.get(url, headers = header_, timeout = 3)
#     result = asyncio.run(async_get())

#     response = {
#         # "result": "ok"
#         "result": result
#     }
#     i = i+1
#     if i>1000:
#         i = 0
#     #return jsonify(response)
#     return response


# @app.get('/testt')
# # async def testt():
# def testt():
#     #params = request.get_json()
#     #print("받은 Json 데이터 ", params)
#     print("bb")
#     global i
#     a = 'test2/' + str(i)

#     response = {
#         #"result": "ok"
#         "result": a
#     }
#     i = i+1
#     if i>1000:
#         i = 0
#     time.sleep(2)
#     #return jsonify(response)
#     return response


# 사이트 목록 조회
@app.get('/api/v1/app/site')
def get_site_list(request: Request):
    if not client_ip_check(request.client.host):
        raise HTTPException(status_code=403, detail='Access is Denied')
    url = base_url+'/api/v1/app/site'
    response = asyncio.run(async_get(url))
    return response


# 사이트 상세 조회
@app.get('/api/v1/app/site/{siteId}')
def get_site_detailed_info(request: Request, siteId):
    if not client_ip_check(request.client.host):
        raise HTTPException(status_code=403, detail='Access is Denied')
    url = base_url+'/api/v1/app/site/'+siteId
    response = asyncio.run(async_get(url))
    return response


# 라인 상세 조회
@app.get('/api/v1/app/line/{lineId}')
def get_line_detailed_info(request: Request, lineId):
    if not client_ip_check(request.client.host):
        raise HTTPException(status_code=403, detail='Access is Denied')
    url = base_url+'/api/v1/app/line/' + lineId
    response = asyncio.run(async_get(url))
    return response


# 원격 콜 요청
@app.post('/api/v1/el/call/general')
def general_call(request: Request, body: GeneralCallBody):
    if not client_ip_check(request.client.host):
        raise HTTPException(status_code=403, detail='Access is Denied')
    url = base_url+'/api/v1/el/call/general'
    request_body = jsonable_encoder(body)
    print(json.dumps(request_body, indent=4))
    response = asyncio.run(async_post(url, request_body))
    if 'messageId' in response:
        robot_ip_dict[response['messageId']] = request.client.host
        # add event push ip
    return response


# 사물 원격 콜 요청
@app.post('/api/v1/el/call/thing')
def robot_call(request: Request, body: RobotCallBody):
    if not client_ip_check(request.client.host):
        raise HTTPException(status_code=403, detail='Access is Denied')
    url = base_url+'/api/v1/el/call/thing'
    request_body = jsonable_encoder(body)
    print(json.dumps(request_body, indent=4))
    response = asyncio.run(async_post(url, request_body))
    if 'messageId' in response:
        robot_ip_dict[response['messageId']] = request.client.host
        # add event push ip
    return response


# 사물 원격 콜 요청(ST7 기종 전용)
@app.post('/api/v1/el/call/general/free')
def robot_st7_call(request: Request, body: GeneralCallBody):
    if not client_ip_check(request.client.host):
        raise HTTPException(status_code=403, detail='Access is Denied')
    url = base_url+'/api/v1/el/call/general/free'
    request_body = jsonable_encoder(body)
    # print(json.dumps(request_body, indent=4))
    response = asyncio.run(async_post(url, request_body))
    if 'messageId' in response:
        robot_ip_doorhold_dict[response['messageId']] = request.client.host
        # add event push ip
    return response


# 사물 원격 콜 취소
@app.delete('/api/v1/el/call/thing/messageid/{messageid}')
def delete_robot_call(request: Request, messageid):
    if not client_ip_check(request.client.host):
        raise HTTPException(status_code=403, detail='Access is Denied')
    url = base_url+'/api/v1/el/call/thing/messageid/'+messageid
    asyncio.run(async_delete(url))
    if messageid in robot_ip_dict:
        del robot_ip_dict[messageid]  # remove event push ip
    return

# EL 연동 상태 조회
@app.get('/api/v1/el/call/thing/messageid/{messageid}/status')
def get_robot_call_status(request: Request, messageid):
    if not client_ip_check(request.client.host):
        raise HTTPException(status_code=403, detail='Access is Denied')
    url = base_url + '/api/v1/el/call/thing/messageid/'+messageid+'/status'
    response = asyncio.run(async_get(url))
    return response


# 사물 연동 상태 전송
@app.put('/api/v1/el/call/thing/messageid/{messageid}/status/{status}')
def set_robot_call_status(request: Request, messageid, status):
    if not client_ip_check(request.client.host):
        raise HTTPException(status_code=403, detail='Access is Denied')
    url = base_url + '/api/v1/el/call/thing/messageid/' + messageid + \
        '/status/'+status
    asyncio.run(async_put(url))
    if messageid == 'destinationFloorGotOff' and messageid in robot_ip_dict:
        del robot_ip_dict[messageid]  # remove event push ip
    return


# 라인 운행 상태
@app.get('/api/v1/el/lineid/{lineid}/status')
def get_line_status(request: Request, lineid):
    if not client_ip_check(request.client.host):
        raise HTTPException(status_code=403, detail='Access is Denied')
    url = base_url + '/api/v1/el/lineid/'+lineid+'/status'
    response = asyncio.run(async_get(url))
    return response


# EL 운행 상태
@app.get('/api/v1/el/lineid/{lineid}/elid/{elid}/status')
def get_el_status(request: Request, lineid, elid):
    if client_ip_check(request.client.host):
        raise HTTPException(status_code=403, detail='Access is Denied')
    url = base_url + '/api/v1/el/lineid/'+lineid+'/elid/'+elid+'/status'
    response = asyncio.run(async_get(url))
    return response


# 라인 별 메시지 ID 조회
@app.get('/api/v1/el/call/thing/lineid/{lineid}/messageid')
def get_message_id(request: Request, lineid):
    if not client_ip_check(request.client.host):
        raise HTTPException(status_code=403, detail='Access is Denied')
    url = base_url + '/api/v1/el/call/thing/lineid/' + lineid + '/messageid'
    response = asyncio.run(async_get(url))
    return response


# 이벤트 푸쉬 서버, ROBOT 상태 이벤트
@app.post('/event_push/robot')
def event_push_robot(request: Request, body: EventPushRobotBody):
    if not client_ip_check(request.client.host):
        raise HTTPException(status_code=403, detail='Access is Denied')
    # url = 'http://127.0.0.1:8080/test'
    cnt = 0
    while body.messageId not in robot_ip_dict:
        time.sleep(0.01)
        cnt = cnt+1
        print('wait: ' + cnt)
        if cnt > 30:
            return EventPushResponse(result='fail')
    url = 'http://'+robot_ip_dict[body.messageId] + ':8675/event_push/robot'
    request_body = jsonable_encoder(body)
    print(json.dumps(request_body, indent=4))
    response = asyncio.run(async_post(url, request_body))
    print(json.dumps(jsonable_encoder(response), indent=4))
    return response


# 이벤트 푸쉬 서버, EL 도착 이벤트
@app.post('/event_push/el')
def event_push_el(request: Request, body: EventPushElBody):
    if not client_ip_check(request.client.host):
        raise HTTPException(status_code=403, detail='Access is Denied')
    # url = base_url+'/api/v1/el/call/thing'
    url = ''
    if body.messageId in robot_ip_doorhold_dict:
        url = 'http://'+robot_ip_doorhold_dict[body.messageId] + \
            ':8675/event_push/el'
        del robot_ip_doorhold_dict[body.messageId]
    elif body.messageId in robot_ip_dict:
        url = 'http://'+robot_ip_dict[body.messageId]+':8675/event_push/el'
    else:
        return EventPushResponse(result='fail')
    request_body = jsonable_encoder(body)
    response = asyncio.run(async_post(url, request_body))
    return response


@app.post('/test')
def get_line_statuss(request: Request, dummy: Dummy):
    print(dummy.json())
    client_host = request.client.host
    print('client_host: ' + client_host)
    url = base_url + '/testt'
    response = asyncio.run(async_get(url))
    return response


@app.get('/')
async def root():
    return {'message': 'Hello World'}


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
