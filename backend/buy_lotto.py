"""매주 목요일 자동 로또 + 연금복권 720+ 모든조 구매 + Discord 알림

GitHub Actions에서 실행. 환경변수:
  LOTTERY_USERNAME   동행복권 아이디
  LOTTERY_PASSWORD   동행복권 비밀번호
  DISCORD_WEBHOOK_URL  Discord 웹훅 URL
  TICKET_COUNT       구매 장수 (기본 5)
"""

import os
import sys
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

USERNAME = os.environ.get("LOTTERY_USERNAME", "")
PASSWORD = os.environ.get("LOTTERY_PASSWORD", "")
DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK_URL", "")
TICKET_COUNT = int(os.environ.get("TICKET_COUNT", "5"))
PENSION_COST = 5000  # 연금복권 모든조 = 1~5조 같은 번호 5매


def send_discord(message: str):
    if not DISCORD_WEBHOOK:
        print("Discord 웹훅 URL 없음 — 알림 스킵")
        return
    try:
        requests.post(DISCORD_WEBHOOK, json={"content": message}, timeout=10)
    except Exception as e:
        print(f"Discord 알림 실패: {e}")


def main():
    if not USERNAME or not PASSWORD:
        send_discord("❌ **로또 자동구매 실패**\n계정 정보가 설정되지 않았습니다.")
        sys.exit(1)

    try:
        from generator import LottoGenerator
        from client import DhlotteryClient

        # 통계 기반 번호 생성
        gen = LottoGenerator()
        tickets = [r["numbers"] for r in gen.generate(TICKET_COUNT)]

        # 로그인
        print("로그인 중...")
        c = DhlotteryClient(USERNAME, PASSWORD)

        # 잔액 확인
        balance = c.get_balance()
        available = balance["available"]
        needed = TICKET_COUNT * 1000 + PENSION_COST
        if available < needed:
            send_discord(
                f"⚠️ **로또 자동구매 취소 — 잔액 부족**\n"
                f"필요 금액: **{needed:,}원** / 현재 잔액: **{available:,}원** (부족: {needed - available:,}원)\n"
                f"👉 충전하기: https://www.dhlottery.co.kr/myPage.do?method=depositMoneyList"
            )
            print(f"잔액 부족: {available}원 / 필요 {needed}원")
            sys.exit(0)

        print(f"잔액 확인: {available:,}원 — 구매 진행")
        result = c.buy_lotto(tickets)
        remaining = c.get_balance()["available"]

    except Exception as e:
        send_discord(f"❌ **로또 자동구매 실패**\n```{e}```")
        print(f"오류: {e}")
        sys.exit(1)

    # Discord 메시지 구성
    round_no = result["round"]
    draw_date = result["draw_date"]
    bought = result["tickets"]

    lines = ["🎰 **로또 6/45 자동구매 완료**", ""]
    lines.append(f"📅 **{round_no}회** 추첨 ({draw_date})")
    lines.append("")
    lines.append("🎫 **구매 번호**")
    for t in bought:
        nums = " ".join(f"{int(n):02d}" for n in t["numbers"])
        lines.append(f"`{t['slot']}` {nums}  _{t['mode']}_")
    lines.append("")
    lines.append(f"💳 {len(bought)}게임 × 1,000원 = **{len(bought) * 1000:,}원**")
    lines.append(f"💰 구매 후 잔액: **{remaining:,}원**")

    msg = "\n".join(lines)
    send_discord(msg)
    print(msg)

    # 연금복권 720+ 모든조 — 로또 결과와 별도로 알림
    try:
        p = c.buy_pension(None)
        remaining = c.get_balance()["available"]
    except Exception as e:
        send_discord(f"❌ **연금복권 자동구매 실패**\n```{e}```")
        print(f"연금복권 오류: {e}")
        sys.exit(1)

    digits = "".join(str(d) for d in p["numbers"])
    msg = (
        f"🎟️ **연금복권 720+ 자동구매 완료**\n\n"
        f"📅 **{p['round']}회**\n"
        f"🔢 1~5조 **{digits}** (모든조)\n\n"
        f"💳 5매 × 1,000원 = **{PENSION_COST:,}원**\n"
        f"💰 구매 후 잔액: **{remaining:,}원**"
    )
    send_discord(msg)
    print(msg)


if __name__ == "__main__":
    main()
