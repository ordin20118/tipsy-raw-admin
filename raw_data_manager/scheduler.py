import logging
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import register_events, DjangoJobStore
from apscheduler.triggers.cron import CronTrigger
from core.settings import TIME_ZONE
from raw_data_manager.view.rembg import get_and_process_queue

logger = logging.getLogger(__name__)

def rembg_job():
    get_and_process_queue()

def start():
    logger.info("[[ ### Scheduler Start ### ]]")
    scheduler = BackgroundScheduler(timezone=TIME_ZONE)
    scheduler.add_jobstore(DjangoJobStore(), "default") 

    scheduler.add_job(
        rembg_job,
        trigger=CronTrigger(second="*/10"),  # 10초마다 실행
        id="rembg",  # 고유 id
        max_instances=1,
        replace_existing=True,
    )
    logger.info("Added job 'rembg_job'.")

    # scheduler.add_job(
    #     my_job_b,
    #     trigger=CronTrigger(
    #         day_of_week="mon", hour="03", minute="00"
    #     ),  # 매주 월요일 3시에 실행
    #     id="my_job_b",
    #     max_instances=1,
    #     replace_existing=True,
    # )
    # print("Added job 'my_job_b'.")

    try:
        logger.info("Starting scheduler...")
        scheduler.start() 
    except KeyboardInterrupt:
        logger.info("Stopping scheduler...")
        scheduler.shutdown()
        logger.info("Scheduler shut down successfully!")