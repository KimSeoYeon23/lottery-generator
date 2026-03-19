from django.apps import AppConfig


class LotteryConfig(AppConfig):
    name = "lottery"
    verbose_name = "Lottery Scheduler"

    def ready(self):
        import os
        # runserver 워커 프로세스에서만 실행 (reloader 제외)
        if os.environ.get("RUN_MAIN") != "true" and not os.environ.get("SCHEDULER_STARTED"):
            return

        os.environ["SCHEDULER_STARTED"] = "1"

        try:
            from apscheduler.schedulers.background import BackgroundScheduler
            from apscheduler.triggers.cron import CronTrigger
            import fetch_stats

            scheduler = BackgroundScheduler(timezone="Asia/Seoul")

            # 매주 토요일 밤 21:30 (추첨 후) 자동 업데이트
            scheduler.add_job(
                fetch_stats.run,
                CronTrigger(day_of_week="sat", hour=21, minute=30),
                id="fetch_lotto_stats",
                replace_existing=True,
            )

            scheduler.start()
            print("[Scheduler] 로또 통계 자동 업데이트 스케줄러 시작 (매주 토요일 21:30)")
        except Exception as e:
            print(f"[Scheduler] 시작 실패: {e}")
