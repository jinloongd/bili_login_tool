import datetime
import hashlib
import json
import time
import webbrowser
from urllib import parse
from urllib.parse import urlencode

import qrcode
import requests
from requests.adapters import HTTPAdapter, Retry
from requests.cookies import cookiejar_from_dict

APPKEY_TV = 'bca7e84c2d947ac6'
APPSEC_TV = '60698ba2f68e01ce44738920a0ffe768'

session = requests.session()
session.mount('https://', HTTPAdapter(max_retries=Retry(total=5)))
session.headers.update({
    "Connection": "keep-alive",
    "Referer": "https://www.bilibili.com/",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/63.0.3239.108",
})


def sign(params, appsec) -> str:
    return hashlib.md5(f"{params}{appsec}".encode()).hexdigest()


def is_login() -> (bool, str):
    resp = session.get(url='https://api.bilibili.com/x/web-interface/nav')
    return resp.json()['code'] == 0, resp.json()['data'].get('uname')


def get_auth_url_and_auth_code() -> (str, str):
    api_url = 'https://passport.bilibili.com/x/passport-tv-login/qrcode/auth_code'
    payload = {
        'appkey': APPKEY_TV,
        'local_id': '0',
        'ts': int(time.time())
    }
    resp = session.post(url=api_url,
                        data={**payload, 'sign': sign(params=urlencode(payload), appsec=APPSEC_TV)})
    if resp.json()['code'] != 0:
        raise Exception(resp.json())
    return resp.json()['data']['url'], resp.json()['data']['auth_code']


def verify_auth(auth_code):
    api_url = 'https://passport.bilibili.com/x/passport-tv-login/qrcode/poll'
    while True:
        payload = {
            'appkey': APPKEY_TV,
            'auth_code': auth_code,
            'local_id': 0,
            'ts': int(time.time())
        }
        resp = session.post(url=api_url,
                            data={**payload, 'sign': sign(params=urlencode(payload), appsec=APPSEC_TV)})
        resp_code = resp.json()['code']
        # 86039: 二维码尚未确认; 86090: 二维码已扫码未确认
        if resp_code == 86039 or resp_code == 86090:
            print(resp.json()['message'])
        elif resp_code == 0:
            # Success
            resp_data = resp.json()['data']
            uid = resp_data['mid']
            cookies = {c['name']: c['value'] for c in resp_data['cookie_info']['cookies']}
            session.cookies.update(cookiejar_from_dict(cookies))
            logined, uname = is_login()
            if logined:
                time_str = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                persistence_path = f'token_uid{uid}_{time_str}.json'
                with open(persistence_path, 'w') as f:
                    json.dump(resp_data, f, ensure_ascii=False, indent=2)
                print(f'登录成功: {uname}')
                print(f'Token已保存到: {persistence_path}')
                input("按下任意键退出...")
                break
            else:
                raise Exception("登录失败")
        else:
            raise Exception(resp.json())
        # sleep 3 secs before the next loop
        time.sleep(3)


# TV端扫码登录
def login_by_qrcode():
    # Step 1: request for auth url
    auth_url, auth_code = get_auth_url_and_auth_code()
    # Step 2: generate auth qrcode
    qr = qrcode.QRCode()
    qr.add_data(auth_url)
    qr.make()
    qr.print_ascii()
    # qrcode_terminal.draw(auth_url)
    content = parse.quote(auth_url, safe='')
    print("请扫码登录")
    print()
    print("如果无法扫描以上二维码，可在浏览器打开以下链接扫描：")
    print(f'https://api.jinloongd.com/v2/action/qrcode/generate?content={content}')
    # webbrowser.open(f'https://api.jinloongd.com/v2/action/qrcode/generate?content={content}', new=2)
    print()
    print("或将此链接复制到手机B站打开: ", auth_url)
    # Step 3:
    # waiting for auth accept
    print('Waiting for authoriazation...')
    verify_auth(auth_code)


if __name__ == '__main__':
    input("请最大化窗口，以确保二维码完整显示，按下任意键继续", )
    login_by_qrcode()
