from ..models import LiquorContent

class LiquorContentRepository:
    def find_all(self):
        return LiquorContent.objects.all()

    def find_by_id(self, id):
        return LiquorContent.objects.get(id=id)

    def find_by_url(self, url):
        return LiquorContent.objects.filter(url=url)

    def create(self, title, content, ):
        return LiquorContent.objects.create(title=title, content=content)

    def update(self, id, title, content):
        content = self.get_by_id(id)
        content.title = title
        content.content = content
        content.save()
        return content

    def delete(self, id):
        content = self.get_by_id(id)
        content.delete()

    def delete_by_liquor_id(self, liquor_id):
        return LiquorContent.objects.filter(liquor_id=liquor_id).delete()