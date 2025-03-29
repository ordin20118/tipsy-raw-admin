from ..models import LiquorArticle

class LiquorArticleRepository:
    def get_all(self):
        return LiquorArticle.objects.all()

    def get_by_id(self, article_id):
        return LiquorArticle.objects.get(id=article_id)

    def create(self, liquor_id, article_id, relation_score):
        return LiquorArticle.objects.create(
            liquor_id=liquor_id,
            article_id=article_id,
            relation_score=relation_score
        )

    def update(self, article_id, liquor_id, relation_score):
        article = self.get_by_id(article_id)
        article.liquor_id = liquor_id
        article.relation_score = relation_score
        article.save()
        return article

    def delete(self, article_id):
        article = self.get_by_id(article_id)
        article.delete()
        return article