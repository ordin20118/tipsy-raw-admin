from django.db import models
from .validators import *

class RawCategory(models.Model):
    id = models.IntegerField(primary_key=True)
    parent = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=45, blank=True, null=True)
    name_en = models.CharField(max_length=45, blank=True, null=True)
    reg_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'raw_category'

class RawLiquor(models.Model):

    UPLOAD_STATE_NOT_YET = 0
    UPLOAD_STATE_NOT_UPLOADED = 1
    UPLOAD_STATE_NOT_INACTIVE = 2
    UPLOAD_STATE_NOT_ERROR = 3
    
    UPDATE_STATE_NORMAL = 0
    UPDATE_STATE_DISABLE = 1
    UPDATE_STATE_NEED_CONFIRM = 2
    UPDATE_STATE_ERROR = 3

    liquor_id = models.AutoField(primary_key=True)
    name_kr = models.CharField(max_length=200, blank=False, null=False, validators=[blank_validate,])
    name_en = models.CharField(max_length=200, blank=False, null=False, validators=[blank_validate,])
    type = models.IntegerField(blank=True, null=True)
    upload_state = models.IntegerField(blank=True, null=True)
    update_state = models.IntegerField(blank=True, null=True)
    vintage = models.IntegerField(blank=True, null=True)
    abv = models.FloatField(blank=False, null=False)
    volume = models.IntegerField(blank=True, null=True)
    country_id = models.IntegerField(blank=False, null=False)
    region = models.CharField(max_length=45, blank=True, null=True)
    region_id = models.IntegerField(blank=True, null=True)
    category1_id = models.IntegerField(blank=False, null=False)
    #category2_id = models.IntegerField(blank=False, null=False)
    category2 = models.ForeignKey(RawCategory, on_delete=models.SET_NULL, null=True)
    category3_id = models.IntegerField(blank=True, null=True)
    category4_id = models.IntegerField(blank=True, null=True)
    category_id = models.IntegerField(blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    history = models.TextField(blank=True, null=True)
    site = models.IntegerField(blank=True, null=True)
    #url = models.CharField(max_length=1000, blank=True, null=True)
    reg_admin = models.IntegerField(blank=True, null=True)
    update_admin = models.IntegerField(blank=True, null=True)
    reg_date = models.DateTimeField(blank=True, null=True)
    update_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'raw_liquor'

class JoinedLiquor(models.Model):
    liquor_id = models.AutoField(primary_key=True)
    name_kr = models.CharField(max_length=200, blank=False, null=False, validators=[blank_validate,])
    name_en = models.CharField(max_length=200, blank=False, null=False, validators=[blank_validate,])
    type = models.IntegerField(blank=True, null=True)
    upload_state = models.IntegerField(blank=True, null=True)
    update_state = models.IntegerField(blank=True, null=True)
    vintage = models.IntegerField(blank=True, null=True)
    abv = models.FloatField(blank=False, null=False)
    volume = models.IntegerField(blank=True, null=True)
    country_id = models.IntegerField(blank=False, null=False)
    region = models.CharField(max_length=45, blank=True, null=True)
    region_id = models.IntegerField(blank=True, null=True)
    category1_id = models.IntegerField(blank=False, null=False)
    category2_id = models.IntegerField(blank=False, null=False)
    category3_id = models.IntegerField(blank=True, null=True)
    category4_id = models.IntegerField(blank=True, null=True)
    category_id = models.IntegerField(blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    history = models.TextField(blank=True, null=True)
    site = models.IntegerField(blank=True, null=True)
    #url = models.CharField(max_length=1000, blank=True, null=True)
    reg_admin = models.IntegerField(blank=True, null=True)
    update_admin = models.IntegerField(blank=True, null=True)
    reg_date = models.DateTimeField(blank=True, null=True)
    update_date = models.DateTimeField(blank=True, null=True)

    # Joined Data
    reg_admin_name = models.CharField(max_length=150, blank=True, null=True)
    update_admin_name = models.CharField(max_length=150, blank=True, null=True)
    country_name = models.CharField(max_length=45, blank=True, null=True)
    category1_name = models.CharField(max_length=45, blank=True, null=True)
    category2_name = models.CharField(max_length=45, blank=True, null=True)
    category3_name = models.CharField(max_length=45, blank=True, null=True)
    category4_name = models.CharField(max_length=45, blank=True, null=True)
    rep_img = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'raw_liquor'


class Ingredient(models.Model):
    ingd_id = models.AutoField(primary_key=True)
    name_kr = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    upload_state = models.IntegerField(blank=True, null=True)
    update_state = models.IntegerField(blank=True, null=True)
    description = models.TextField()
    category1_id = models.IntegerField(blank=True, null=True)
    category2_id = models.IntegerField(blank=True, null=True)
    category3_id = models.IntegerField(blank=True, null=True)
    category4_id = models.IntegerField(blank=True, null=True)
    unit = models.CharField(max_length=10)
    is_liquid = models.IntegerField(blank=True, null=True)
    reg_user = models.IntegerField(blank=True, null=True)
    reg_admin = models.IntegerField(blank=True, null=True)
    update_admin = models.IntegerField(blank=True, null=True)
    reg_date = models.DateTimeField(blank=True, null=True)
    update_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ingredient'


class JoinedIngredient(models.Model):
    ingd_id = models.AutoField(primary_key=True)
    name_kr = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    upload_state = models.IntegerField(blank=True, null=True)
    update_state = models.IntegerField(blank=True, null=True)
    description = models.TextField()
    category1_id = models.IntegerField(blank=True, null=True)
    category2_id = models.IntegerField(blank=True, null=True)
    category3_id = models.IntegerField(blank=True, null=True)
    category4_id = models.IntegerField(blank=True, null=True)
    unit = models.CharField(max_length=10)
    is_liquid = models.IntegerField(blank=True, null=True)
    reg_user = models.IntegerField(blank=True, null=True)
    reg_admin = models.IntegerField(blank=True, null=True)
    update_admin = models.IntegerField(blank=True, null=True)
    reg_date = models.DateTimeField(blank=True, null=True)
    update_date = models.DateTimeField(blank=True, null=True)

    
    # Joined Data
    reg_admin_name = models.CharField(max_length=150, blank=True, null=True)
    update_admin_name = models.CharField(max_length=150, blank=True, null=True)
    category1_name = models.CharField(max_length=45, blank=True, null=True)
    category2_name = models.CharField(max_length=45, blank=True, null=True)
    category3_name = models.CharField(max_length=45, blank=True, null=True)
    category4_name = models.CharField(max_length=45, blank=True, null=True)
    rep_img = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ingredient'

class Equipment(models.Model):
    equip_id = models.AutoField(primary_key=True)
    name_kr = models.CharField(max_length=100, blank=True, null=True)
    name_en = models.CharField(max_length=100, blank=True, null=True)
    upload_state = models.IntegerField(blank=True, null=True)
    update_state = models.IntegerField(blank=True, null=True)
    category1_id = models.IntegerField(blank=True, null=True)
    category2_id = models.IntegerField(blank=True, null=True)
    category3_id = models.IntegerField(blank=True, null=True)
    category4_id = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    reg_admin = models.IntegerField(blank=True, null=True)
    update_admin = models.IntegerField(blank=True, null=True)
    reg_date = models.DateTimeField(blank=True, null=True)
    update_date = models.DateTimeField(blank=True, null=True)
   
    class Meta:
        managed = False
        db_table = 'equipment'


class JoinedEquipment(models.Model):
    equip_id = models.AutoField(primary_key=True)
    name_kr = models.CharField(max_length=100, blank=True, null=True)
    name_en = models.CharField(max_length=100, blank=True, null=True)
    upload_state = models.IntegerField(blank=True, null=True)
    update_state = models.IntegerField(blank=True, null=True)
    category1_id = models.IntegerField(blank=True, null=True)
    category2_id = models.IntegerField(blank=True, null=True)
    category3_id = models.IntegerField(blank=True, null=True)
    category4_id = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    reg_admin = models.IntegerField(blank=True, null=True)
    update_admin = models.IntegerField(blank=True, null=True)
    reg_date = models.DateTimeField(blank=True, null=True)
    update_date = models.DateTimeField(blank=True, null=True)
     
    # Joined Data
    reg_admin_name = models.CharField(max_length=150, blank=True, null=True)
    update_admin_name = models.CharField(max_length=150, blank=True, null=True)
    category1_name = models.CharField(max_length=45, blank=True, null=True)
    category2_name = models.CharField(max_length=45, blank=True, null=True)
    category3_name = models.CharField(max_length=45, blank=True, null=True)
    category4_name = models.CharField(max_length=45, blank=True, null=True)
    rep_img = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'equipment'


class Cocktail(models.Model):
    cocktail_id = models.AutoField(primary_key=True)
    name_kr = models.CharField(max_length=150, blank=True, null=True)
    name_en = models.CharField(max_length=150, blank=True, null=True)
    upload_state = models.IntegerField(blank=True, null=True)
    update_state = models.IntegerField(blank=True, null=True)
    strength = models.IntegerField(blank=True, null=True)
    method = models.IntegerField(blank=True, null=True, default=0)
    description = models.CharField(max_length=45, blank=True, null=True)
    detail_json = models.TextField(blank=True, null=True)
    source = models.IntegerField(blank=True, null=True)
    format_version = models.FloatField(blank=True, null=True)
    reg_user = models.IntegerField(blank=True, null=True)
    update_user = models.IntegerField(blank=True, null=True)
    reg_admin = models.IntegerField(blank=True, null=True)
    update_admin = models.IntegerField(blank=True, null=True)
    reg_date = models.DateTimeField(blank=True, null=True)
    update_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cocktail'


class JoinedCocktail(models.Model):
    cocktail_id = models.AutoField(primary_key=True)
    name_kr = models.CharField(max_length=150, blank=True, null=True)
    name_en = models.CharField(max_length=150, blank=True, null=True)
    upload_state = models.IntegerField(blank=True, null=True)
    update_state = models.IntegerField(blank=True, null=True)
    strength = models.IntegerField(blank=True, null=True)
    method = models.IntegerField(blank=True, null=True, default=0)
    description = models.CharField(max_length=45, blank=True, null=True)
    detail_json = models.TextField(blank=True, null=True)
    source = models.IntegerField(blank=True, null=True)
    format_version = models.FloatField(blank=True, null=True)
    reg_user = models.IntegerField(blank=True, null=True)
    update_user = models.IntegerField(blank=True, null=True)
    reg_admin = models.IntegerField(blank=True, null=True)
    update_admin = models.IntegerField(blank=True, null=True)
    reg_date = models.DateTimeField(blank=True, null=True)
    update_date = models.DateTimeField(blank=True, null=True)

    # Joined Data
    reg_admin_name = models.CharField(max_length=150, blank=True, null=True)
    update_admin_name = models.CharField(max_length=150, blank=True, null=True)
    rep_img = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cocktail'

class Word(models.Model):
    word_id = models.AutoField(primary_key=True)
    name_kr = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    description = models.TextField()
    reg_admin = models.IntegerField()
    update_admin = models.IntegerField(blank=True, null=True)
    reg_date = models.DateTimeField()
    update_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'word'

class JoinedWord(models.Model):
    word_id = models.AutoField(primary_key=True)
    name_kr = models.CharField(max_length=100, blank=True, null=True)
    name_en = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    reg_admin = models.IntegerField(blank=True, null=True)
    update_admin = models.IntegerField(blank=True, null=True)
    reg_date = models.DateTimeField(blank=True, null=True)
    update_date = models.DateTimeField(blank=True, null=True)
     
    # Joined Data
    reg_admin_name = models.CharField(max_length=150, blank=True, null=True)
    update_admin_name = models.CharField(max_length=150, blank=True, null=True)
    rep_img = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'word'


class RatingStats(models.Model):
    rating_stats_id = models.AutoField(primary_key=True)
    content_id = models.IntegerField()
    content_type = models.IntegerField()
    rating_cnt = models.IntegerField(default=0)
    rating_avg = models.FloatField(default=0.0)
    rating00 = models.IntegerField(default=0)
    rating01 = models.IntegerField(default=0)
    rating02 = models.IntegerField(default=0)
    rating03 = models.IntegerField(default=0)
    rating04 = models.IntegerField(default=0)
    rating05 = models.IntegerField(default=0)
    reg_date = models.DateTimeField()
    update_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rating_stats'

class ContentStats(models.Model):
    content_stats_id = models.AutoField(primary_key=True)
    content_id = models.IntegerField()
    content_type = models.IntegerField()
    view_cnt = models.IntegerField(default=0)
    bookmark_cnt = models.IntegerField(default=0)
    comment_cnt = models.IntegerField(default=0)
    like_cnt = models.IntegerField(default=0)
    dislike_cnt = models.IntegerField(default=0)
    share_cnt = models.IntegerField(default=0)
    report_cnt = models.IntegerField(default=0)
    reg_date = models.DateTimeField()
    update_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'content_stats'
        unique_together = (('content_id', 'content_type'),)





class CategoryTree(models.Model):
    categ_tree_key = models.CharField(primary_key=True, max_length=100)
    category1_id = models.IntegerField(blank=True, null=True)
    category2_id = models.IntegerField(blank=True, null=True)
    category3_id = models.IntegerField(blank=True, null=True)
    category4_id = models.IntegerField(blank=True, null=True)
    reg_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'category_tree'

class CategoryTreeWithName(models.Model):
    categ_tree_key = models.CharField(primary_key=True, max_length=100)
    category1_id = models.IntegerField(blank=True, null=True)
    category2_id = models.IntegerField(blank=True, null=True)
    category3_id = models.IntegerField(blank=True, null=True)
    category4_id = models.IntegerField(blank=True, null=True)
    category1_name = models.CharField(max_length=45, blank=True, null=True)
    category2_name = models.CharField(max_length=45, blank=True, null=True)
    category3_name = models.CharField(max_length=45, blank=True, null=True)
    category4_name = models.CharField(max_length=45, blank=True, null=True)
    category1_name_en = models.CharField(max_length=45, blank=True, null=True)
    category2_name_en = models.CharField(max_length=45, blank=True, null=True)
    category3_name_en = models.CharField(max_length=45, blank=True, null=True)
    category4_name_en = models.CharField(max_length=45, blank=True, null=True)
    reg_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'category_tree'

class Country(models.Model):
    country_id = models.IntegerField(primary_key=True)
    parent_id = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=45, blank=True, null=True)
    name_eng = models.CharField(max_length=45, blank=True, null=True)
    type = models.IntegerField(blank=True, null=True)
    alpha2 = models.CharField(max_length=10, blank=True, null=True)
    alpha3 = models.CharField(max_length=10, blank=True, null=True)
    image = models.CharField(max_length=500, blank=True, null=True)
    reg_date = models.DateTimeField(blank=True, null=True)
    update_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'country'
        

class Image(models.Model):

    IMG_TYPE_REP = 0
    IMG_TYPE_NORMAL = 1
    IMG_TYPE_ORG = 99

    IMG_STATUS_PUB = 0
    IMG_STATUS_PRV = 1

    image_id = models.AutoField(primary_key=True)
    image_type = models.IntegerField(blank=True, null=True)
    content_id = models.IntegerField(blank=True, null=True)
    content_type = models.IntegerField(blank=True, null=True)
    s3_key = models.CharField(max_length=500, blank=True, null=True)
    extension = models.CharField(max_length=20, blank=True, null=True)
    seq = models.IntegerField(blank=True, null=True)
    is_open = models.IntegerField(blank=True, null=True)
    reg_date = models.DateTimeField(blank=True, null=True, auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'image'



class AuthUser(models.Model):
    id = models.AutoField(primary_key=True)
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'        



class ManageLog(models.Model):
    id = models.AutoField(primary_key=True)
    #admin_id = models.IntegerField(blank=True, null=True)
    #admin = models.ForeignKey(AuthUser, to_field='id', on_delete=models.SET_NULL, related_name='admin', null=True)
    admin = models.ForeignKey(AuthUser, on_delete=models.SET_NULL, null=True)
    job_code = models.IntegerField(blank=True, null=True)
    job_name = models.CharField(max_length=45, blank=True, null=True)
    content_id = models.IntegerField(blank=True, null=True)
    content_type = models.IntegerField(blank=True, null=True)
    info = models.TextField(blank=True, null=True)
    reg_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'manage_log'


class CrawledLiquorImage(models.Model):
    
    STATE_USABLE = 0
    STATE_UNUSABLE = 1
    STATE_WAITING = 2

    id = models.AutoField(primary_key=True)
    liquor_id = models.IntegerField(blank=True, null=False)
    query = models.CharField(max_length=200, blank=True, null=False)
    is_use = models.IntegerField(blank=True, null=False)
    org_img_url = models.CharField(max_length=500, blank=True, null=False)
    img_url = models.CharField(max_length=500, blank=True, null=False)
    s3_key = models.CharField(max_length=300, blank=True, null=False)
    reg_date = models.DateTimeField(blank=True, null=False)
    update_date = models.DateTimeField(blank=True, null=False)

    class Meta:
        managed = False
        db_table = 'crawled_liquor_image'

class GroupedCrawledLiquorImage(models.Model):
    id = models.AutoField(primary_key=True)
    liquor_id = models.IntegerField(blank=True, null=False)
    name_kr = models.CharField(max_length=200, blank=True, null=False)
    total_cnt = models.IntegerField(blank=True, null=False)
    usable = models.IntegerField(blank=True, null=False)
    unusable = models.IntegerField(blank=True, null=False)
    waiting = models.IntegerField(blank=True, null=False)

    class Meta:
        managed = False
        db_table = 'crawled_liquor_image'


class CrawledLiquor(models.Model):
    
    # 0:크롤링 대기, 1:크롤링 완료, 2:크롤링 에러, 3:크롤링 업데이트 필요, 4:데이터 중복, 5:업로드 완료, 6:업로드 실패, 7:업로드 대기, 99: 더 이상 크롤링 불가
    STATE_CRAWL_WAIT = 0
    STATE_CRAWL_SUCCESS = 1
    STATE_CRAWL_FAIL = 2
    STATE_CRAWL_NEED_UPDATE = 3
    STATE_CRAWL_DUP = 4
    STATE_UPLOAD_SUCCESS = 5
    STATE_UPLOAD_FAIL = 6
    STATE_UPLOAD_WAIT = 7
    STATE_CRAWL_CANT = 99

    # 봇이 판단한 업로드 가능 여부\n0:사용 가능, 1:사용 불가
    AUTO_INGEST_USABLE = 0
    AUTO_INGEST_UNUSABLE = 1
    

    id = models.AutoField(primary_key=True)
    liquor_id = models.IntegerField(blank=True, null=False)
    name_kr = models.CharField(max_length=200, blank=True, null=False)
    name_en = models.CharField(max_length=200, blank=True, null=False)
    name_en_dup_chck = models.CharField(max_length=200, blank=True, null=False)
    site = models.IntegerField(blank=True, null=False)
    url = models.CharField(max_length=500, blank=True, null=False)
    
    vintage = models.IntegerField(blank=True, null=False)
    abv = models.FloatField(blank=True, null=False)

    auto_state = models.IntegerField(blank=True, null=False)
    state = models.IntegerField(blank=True, null=False)
    is_use = models.IntegerField(blank=True, null=False)
    country_id = models.IntegerField(blank=True, null=False)
    country_name = models.CharField(max_length=50, blank=True, null=False)
    region_id = models.IntegerField(blank=True, null=False)
    region_name = models.CharField(max_length=50, blank=True, null=False)
    category_name = models.CharField(max_length=45, blank=True, null=False)
    variety = models.CharField(max_length=100, blank=True, null=False)

    category1_id = models.IntegerField(blank=True, null=False)
    #category2_id = models.IntegerField(blank=True, null=False)
    category2 = models.ForeignKey(RawCategory, on_delete=models.SET_NULL, null=True)
    category3_id = models.IntegerField(blank=True, null=False)
    category4_id = models.IntegerField(blank=True, null=False)

    rating_avg = models.FloatField(blank=True, null=False)
    rating_count = models.IntegerField(blank=True, null=False)

    description = models.TextField(blank=True, null=False)
    img_url = models.CharField(max_length=300, blank=True, null=False)
    detail_json = models.TextField(blank=True, null=False)
    u_name_kr = models.CharField(max_length=200, blank=True, null=False)
    u_name_en = models.CharField(max_length=200, blank=True, null=False)
    u_country_name = models.CharField(max_length=50, blank=True, null=False)
    u_region_name = models.CharField(max_length=50, blank=True, null=False)

    
    last_crawled_date = models.DateTimeField(blank=True, null=False)
    upload_date = models.DateTimeField(blank=True, null=False)
    reg_date = models.DateTimeField(blank=True, null=False)
    update_date = models.DateTimeField(blank=True, null=False)

    

    class Meta:
        managed = False
        db_table = 'crawled_liquor'
