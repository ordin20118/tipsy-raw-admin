from django.db import models

class RawLiquor(models.Model):
    liquor_id = models.AutoField(primary_key=True)
    name_kr = models.CharField(max_length=200, blank=True, null=True)
    name_en = models.CharField(max_length=200, blank=True, null=True)
    type = models.IntegerField(blank=True, null=True)
    upload_state = models.IntegerField(blank=True, null=True)
    update_state = models.IntegerField(blank=True, null=True)
    vintage = models.IntegerField(blank=True, null=True)
    abv = models.FloatField(blank=True, null=True)
    volume = models.IntegerField(blank=True, null=True)
    country_id = models.IntegerField(blank=True, null=True)
    region = models.CharField(max_length=45, blank=True, null=True)
    region_id = models.IntegerField(blank=True, null=True)
    category1_id = models.IntegerField(blank=True, null=True)
    category2_id = models.IntegerField(blank=True, null=True)
    category3_id = models.IntegerField(blank=True, null=True)
    category4_id = models.IntegerField(blank=True, null=True)
    category_id = models.IntegerField(blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    history = models.TextField(blank=True, null=True)
    reg_date = models.DateTimeField(blank=True, null=True)
    update_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'raw_liquor'



class RawCategory(models.Model):
    id = models.IntegerField(primary_key=True)
    parent = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=45, blank=True, null=True)
    name_en = models.CharField(max_length=45, blank=True, null=True)
    reg_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'raw_category'


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
    image_id = models.AutoField(primary_key=True)
    image_type = models.IntegerField(blank=True, null=True)
    content_id = models.IntegerField(blank=True, null=True)
    content_type = models.IntegerField(blank=True, null=True)
    path = models.CharField(max_length=200, blank=True, null=True)
    is_open = models.IntegerField(blank=True, null=True)
    reg_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'image'