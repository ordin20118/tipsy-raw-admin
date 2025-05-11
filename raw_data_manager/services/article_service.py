from raw_data_manager.forms import ArticleForm, ArticleTagForm
from raw_data_manager.repositories.liquor_article_repository import LiquorArticleRepository
from ..repositories.article_repository import ArticleRepository

import logging
logger = logging.getLogger('django')
class ArticleService:
    def __init__(self):
        self.article_repo = ArticleRepository()
        self.liquor_article_repo = LiquorArticleRepository()

    def get_all_articles(self):
        return self.article_repo.find_all()

    def get_article_by_id(self, article_id):
        return self.article_repo.find_by_id(article_id)
    
    def get_article_by_url(self, url):
        results = self.article_repo.find_by_url(url)
        logger.info(f"[검색된 URL 아티클]:{results}")
        if not results.exists():
            logger.info("[검색된게 없어서 None 반환]")
            return None
        logger.info("[검색된 아티클 반환]")
        for obj in results:
            logger.info(f"ID: {obj.id}, title: {obj.title}, url: {obj.url}")
        return results.first()

    def get_liquor_article_rel(self, liquor_id, article_id):
        return self.liquor_article_repo.find_by_id(liquor_id, article_id)

    # 대상 술에 대한 품질이 좋은 상위 아티클 조회
    def get_liquor_top_articles(self, liquor_id):
        return self.article_repo.find_liquor_best_articles(
            liquor_id=liquor_id,
            limit_rel_score=80,
            limit_article_score=80,
            limit_count=5
        )

    def create_article(self, data):
        #logger.info(f"create article// data=> {data}")
        article_form = ArticleForm(data)
        if article_form.is_valid():
            article = article_form.save(commit=True)
            # TODO: save tags
            tags = data['tags']
            if tags != None and len(tags) > 0:
                for tag in tags:
                    tag_data = {
                        'article': article,
                        'tag': tag
                    }
                    tag_form = ArticleTagForm(tag_data)
                    if tag_form.is_valid():
                        tag_form.save(commit=True)
            return article
        else:
            logger.info(f"invalidated article data: {article_form.errors}")
            return None

    def create_liquor_article_rel(self, liquor_id, article_id, relation_score):
        return self.liquor_article_repo.create(liquor_id, article_id, relation_score)

    def update_article(self, article_id, title, content):
        return self.article_repo.update(article_id, title, content)

    def delete_article(self, article_id):
        return self.article_repo.delete(article_id)
