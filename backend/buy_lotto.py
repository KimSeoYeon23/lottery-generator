"""매주 토요일 자동 로또 구매 + Discord 알림

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
        needed = TICKET_COUNT * 1000
        if available < needed:
            send_discord(
                f"⚠️ **로또 자동구매 취소 — 잔액 부족**\n"
                f"필요 금액: **{needed:,}원**\n"
                f"사용 가능 잔액: **{available:,}원**\n"
                f"부족분: **{needed - available:,}원**"
            )
            print(f"잔액 부족: {available}원 / 필요 {needed}원")
            sys.exit(0)

        print(f"잔액 확인: {available:,}원 — 구매 진행")
        result = c.buy_lotto(tickets)

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

    msg = "\n".join(lines)
    send_discord(msg)
    print(msg)


if __name__ == "__main__":
    main()
