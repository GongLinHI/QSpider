import requests
import random
import re
import time
import datetime
import js2py
from requests import Response
from bs4 import BeautifulSoup


# https://w.wjx.com/vm/rXz5Xu9.aspx
class QSpider(object):

    def __init__(self, shortId: str = ''):
        self.sessions = requests.session()
        self.shortId = shortId
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-GB;q=0.8,en;q=0.7,en-US;q=0.6',
            'Connection': 'keep-alive',
            'Sec-Ch-Ua': '"Microsoft Edge";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': r'"Windows"'
        }

    def _decode_id(self, input: int) -> int:
        context = js2py.EvalJs(enable_require=True)
        with open('js/DecodeId.js', 'r', encoding='utf8') as f:
            script = f.read()
        context.execute(script)
        return context.DecodeId(input)

    def _get_jqsign(self, jqnonce: str, ktimes: int):
        context = js2py.EvalJs(enable_require=True)
        with open('js/dataenc.js', 'r', encoding='utf8') as f:
            script = f.read()
        context.execute(script)
        return context.dataenc(jqnonce, ktimes)

    def _get_cookies(self) -> Response:
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Host': 'w.wjx.com',
        }
        response: Response = self.sessions.get(f'https://www.wjx.cn/vm/{self.shortId}.aspx', headers=self.headers,
                                               timeout=10)
        # 建议：每个问卷的答题时间为5-60s
        time.sleep(random.randrange(5, 30))
        return response

    def _get_all_params(self, response: Response):

        resp_content = response.content.decode()
        string = resp_content

        regex = r'var emUserName = "([^"]+)"'
        match = re.search(regex, string)
        if match:
            username = match.group(1)
        else:
            print("emUserName 未找到匹配的值。")

        # 完成payload
        finish_payload: dict[str, str | int] = {
            'source': 1,
            'weixin': 0,
            'vip': 0,
            'qtype': 1,
            'qw': 0,
            'name': username
        }
        # 提交答案payload
        soup: BeautifulSoup = BeautifulSoup(resp_content, 'html.parser')
        start_time: str = soup.find('input', attrs={'name': 'starttime'})['value']
        ktimes: int = random.randint(57, 143) + int(random.random() * 200)

        regex = r'var rndnum="([^"]+)"'
        match = re.search(regex, string)
        if match:
            rndnum = match.group(1)
        else:
            print("rndnum 未找到匹配的值。")

        regex = r'var jqnonce="([^"]+)"'
        match = re.search(regex, string)
        if match:
            jqnonce = match.group(1)
        else:
            print("jqnonce 未找到匹配的值。")

        jqsign = self._get_jqsign(jqnonce, ktimes)

        regex = r'var activityId =(\d+)'
        match = re.search(regex, string)
        if match:
            activity_num = match.group(1)
            activity_id = self._decode_id(activity_num)
        else:
            print("activityId 未找到匹配的值。")

        cst = int(time.time() * 1000)
        time.sleep(random.random())
        params = {
            'shortid': self.shortId,
            'starttime': start_time,
            'submittype': 1,
            'ktimes': ktimes,
            'hlv': 1,
            'rn': rndnum,
            'nw': 1,
            'jwt': 16,
            'jpm': 27,
            't': int(time.time() * 1000),
            'jqnonce': jqnonce,
            'jqsign': jqsign,
        }

        finish_payload.update({'APIVersion': '0.6.0', 'activity': activity_id})
        return params, activity_id, finish_payload

    def submit(self, submitdata: str = '') -> None:
        resp = self._get_cookies()
        params, activity_id, finish_payload = self._get_all_params(resp)

        # 1
        headers_1 = {'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                     'Host': 'sojump.cn-hangzhou.log.aliyuncs.com',
                     'Referer': 'https://w.wjx.com/', }.update(self.headers)

        payload_1 = {"APIVersion": "0.6.0", "a": activity_id, 'pd': submitdata, 'ua': self.headers['User-Agent']}
        self.sessions.get('https://sojump.cn-hangzhou.log.aliyuncs.com/logstores/activitypostdata/track.gif',
                          headers=headers_1, params=payload_1)
        # 2 POST
        headers_2 = {'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                     'Host': 'w.wjx.com',
                     'Origin': 'https://w.wjx.com/',
                     'Referer': f'https://w.wjx.com/vm/{self.shortId}.aspx',
                     'X-Requested-With': 'XMLHttpRequest'}.update(self.headers)
        res = self.sessions.post(r'https://w.wjx.com/joinnew/processjq.ashx', headers=headers_2, params=params,
                                 data={'submitdata': submitdata}, timeout=10)

        headers_3 = {'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                     'Host': 'image.wjx.cn',
                     'Referer': 'https://w.wjx.com/', }.update(self.headers)
        # 3 Wait GIF
        self.sessions.get('https://image.wjx.cn/images/wjxMobile/wait.gif', headers=headers_3, timeout=10)

        # 4
        payload_4 = {"APIVersion": "0.6.0", "a": activity_id, 'pd': res.content.decode(),
                     'ua': self.headers['User-Agent']}
        self.sessions.get('https://sojump.cn-hangzhou.log.aliyuncs.com/logstores/activitypostdata/track.gif',
                          headers=headers_1, params=payload_4, timeout=10)

        # 5 finish GET
        res2 = self.sessions.get('https://sojump.cn-hangzhou.log.aliyuncs.com/logstores/activityfinish/track.gif',
                                 headers=headers_1, params=finish_payload, timeout=10)

        out = f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] - 已提交 : {res2}"
        out = '\033[93m' + out + '\033[0m'
        print(out)
