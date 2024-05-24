import requests
import random
import re
import time
import datetime
import js2py
from requests import Response
from bs4 import BeautifulSoup
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor

from AnswerGenerator import AnswerGeneratorType


# https://w.wjx.com/vm/rXz5Xu9.aspx
class QSpider(object):

    def __init__(self, shortId: str = '', *, proxies: dict = None):
        if not isinstance(shortId, str):
            raise TypeError(f'shortId - Expect str but get {type(shortId)}')
        self.shortId = shortId

        self._session = requests.session()
        if proxies is not None and len(proxies) != 0:
            self._session.proxies = proxies

        self._const_values = {
            'source': 1,
            'weixin': 0,
            'vip': 0,
            'qtype': 1,
            'qw': 0,
            'submittype': 1,
            'hlv': 1,
            'nw': 1,
            'jwt': 4,
            'jpm': 52,
            'ge': 2
        }
        self._headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-GB;q=0.8,en;q=0.7,en-US;q=0.6',
            'Connection': 'keep-alive',
            'Sec-Ch-Ua': '"Microsoft Edge";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': r'"Windows"',
        }
        self._request_timeout = 10.0
        self._finish_time_limit_lower_bound = 10
        self._finish_time_limit_upper_bound = 40
        self._sleep_time_limit_lower_bound = 300
        self._sleep_time_limit_upper_bound = 1500

    def get_finish_time_limit(self, *args):
        if not args:
            return self._finish_time_limit_lower_bound, self._finish_time_limit_upper_bound
        if args[0] in (0, 'lb'):
            return self._finish_time_limit_lower_bound
        elif args[0] in (1, 'ub'):
            return self._finish_time_limit_upper_bound

    def set_finish_time_limit(self, lower_bound=5, upper_bound=45):
        self._finish_time_limit_lower_bound = lower_bound
        self._finish_time_limit_upper_bound = upper_bound

    def get_sleep_time_limit(self, *args):
        if not args:
            return self._sleep_time_limit_lower_bound, self._sleep_time_limit_upper_bound
        if args[0] in (0, 'lb'):
            return self._sleep_time_limit_lower_bound
        elif args[0] in (1, 'ub'):
            return self._sleep_time_limit_upper_bound

    def set_sleep_time_limit(self, lower_bound=5, upper_bound=45):
        self._sleep_time_limit_lower_bound = lower_bound
        self._sleep_time_limit_upper_bound = upper_bound

    def _message(self, message: str):
        message = f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] <{self.shortId}> - {message}"
        out = '\033[93m' + message + '\033[0m'
        print(out)

    def clear_proxies(self):
        self._session.proxies.clear()

    def set_proxies(self, proxies: dict = None):
        if proxies is None:
            self.clear_proxies()
        elif len(proxies) != 0:
            self._session.proxies = proxies
        return True

    def get_request_timeout(self, t: float):
        self._request_timeout = t

    def get_proxies(self):
        return self._session.proxies

    def _decode_id(self, i: int) -> int:
        context = js2py.EvalJs(enable_require=True)
        with open('js/DecodeId.js', 'r', encoding='utf8') as f:
            script = f.read()
        context.execute(script)
        return context.DecodeId(i)

    def _get_jqsign(self, jqnonce: str, ktimes: int):
        context = js2py.EvalJs(enable_require=True)
        with open('js/dataenc.js', 'r', encoding='utf8') as f:
            script = f.read()
        context.execute(script)
        return context.dataenc(jqnonce, ktimes)

    def _encodeURIComponent(self, context: str):
        return quote(context)

    def _get_cookies(self) -> Response:
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Host': 'w.wjx.com',
        }
        response: Response = self._session.get(f'https://www.wjx.cn/vm/{self.shortId}.aspx', headers=self._headers,
                                               timeout=self._request_timeout)

        return response

    def _get_all_params(self, response: Response):

        resp_content = response.content.decode()
        string = resp_content
        if '已暂停' in string:
            self._message('很抱歉，此问卷已暂停，不能填写！')
            exit(-1)
        if '停止状态' in string:
            self._message('此问卷处于停止状态，仅供浏览，请勿填写！')
            exit(-2)

        time.sleep(random.uniform(self._finish_time_limit_lower_bound, self._finish_time_limit_upper_bound))

        regex = r'var emUserName = "([^"]+)"'
        match = re.search(regex, string)
        if match:
            username = match.group(1)
        else:
            print("emUserName 未找到匹配的值。")

        # 完成payload
        finish_payload: dict[str, str | int] = {
            'source': self._const_values['source'],
            'weixin': self._const_values['weixin'],
            'vip': self._const_values['vip'],
            'qtype': self._const_values['qtype'],
            'qw': self._const_values['qw'],
            'name': username
        }
        # 提交答案payload
        soup: BeautifulSoup = BeautifulSoup(resp_content, 'html.parser')
        start_time: str = soup.find('input', attrs={'name': 'starttime'})['value']
        ktimes: int = random.randint(1, 100) + int(random.random() * 100)

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
        # time.sleep(random.random())
        time.sleep(ktimes / 1000 * 1.1)
        params = {
            'shortid': self.shortId,
            'starttime': start_time,
            'submittype': self._const_values['submittype'],
            'ktimes': ktimes,
            'hlv': self._const_values['hlv'],
            'rn': rndnum,
            'nw': self._const_values['nw'],
            'jwt': self._const_values['jwt'],
            'jpm': self._const_values['jpm'],
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
                     'Referer': 'https://w.wjx.com/', }.update(self._headers)

        payload_1 = {"APIVersion": "0.6.0", "a": activity_id, 'pd': submitdata, 'ua': self._headers['User-Agent']}
        self._session.get('https://sojump.cn-hangzhou.log.aliyuncs.com/logstores/activitypostdata/track.gif',
                          headers=headers_1, params=payload_1, timeout=self._request_timeout)
        # 2 POST
        headers_2 = {'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                     'Host': 'w.wjx.com',
                     'Origin': 'https://w.wjx.com/',
                     'Referer': f'https://w.wjx.com/vm/{self.shortId}.aspx',
                     'X-Requested-With': 'XMLHttpRequest'}.update(self._headers)
        res = self._session.post(r'https://w.wjx.com/joinnew/processjq.ashx', headers=headers_2, params=params,
                                 data={'submitdata': submitdata}, timeout=self._request_timeout)
        # print(res.content.decode())

        headers_3 = {'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                     'Host': 'image.wjx.cn',
                     'Referer': 'https://w.wjx.com/', }.update(self._headers)
        # 3 Wait GIF
        self._session.get('https://image.wjx.cn/images/wjxMobile/wait.gif', headers=headers_3,
                          timeout=self._request_timeout)

        # 4
        payload_4 = {"APIVersion": "0.6.0", "a": activity_id, 'pd': res.content.decode(),
                     'ua': self._headers['User-Agent']}
        self._session.get('https://sojump.cn-hangzhou.log.aliyuncs.com/logstores/activitypostdata/track.gif',
                          headers=headers_1, params=payload_4, timeout=self._request_timeout)

        # 5 finish GET
        res2 = self._session.get('https://sojump.cn-hangzhou.log.aliyuncs.com/logstores/activityfinish/track.gif',
                                 headers=headers_1, params=finish_payload, timeout=self._request_timeout)

        # 6 completemobile2.aspx
        state_code, message = res.content.decode().split('〒')
        state_code = int(state_code)
        if state_code != 10:  # 有异常
            self._message(f'提交异常 : {message}')
            return state_code

        message: str = message.replace("complete.aspx", "completemobile2.aspx").replace("?q=", "?activity=").replace(
            "&joinid=", "&joinactivity=").replace("&JoinID=", "&joinactivity=")
        payload_6 = {'ge': self._const_values['ge'], 'nw': self._const_values['nw'], 'jpm': self._const_values['jpm']}
        _url, message = message.split('?')
        for param_string in message.split('&'):
            key, value = param_string.split('=')
            payload_6[key] = value

        self._session.get('https://www.wjx.cn/' + _url, params=payload_6, timeout=self._request_timeout)

        self._message(f"已提交 : {payload_6['comsign']}")
        return state_code

    def run(self, answer_generator: AnswerGeneratorType, total_num: int):

        def task(thread_index: int = 0, count: int = 0):
            gen: AnswerGeneratorType = answer_generator()
            for i in range(1, 1 + count):
                data: str = gen.generate()
                if workers > 1:
                    time.sleep(random.uniform(thread_index, thread_index * 1.2))
                if workers > 1:
                    print(f'{thread_index} - {i} : {data}')
                elif workers == 1:
                    print(f'{i} : {data}')
                while QSpider(self.shortId).submit(data) != 10:
                    time.sleep(random.uniform(self._sleep_time_limit_lower_bound, self._sleep_time_limit_upper_bound))
            return count

        workers = 2
        if workers >= 1:
            with ThreadPoolExecutor(max_workers=workers) as pool:
                futures = []
                for i in range(1, workers + 1):
                    f = pool.submit(task, i, (total_num // workers))
                    futures.append(f)
        elif workers <= 0:
            pass
