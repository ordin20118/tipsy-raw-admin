from ..models import LiquorArticle

class LiquorArticleRepository:
    def find_all(self):
        return LiquorArticle.objects.all()

    def find_by_id(self, liquor_id, article_id):
        liquor_article = LiquorArticle.objects.filter(liquor_id=liquor_id, article_id=article_id).first()
        if not liquor_article:
            return None
        return liquor_article

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