from ..models import Article

class ArticleRepository:
    def get_all(self):
        return Article.objects.all()

    def get_by_id(self, article_id):
        return Article.objects.get(id=article_id)

    def create(self, title, content):
        return Article.objects.create(title=title, content=content)

    def update(self, article_id, title, content):
        article = self.get_by_id(article_id)
        article.title = title
        article.content = content
        article.save()
        return article

    def delete(self, article_id):
        article = self.get_by_id(article_id)
        article.delete()