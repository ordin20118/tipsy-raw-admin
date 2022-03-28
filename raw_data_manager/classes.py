from django.db import models
import math

class ContentInfo():
    CONTENT_TYPE_LIQUOR = 100
    CONTENT_TYPE_COCTAIL = 200
    CONTENT_TYPE_FLAG = 901

# 1001: 술 정보 등록
# 1002: 술 정보 수정
# 1003: 술 정보 제거(영구)
class JobInfo():
    JOB_ADD_SPIRITS = 1001
    JOB_MODIFY_SPIRITS = 1002
    JOB_REMOVE_SPIRITS = 1003

    JOBN_ADD_SPIRITS = "술 정보 등록"
    JOBN_MODIFY_SPIRITS = "술 정보 수정"
    JOBN_REMOVE_SPIRITS = "술 정보 제거(영구)"


class SearchParam(models.Model):
    
    STATE_SUCCESS = 0
    STATE_ERROR   = 1
	
    STATE_DUPLICATION = 10
    STATE_UNDEFINE = 11
    STATE_NO_DATA = 12
	
    STATE_SUCCESS_MESSAGE = "success"

    def __init__(self):
        self.list = None
        self.data = None
        self.paging = Paging()
        self.orderby = OrderBy()

class Paging(models.Model):

    DEF_PER_PAGE = 10

    def __init__(self, nowPage=1, totalCount=0, perPage=10):
        self.per_page = perPage
        self.now_page = nowPage
        self.total_count = totalCount
        self.page_range = 10
        self.makePages()


    def getLastRow(self):
        return self.per_page * self.now_page

    def getFirstRow(self):
        return self.per_page * self.now_page - self.per_page

    def getMaxPage(self):
        return int(math.ceil(self.total_count / (self.per_page * float(1))))

    def makePages(self):
        startPage = int((math.ceil(self.now_page/self.page_range)-1)*self.page_range)+1
        pages = []

        for i in range(0,self.page_range):
            pages.append(startPage)
            startPage += 1
            if startPage > self.getMaxPage():
                break
        self.pages = pages

    def getPages(self):
        return self.pages


class OrderBy(models.Model):

    SORT_ASC = "asc"
    SORT_DESC = "desc"

    def __init__(self, field=None):
        self.field = field
        self.sorting = self.SORT_DESC