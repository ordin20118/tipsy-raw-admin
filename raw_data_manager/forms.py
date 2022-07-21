from importlib.metadata import requires
from django import forms
from raw_data_manager.models import *
from .validators import *

class LiquorForm(forms.Form):
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
	name_kr = forms.CharField(max_length=100, validators=[blank_validate])
	name_en = forms.CharField(max_length=100, validators=[blank_validate])
	category1_id = forms.IntegerField(validators=[int_zero_validate])
	category2_id = forms.IntegerField(required=False, validators=[int_zero_validate])
	category3_id = forms.IntegerField(required=False, validators=[int_zero_validate])
	category4_id = forms.IntegerField(required=False, validators=[int_zero_validate])
	unit = forms.CharField(max_length=10, validators=[blank_validate])
	description = forms.CharField(required=False)	
    
	def save(self, commit=True):		
		ingredient = Ingredient(**self.cleaned_data)
		if commit:
			ingredient.save()
		return ingredient



class EquipmentForm(forms.Form):
	name_kr = forms.CharField(max_length=100, validators=[blank_validate])
	name_en = forms.CharField(max_length=200, validators=[blank_validate])
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
