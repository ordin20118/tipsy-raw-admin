from ..models import Article, LiquorArticle
from django.db.models import F

class ArticleRepository:
    def find_all(self):
        return Article.objects.all()

    def find_by_id(self, article_id):
        return Article.objects.get(id=article_id)

    def find_by_url(self, url):
        return Article.objects.filter(url=url)

    # 대상 술에 대한 품질이 좋은 상위 아티클 조회 
    def find_liquor_best_articles(self, liquor_id, limit_rel_score, limit_article_score, limit_count):
        # article_ids = LiquorArticle.objects.select_related('article') \
        # .filter(
        #     liquor=liquor_id,
        #     article__score__gte=limit_article_score,
        #     relation_score__gte=limit_rel_score
        # ) \
        # .order_by('article__score', '-relation_score')[:limit_count] \
        # .values_list('article_id', flat=True)
        
        # return Article.objects.filter(id__in=article_ids)

        return Article.objects.filter(
            score__gte=limit_article_score,
            liquorarticle__liquor=liquor_id,
            liquorarticle__relation_score__gte=limit_rel_score
        ).annotate(
            relation_score=F('liquorarticle__relation_score')
        ).order_by('-score', '-relation_score')[:limit_count]


    def create(self, title, content, ):
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