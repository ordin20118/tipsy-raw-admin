from django.db import models
import math

class ContentInfo():
    CONTENT_TYPE_LIQUOR = 100
    CONTENT_TYPE_COCTAIL = 200
    CONTENT_TYPE_INGREDIENT = 300
    CONTENT_TYPE_EQUIP = 400
    CONTENT_TYPE_FLAG = 901


class JobInfo():
    JOB_ADD_SPIRITS = 1001
    JOB_MODIFY_SPIRITS = 1002
    JOB_REMOVE_SPIRITS = 1003
    JOB_INACTIVE_SPIRITS = 1004
    JOB_ACTIVE_SPIRITS = 1005

    JOB_ADD_INGREDIENT = 3001
    JOB_MODIFY_INGREDIENT = 3002
    JOB_REMOVE_INGREDIENT = 3003
    JOB_INACTIVE_INGREDIENT = 3004
    JOB_ACTIVE_INGREDIENT = 3005

    JOB_ADD_EQUIP = 4001
    JOB_MODIFY_EQUIP = 4002
    JOB_REMOVE_EQUIP = 4003
    JOB_INACTIVE_EQUIP = 4004
    JOB_ACTIVE_EQUIP = 4005

    JOBN_ADD_SPIRITS = "술 정보 등록"
    JOBN_MODIFY_SPIRITS = "술 정보 수정"
    JOBN_REMOVE_SPIRITS = "술 정보 제거(영구)"
    JOBN_INACTIVE_SPIRITS = "술 정보 비활성"
    JOBN_ACTIVE_SPIRITS = "술 정보 활성"
    
    JOBN_ADD_INGREDIENT = "재료 정보 등록"
    JOBN_MODIFY_INGREDIENT = "재료 정보 수정"
    JOBN_REMOVE_INGREDIENT = "재료 정보 제거(영구)"
    JOBN_INACTIVE_INGREDIENT = "재료 정보 비활성"
    JOBN_ACTIVE_INGREDIENT = "재료 정보 활성"

    JOBN_ADD_EQUIP = "도구 정보 등록"
    JOBN_MODIFY_EQUIP = "도구 정보 수정"
    JOBN_REMOVE_EQUIP = "도구 정보 제거(영구)"
    JOBN_INACTIVE_EQUIP = "도구 정보 비활성"
    JOBN_ACTIVE_EQUIP = "도구 정보 활성"


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