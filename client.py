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
except ImportError:
    _RSA = None
    _PKCS = None

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
