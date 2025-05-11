from importlib.metadata import requires
from django import forms
from raw_data_manager.models import *
from .validators import *

class LiquorForm(forms.Form):
	liquor_id = forms.IntegerField(required=False)
	name_kr = forms.CharField(max_length=100, validators=[blank_validate])
	name_en = forms.CharField(max_length=200, validators=[blank_validate])
	upload_state = forms.IntegerField(required=False)
	update_state = forms.IntegerField(required=False)
	vintage = forms.IntegerField(required=False, validators=[int_zero_validate])
	abv = forms.FloatField(validators=[float_zero_validate])
	country_id = forms.IntegerField(validators=[int_zero_validate])
	region = forms.CharField(max_length=45, required=False, validators=[blank_validate])
	category1_id = forms.IntegerField(validators=[int_zero_validate])
	category2_id = forms.IntegerField(validators=[int_zero_validate])
	category3_id = forms.IntegerField(required=False, validators=[int_zero_validate])
	category4_id = forms.IntegerField(required=False, validators=[int_zero_validate])
	price = forms.FloatField(required=False, validators=[float_zero_validate])
	description = forms.CharField(required=False, validators=[blank_validate])
	history = forms.CharField(required=False, validators=[blank_validate])
    
	# class Meta:
	# 	model = RawLiquor
	# 	fields = '__all__'

	def save(self, commit=True):
		
		# validate data
		liquor = RawLiquor(**self.cleaned_data)

		if commit:
			liquor.save()
		return liquor

class CocktailForm(forms.Form):
	cocktail_id = forms.IntegerField(required=False)
	name_kr = forms.CharField(max_length=100, validators=[blank_validate])
	name_en = forms.CharField(max_length=200, validators=[blank_validate])
	strength = forms.IntegerField(validators=[int_zero_validate])
	description = forms.CharField(required=False, validators=[blank_validate])
	detail_json = forms.CharField(required=True, validators=[blank_validate])
	format_version = forms.FloatField(required=True, validators=[float_zero_validate])

	def save(self, commit=True):
		
		# validate data
		cocktail = Cocktail(**self.cleaned_data)

		if commit:
			cocktail.save()
		return cocktail


class CocktailDelForm(forms.Form):
	cocktail_id = forms.IntegerField(required=True)

	def get_obj(self):		
		cocktail = Cocktail(**self.cleaned_data)
		return cocktail


class IngredientForm(forms.Form):
	ingd_id = forms.IntegerField(required=False, validators=[int_zero_validate])
	name_kr = forms.CharField(max_length=100, validators=[blank_validate])
	name_en = forms.CharField(max_length=100, validators=[blank_validate])
	upload_state = forms.IntegerField(required=False)
	update_state = forms.IntegerField(required=False)
	category1_id = forms.IntegerField(validators=[int_zero_validate])
	category2_id = forms.IntegerField(required=False)
	category3_id = forms.IntegerField(required=False)
	category4_id = forms.IntegerField(required=False)
	unit = forms.CharField(required=False, max_length=10)
	description = forms.CharField(required=False)	
    
	def save(self, commit=True):		
		ingredient = Ingredient(**self.cleaned_data)
		if commit:
			ingredient.save()
		return ingredient



class EquipmentForm(forms.Form):
	equip_id = forms.IntegerField(required=False, validators=[int_zero_validate])
	name_kr = forms.CharField(max_length=100, validators=[blank_validate])
	name_en = forms.CharField(max_length=200, validators=[blank_validate])
	upload_state = forms.IntegerField(required=False)
	update_state = forms.IntegerField(required=False)
	category1_id = forms.IntegerField(validators=[int_zero_validate])
	category2_id = forms.IntegerField(required=False, validators=[int_zero_validate])
	category3_id = forms.IntegerField(required=False, validators=[int_zero_validate])
	category4_id = forms.IntegerField(required=False, validators=[int_zero_validate])
	description = forms.CharField(required=False)
	
	def save(self, commit=True):		
		equip = Equipment(**self.cleaned_data)
		if commit:
			equip.save()
		return equip

class WordForm(forms.Form):
	word_id = forms.IntegerField(required=False, validators=[int_zero_validate])
	name_kr = forms.CharField(max_length=100, validators=[blank_validate])
	name_en = forms.CharField(max_length=200, validators=[blank_validate])
	description = forms.CharField(required=False)
	
	def save(self, commit=True):		
		word = Word(**self.cleaned_data)
		if commit:
			word.save()
		return word


class ImageForm(forms.Form):
	image_id = forms.IntegerField(required=False)
	image_type = forms.IntegerField(required=False)
	content_id = forms.IntegerField(required=False)
	content_type = forms.IntegerField(required=False)
	is_open = forms.IntegerField(required=False)
	#is_delete = forms.IntegerField(required=False)

	def save(self, commit=True):
		image = Image(**self.cleaned_data)
		if commit:
			image.save()
		return image

class CrawledLiquorImageForm(forms.Form):
	id = forms.IntegerField(required=False)
	liquor_id = forms.IntegerField(required=False)
	is_use = forms.IntegerField(required=False)

	def save(self, commit=True):
		image = CrawledLiquorImage(**self.cleaned_data)
		if commit:
			image.save()
		return image

class RembgQueueForm(forms.Form):
	id = forms.IntegerField(required=False)
	org_image_id = forms.IntegerField(required=True)
	out_image_id = forms.IntegerField(required=False)
	state = forms.IntegerField(required=False)

	def save(self, commit=True):
		queue = RembgQueue(**self.cleaned_data)
		if commit:
			queue.save()
		return queue

class SearchLiquorArticleQueueForm(forms.ModelForm):
	target_search_count = forms.IntegerField(required=True)
	searched_count = forms.IntegerField(initial=0, required=False)
	collected_count = forms.IntegerField(initial=0, required=False)
	dup_count = forms.IntegerField(initial=0, required=False)
	failed_count = forms.IntegerField(initial=0, required=False)
	liquor_id = forms.IntegerField(initial=0, required=False)

	class Meta:
		model = SearchLiquorArticleQueue
		fields = ['keyword', 'target_search_count', 'searched_count', 'collected_count', 'dup_count', 'failed_count', 'liquor']

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['url', 'title', 'content', 'extracted_content', 'score', 'state']

    # 필요한 경우 custom validation 추가
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 1:
            raise forms.ValidationError('제목은 1자 이상이어야 합니다.')
        return title

    def clean_score(self):
        score = self.cleaned_data.get('score')
        if score is not None and (score < 0 or score > 100):
            raise forms.ValidationError('점수는 0에서 100 사이여야 합니다.')
        return score

class ArticleTagForm(forms.ModelForm):
    class Meta:
        model = ArticleTag
        fields = ['article', 'tag']

    # 필요한 경우 추가적인 검증 로직을 추가할 수 있습니다.
    def clean_tag(self):
        tag = self.cleaned_data.get('tag')
        if len(tag) < 3:
            raise forms.ValidationError('태그는 3자 이상이어야 합니다.')
        return tag

class LiquorContentForm(forms.ModelForm):
    class Meta:
        model = LiquorContent
        fields = [
            'liquor',
            'seq',
            'title',
            'sub_title',
            'content',
            'type'
        ]
	
    