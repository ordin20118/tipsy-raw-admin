from ..repositories.article_repository import ArticleRepository

class ArticleService:
    def __init__(self):
        self.article_repo = ArticleRepository()

    def get_all_articles(self):
        return self.article_repo.get_all()

    def get_article_by_id(self, article_id):
        return self.article_repo.get_by_id(article_id)

    def create_article(self, title, content):
        return self.article_repo.create(title, content)

    def update_article(self, article_id, title, content):
        return self.article_repo.update(article_id, title, content)

    def delete_article(self, article_id):
        return self.article_repo.delete(article_id)
