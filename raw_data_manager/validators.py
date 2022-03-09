from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator

length_validator = MinLengthValidator(3, "길이가 너무 짧습니다.")

def space_validate(value):
    if len(value.split()) >= 2:
        raise ValidationError("이름에 공백이 있습니다. 공백 제거 후 다시 저장해주세요")

def blank_validate(value):
    if len(value) == 0:
        raise ValidationError("내용이 없습니다. 다시 작성해주세요.")

def zero_validate(value):
    if value == 0:
        raise ValidationError("값을 입력해주세요.")

def int_zero_validate(value):
    value = int(value)
    if value == 0:
        raise ValidationError("값을 입력해주세요.")

def float_zero_validate(value):
    value = float(value)
    if value == 0:
        raise ValidationError("값을 입력해주세요.")