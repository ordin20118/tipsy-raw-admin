from django import forms
from models import RawLiquor

def min_length_3_validator(value):
	if len(value) < 3:
		raise forms.ValidationError('3글자 이상 입력해주세요')

class LiquorForm(forms.Form):
	name_kr = forms.CharField(max_length=100, validators=['min_length_3_validator'])

	# ModelForm.save 인터페이스를 흉내내어 구현
	def save(self, commit=True):
		liquor = RawLiquor(**self.cleaned_data)
		if commit:
			liquor.save()
		return liquor