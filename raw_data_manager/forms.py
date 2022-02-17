from importlib.metadata import requires
from django import forms
from django.core.validators import MinLengthValidator
from raw_data_manager.models import RawLiquor

def min_length_3_validator(value):
	if len(value) < 3:
		raise forms.ValidationError('3글자 이상 입력해주세요')

length_validator = MinLengthValidator(3, "길이가 너무 짧습니다.")


class LiquorForm(forms.Form):
	name_kr = forms.CharField(max_length=100, validators=[length_validator])
	#name_en = forms.CharField(max_length=100, validators=['min_length_3_validator'])
	#name_kr = forms.CharField(max_length=100)
	name_en = forms.CharField(max_length=100)

	def save(self, commit=True):
		
		# validate data
		liquor = RawLiquor(**self.cleaned_data)

		if commit:
			liquor.save()
		return liquor