from rest_framework import serializers
from .models import CategoryTree, Country, Image, JoinedLiquor, RawCategory, RawLiquor, CategoryTreeWithName
from .classes import *

class RawLiquorSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawLiquor
        fields = '__all__'

class JoinedLiquorSerializer(serializers.ModelSerializer):
    class Meta:
        model = JoinedLiquor
        fields = '__all__'


class RawCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RawCategory
        fields = ('id', 'parent', 'name', 'name_en', 'reg_date')

class CategoryTreeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryTree
        fields = '__all__'

class CategoryTreeWithNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryTreeWithName
        fields = '__all__'

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'

class SearchParamSerializer(serializers.Serializer):
    page = serializers.IntegerField()
    per_page = serializers.IntegerField()
    list = RawLiquorSerializer()
    # content = serializers.CharField(max_length=200)
    # created = serializers.DateTimeField()




