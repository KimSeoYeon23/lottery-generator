"""동행복권 클라이언트 — 로그인, 구매, 잔액조회 (자체 구현)"""

import datetime
import json
import os
import getpass

try:
    import requests as _requests
except ImportError:
    _requests = None

try:
    from Crypto.PublicKey import RSA as _RSA
    from Crypto.Cipher import PKCS1_v1_5 as _PKCS
    from Crypto.Cipher import AES as _AES
    from Crypto.Protocol.KDF import PBKDF2 as _PBKDF2
    from Crypto.Hash import SHA256 as _SHA256
    from Crypto.Random import get_random_bytes as _get_random_bytes
    import base64 as _base64
except ImportError:
    _RSA = None
    _PKCS = None
    _AES = None

CREDENTIALS_PATH = os.path.expanduser("~/.lottery/credentials.json")


def check_deps():
    missing = []
    if _requests is None:
        missing.append("requests")
    if _RSA is None:
        missing.append("pycryptodome")
    return missing


def load_credentials():
    if os.path.exists(CREDENTIALS_PATH):
        with open(CREDENTIALS_PATH, "r") as f:
            return json.load(f)
    return None


def save_credentials(username, password):
    os.makedirs(os.path.dirname(CREDENTIALS_PATH), exist_ok=True)
    with open(CREDENTIALS_PATH, "w") as f:
        json.dump({"username": username, "password": password}, f)
    os.chmod(CREDENTIALS_PATH, 0o600)


class DhlotteryClient:
    BASE = "https://www.dhlottery.co.kr"
    OL = "https://ol.dhlottery.co.kr"

    def __init__(self, username, password):
        self._uid = username
        self._pwd = password
        self._session = _requests.Session()
        self._session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9",
        })
        self._login()

    def _rsa_encrypt(self, text, mod_hex, exp_hex):
        n, e = int(mod_hex, 16), int(exp_hex, 16)
        key = _RSA.construct((n, e))
        return _PKCS.new(key).encrypt(text.encode("utf-8")).hex()

    def _login(self):
        resp = self._session.get(f"{self.BASE}/", timeout=10)
        if "index_check.html" in resp.url:
            raise RuntimeError("동행복권 시스템 점검 중")

        self._session.get(f"{self.BASE}/login", timeout=10)

        rsa_resp = self._session.get(
            f"{self.BASE}/login/selectRsaModulus.do",
            headers={"Accept": "application/json",
                     "X-Requested-With": "XMLHttpRequest",
                     "Referer": f"{self.BASE}/login"},
            timeout=10,
        )
        rsa = rsa_resp.json()
        if "data" not in rsa:
            raise RuntimeError("RSA 키 획득 실패")

        mod = rsa["data"]["rsaModulus"]
        exp = rsa["data"]["publicExponent"]

        resp = self._session.post(
            f"{self.BASE}/login/securityLoginCheck.do",
            headers={"Content-Type": "application/x-www-form-urlencoded",
                     "Origin": self.BASE, "Referer": f"{self.BASE}/login"},
            data={"userId": self._rsa_encrypt(self._uid, mod, exp),
                  "userPswdEncn": self._rsa_encrypt(self._pwd, mod, exp),
                  "inpUserId": self._uid},
            timeout=10, allow_redirects=True,
        )
        if resp.status_code != 200 or "loginSuccess" not in resp.url:
            raise RuntimeError("로그인 실패 — 아이디/비밀번호 확인")

        self._session.get(f"{self.BASE}/main", timeout=10)
        self._session.get(f"{self.OL}/olotto/game/game645.do",
                          timeout=10, allow_redirects=True)

    def _get_round(self):
        first = datetime.date(2002, 12, 7)
        today = datetime.date.today()
        sat = today + datetime.timedelta(days=(5 - today.weekday()) % 7)
        return 1 + (sat - first).days // 7

    def buy_lotto(self, tickets):
        """tickets: [[1,2,3,4,5,6], ...] 최대 5장, 빈 리스트=자동"""
        tickets = tickets[:5]

        direct = json.loads(
            self._session.post(f"{self.OL}/olotto/game/egovUserReadySocket.json",
                               timeout=5).text
        )["ready_ip"]

        rnd = self._get_round()
        today = datetime.date.today()
        draw = today + datetime.timedelta(days=(5 - today.weekday()) % 7)
        limit = draw + datetime.timedelta(days=365)

        param = []
        for i, nums in enumerate(tickets):
            slot = "ABCDE"[i]
            if nums and len(nums) == 6:
                param.append({"genType": "1",
                              "arrGameChoiceNum": ",".join(str(n) for n in sorted(nums)),
                              "alpabet": slot})
            elif nums and 1 <= len(nums) <= 5:
                param.append({"genType": "2",
                              "arrGameChoiceNum": ",".join(str(n) for n in sorted(nums)),
                              "alpabet": slot})
            else:
                param.append({"genType": "0", "arrGameChoiceNum": None, "alpabet": slot})

        resp = self._session.post(
            f"{self.OL}/olotto/game/execBuy.do",
            headers={"Referer": f"{self.OL}/olotto/game/game645.do",
                     "Origin": self.OL},
            data={"round": str(rnd), "direct": direct,
                  "nBuyAmount": str(1000 * len(tickets)),
                  "param": json.dumps(param),
                  "ROUND_DRAW_DATE": draw.strftime("%Y/%m/%d"),
                  "WAMT_PAY_TLMT_END_DT": limit.strftime("%Y/%m/%d"),
                  "gameCnt": len(tickets), "saleMdaDcd": "10"},
            timeout=10,
        )
        result = json.loads(resp.text)

        if result.get("result", {}).get("resultCode") != "100":
            msg = result.get("result", {}).get("resultMsg", "알 수 없는 오류")
            raise RuntimeError(f"구매 실패: {msg}")

        mode_map = {"1": "수동", "2": "반자동", "3": "자동"}
        bought = []
        for line in result["result"]["arrGameChoiceNum"]:
            bought.append({
                "slot": line[0],
                "mode": mode_map.get(line[-1], "?"),
                "numbers": line[2:-1].split("|"),
            })
        return {"round": rnd, "draw_date": str(draw), "tickets": bought}

    # ── 연금복권 AES 암호화 ────────────────────────────────
    _BLOCK = 16
    _ITER  = 1000
    _pad   = lambda self, s: s + (16 - len(s) % 16) * chr(16 - len(s) % 16)
    _unpad = lambda self, s: s[:-ord(s[len(s)-1:])]

    def _enc(self, plaintext):
        salt = _get_random_bytes(32)
        iv   = _get_random_bytes(16)
        key  = _PBKDF2(self._pension_key(), salt, 16, count=self._ITER, hmac_hash_module=_SHA256)
        aes  = _AES.new(key, _AES.MODE_CBC, iv)
        enc  = aes.encrypt(self._pad(plaintext).encode('utf-8'))
        return salt.hex() + iv.hex() + _base64.b64encode(enc).decode()

    def _dec(self, enctext):
        salt = bytes.fromhex(enctext[0:64])
        iv   = bytes.fromhex(enctext[64:96])
        key  = _PBKDF2(self._pension_key(), salt, 16, count=self._ITER, hmac_hash_module=_SHA256)
        aes  = _AES.new(key, _AES.MODE_CBC, iv)
        raw  = self._unpad(aes.decrypt(_base64.b64decode(enctext[96:])))
        return raw.decode('utf-8', errors='replace')

    def _pension_round(self):
        try:
            resp = self._session.get(f"{self.BASE}/common.do?method=main", timeout=10)
            from bs4 import BeautifulSoup
            found = BeautifulSoup(resp.text, 'html.parser').find('strong', id='drwNo720')
            if found:
                return str(int(found.text) - 1)
        except Exception:
            pass
        # 폴백: 기준 회차 계산 (2024-12-26 = 244회)
        base = datetime.date(2024, 12, 26)
        today = datetime.date.today()
        days = (3 - today.weekday()) % 7
        next_thu = today + datetime.timedelta(days=days)
        return str(244 + (next_thu - base).days // 7 - 1)

    _EL = "https://el.dhlottery.co.kr"

    def _init_pension_session(self):
        """el.dhlottery.co.kr SSO 세션 초기화"""
        # www에서 el로 이동하는 링크를 통해 SSO 세션 수립
        self._session.get(f"{self.BASE}/gameInfo/win720Login.do", timeout=10, allow_redirects=True)
        self._session.get(f"{self._EL}/game/pension720/game.jsp", timeout=10, allow_redirects=True)

    def _pension_key(self):
        for c in self._session.cookies:
            if c.name == 'DHJSESSIONID':
                return c.value[:32]
        return self._session.cookies.get('JSESSIONID', '')[:32]

    def buy_pension(self, group, mock=False):
        """연금복권 720+ 자동 구매 (번호는 서버가 배정)
        group: int (1~5, 희망 조 — 서버가 무시할 수 있음)
        """
        import urllib.parse

        if not getattr(self, '_pension_session_ready', False):
            self._init_pension_session()
            self._pension_session_ready = True
        rnd = self._pension_round()
        sel_cls_no = str(group)

        headers = {
            "User-Agent": self._session.headers["User-Agent"],
            "Origin": self._EL,
            "Referer": f"{self._EL}/game/pension720/game.jsp",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
        }

        def post_enc(url, payload):
            data = {"q": urllib.parse.quote(self._enc(payload))}
            resp = self._session.post(url, headers=headers, data=data, timeout=10)
            try:
                outer = json.loads(resp.text)
            except Exception:
                raise RuntimeError(f"서버 응답 파싱 실패 ({url.split('/')[-1]}): {resp.text[:200]}")
            q_val = outer.get('q', '')
            if not q_val:
                raise RuntimeError(f"응답에 q 필드 없음 ({url.split('/')[-1]}): {resp.text[:200]}")
            return json.loads(self._dec(q_val))

        if mock:
            return {"round": int(rnd), "group": group, "numbers": [], "mock": True}

        # 1단계: makeAutoNo.do (서버가 번호 자동 배정)
        auto_payload = (
            f"ROUND={rnd}&round={rnd}&LT_EPSD={rnd}"
            f"&SEL_NO=&BUY_CNT=1&AUTO_SEL_SET=SA"
            f"&SEL_CLASS={sel_cls_no}&BUY_TYPE=A&ACCS_TYPE=01"
        )
        auto_res = post_enc(f"{self._EL}/makeAutoNo.do", auto_payload)
        if str(auto_res.get('resultCode', '')) != '100':
            raise RuntimeError(f"번호 생성 실패: {json.dumps(auto_res, ensure_ascii=False)}")

        actual_lot_no = auto_res.get('selLotNo', '')
        actual_cls_no = auto_res.get('sPReqClass', sel_cls_no)

        # 2단계: 주문번호 발급
        import time
        time.sleep(0.5)
        order_payload = (
            f"ROUND={rnd}&round={rnd}&LT_EPSD={rnd}"
            f"&AUTO_SEL_SET=SA&SEL_CLASS={actual_cls_no}&SEL_NO={actual_lot_no}"
            f"&BUY_TYPE=A&BUY_CNT=1"
        )
        order_res = post_enc(f"{self._EL}/makeOrderNo.do", order_payload)
        order_no   = order_res.get('orderNo', '')
        order_date = order_res.get('orderDate', '')
        # 항상 makeOrderNo 전체 응답을 로깅
        _order_debug = json.dumps(order_res, ensure_ascii=False)
        if not order_no:
            raise RuntimeError(f"주문번호 발급 실패: {_order_debug}")

        # 3단계: 실제 구매
        time.sleep(0.3)
        buy_no = f"1{actual_cls_no}{actual_lot_no}"
        conn_payload = (
            f"ROUND={rnd}&FLAG=&BUY_KIND=01&BUY_NO={buy_no}&BUY_CNT=1"
            f"&BUY_SET_TYPE=A&BUY_TYPE=A&CS_TYPE=01"
            f"&orderNo={urllib.parse.quote(order_no)}&orderDate={urllib.parse.quote(order_date)}"
            f"&TRANSACTION_ID=&WIN_DATE=&USER_ID={self._uid}&PAY_TYPE=01"
            f"&resultErrorCode=&resultErrorMsg=&resultOrderNo="
            f"&WORKING_FLAG=true&NUM_CHANGE_TYPE=&auto_process=N"
            f"&set_type=A&classnum={actual_cls_no}&selnum={actual_lot_no}&buytype=A"
            f"&num1=&num2=&num3=&num4=&num5=&num6="
            f"&DSEC=0&CLOSE_DATE=&verifyYN=N&curdeposit=&curpay=1000"
            f"&DROUND={rnd}&lotto720_radio_group=on"
        )
        conn_resp = self._session.post(
            f"{self._EL}/connPro.do",
            headers={**headers, "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"},
            data={"q": urllib.parse.quote(self._enc(conn_payload))},
            timeout=10,
            allow_redirects=False,
        )
        conn_text = conn_resp.text
        if not conn_text.strip().startswith('{'):
            raise RuntimeError(f"connPro HTML 응답 (orderNo={order_no}, orderDate={order_date}, buy_no={buy_no}): {conn_text[:200]}")
        outer = json.loads(conn_text)
        q_val = outer.get('q', '')
        result = json.loads(self._dec(q_val)) if q_val else outer

        result_inner = result.get('result', result)
        result_msg = str(result_inner.get('resultMsg', '')).upper()
        result_code = str(result_inner.get('resultCode', ''))
        if result_msg != 'SUCCESS' and result_code != '100':
            raise RuntimeError(f"구매 실패: {json.dumps(result, ensure_ascii=False)} | makeOrderNo: {_order_debug}")

        return {
            "round": int(rnd),
            "group": int(actual_cls_no),
            "numbers": [int(d) for d in str(actual_lot_no)],
        }

    def test_pension_format(self):
        """makeAutoNo.do만 호출 → selLotNo 포맷 확인 (구매 없음)"""
        self._init_pension_session()
        rnd = self._pension_round()
        payload = f"ROUND={rnd}&round={rnd}&LT_EPSD={rnd}&SEL_NO=&BUY_CNT=&AUTO_SEL_SET=SA&SEL_CLASS=&BUY_TYPE=A&ACCS_TYPE=01"
        import urllib.parse
        headers = {
            "User-Agent": self._session.headers["User-Agent"],
            "Origin": self._EL,
            "Referer": f"{self._EL}/game/pension720/game.jsp",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
        }
        data = {"q": urllib.parse.quote(self._enc(payload))}
        resp = self._session.post(f"{self._EL}/makeAutoNo.do", headers=headers, data=data, timeout=10)

        all_jsids = {
            f"{c.domain}{c.path}": c.value[:8] + "..."
            for c in self._session.cookies
            if c.name == 'JSESSIONID'
        }
        all_cookies = {
            f"{c.domain}::{c.name}": c.value[:8] + "..."
            for c in self._session.cookies
        }

        raw_q = json.loads(resp.text).get('q', '')

        # 가능한 키 후보 전부 시도
        candidates = {}
        for c in self._session.cookies:
            if c.name in ('JSESSIONID', 'DHJSESSIONID'):
                candidates[f"{c.domain}::{c.name}"] = c.value

        results = {}
        for label, val in candidates.items():
            try:
                key = val[:32]
                salt = bytes.fromhex(raw_q[0:64])
                iv   = bytes.fromhex(raw_q[64:96])
                dk   = _PBKDF2(key, salt, 16, count=self._ITER, hmac_hash_module=_SHA256)
                aes  = _AES.new(dk, _AES.MODE_CBC, iv)
                raw  = self._unpad(aes.decrypt(_base64.b64decode(raw_q[96:])))
                results[label] = raw.decode('utf-8', errors='replace')
            except Exception as e:
                results[label] = f'실패: {e}'

        return {
            "round": rnd,
            "key_attempts": results,
        }

    def get_balance(self):
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": f"{self.BASE}/mypage/home",
        }
        data = self._session.get(
            f"{self.BASE}/mypage/selectUserMndp.do",
            headers=headers, timeout=10,
        ).json().get("data", {}).get("userMndp", {})

        total = (
            ((data.get("pntDpstAmt", 0) or 0) - (data.get("pntTkmnyAmt", 0) or 0))
            + ((data.get("ncsblDpstAmt", 0) or 0) - (data.get("ncsblTkmnyAmt", 0) or 0))
            + ((data.get("csblDpstAmt", 0) or 0) - (data.get("csblTkmnyAmt", 0) or 0))
        )
        available = data.get("crntEntrsAmt", 0) or 0
        reserved = data.get("rsvtOrdrAmt", 0) or 0

        return {"total": total, "available": available,
                "reserved": reserved, "tickets": available // 1000}
