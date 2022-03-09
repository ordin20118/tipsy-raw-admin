from importlib.metadata import requires
from django import forms
from raw_data_manager.models import RawLiquor
from .validators import *

class LiquorForm(forms.Form):
	name_kr = forms.CharField(max_length=100, validators=[blank_validate])
	name_en = forms.CharField(max_length=200, validators=[blank_validate])
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