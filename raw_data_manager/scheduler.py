import logging
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import register_events, DjangoJobStore
from apscheduler.triggers.cron import CronTrigger
from core.settings import TIME_ZONE
from raw_data_manager.services.ai_service import AiService
from raw_data_manager.services.article_generation_service import ArticleGenerationService
from raw_data_manager.services.liquor_article_queue_service import SearchLiquorArticleQueueService
from raw_data_manager.views.rembg import get_and_process_queue

logger = logging.getLogger(__name__)

def rembg_process():
    get_and_process_queue()

def search_liquor_article_process():
    liquor_article_queue_service = SearchLiquorArticleQueueService()
    ai_service = AiService()
    queue = liquor_article_queue_service.get_standby_queue()
    if queue != None:
        ai_service.search_liquor_article_and_save(queue)

def make_liquor_content_process():
    article_gen_service = ArticleGenerationService()
    article_gen_service.process_batch()

def start():
    logger.info("[[ ### Scheduler Start ### ]]")
    scheduler = BackgroundScheduler(timezone=TIME_ZONE)
    scheduler.add_jobstore(DjangoJobStore(), "default") 

    scheduler.add_job(
        rembg_process,
        trigger=CronTrigger(second="*/5"),  # 10초마다 실행
        id="rembg",  # 고유 id
        max_instances=1,
        replace_existing=True,
    )
    logger.info("Added job 'rembg_job'.")

    scheduler.add_job(
        search_liquor_article_process,
        trigger=CronTrigger(second="*/5"),  # 10초마다 실행
        id="search_liquor_article",  # 고유 id
        max_instances=1,
        replace_existing=True,
    )
    logger.info("Added job 'search_liquor_article_job'.")

    scheduler.add_job(
        search_liquor_article_process,
        trigger=CronTrigger(second="*/5"),  # 10초마다 실행
        id="search_liquor_article",  # 고유 id
        max_instances=1,
        replace_existing=True,
    )
    logger.info("Added job 'search_liquor_article_job'.")

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