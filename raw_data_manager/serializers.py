from rest_framework import serializers
from .models import CategoryTree, Country, Image, RawCategory, RawLiquor, CategoryTreeWithName

class RawLiquorSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawLiquor
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