from rest_framework import serializers
from .models import *
from .classes import *

class RawLiquorSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawLiquor
        fields = '__all__'

class JoinedLiquorSerializer(serializers.ModelSerializer):
    class Meta:
        model = JoinedLiquor
        fields = '__all__'

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'

class JoinedIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = JoinedIngredient
        fields = '__all__'

class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = '__all__'

class JoinedEquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = JoinedEquipment
        fields = '__all__'

class WordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Word
        fields = '__all__'

class JoinedWordSerializer(serializers.ModelSerializer):
    class Meta:
        model = JoinedWord
        fields = '__all__'

class CocktailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cocktail
        fields = '__all__'

class JoinedCocktailSerializer(serializers.ModelSerializer):
    class Meta:
        model = JoinedCocktail
        fields = '__all__'

class CrawledLiquorImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrawledLiquorImage
        fields = '__all__'

class GroupedCrawledLiquorImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupedCrawledLiquorImage
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

class ManageLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManageLog
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['admin'] = AuthUserSerializer(instance.admin).data
        return response


class AuthUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = ['username',  'email', 'last_login']




