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


class SearchParam():
    
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

class Paging():

    DEF_PER_PAGE = 10

    def __init__(self, nowPage=1, totalCount=0, perPage=10):
        self.perPage = perPage
        self.nowPage = nowPage
        self.totalCount = totalCount
        self.pageRange = 10

    def getLastRow(self):
        return self.perPage * self.nowPage

    def getFirstRow(self):
        return self.perPage * self.nowPage - self.perPage

    def getMaxPage(self):
        return int(math.ceil(self.totalCount / (self.perPage * float(1))))

    def getPages(self):
        startPage = int((math.ceil(self.nowPage/self.pageRange)-1)*self.pageRange)+1
        pages = []

        for i in range(0,self.pageRange):
            pages.append(startPage)
            startPage += 1
            if startPage > self.getMaxPage():
                break

        return pages


class OrderBy():

    SORT_ASC = "asc"
    SORT_DESC = "desc"

    def __init__(self, field=None):
        self.field = field
        self.sorting = self.SORT_DESC