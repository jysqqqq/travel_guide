from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class CustomMinimumLengthValidator:
    def __init__(self, min_length=8):
        self.min_length = min_length

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                _("密码长度至少为%(min_length)d个字符"),
                code='password_too_short',
                params={'min_length': self.min_length},
            )

    def get_help_text(self):
        return _("密码长度至少为%d个字符" % self.min_length)

class CustomNumericPasswordValidator:
    def validate(self, password, user=None):
        if password.isdigit():
            raise ValidationError(
                _("密码不能全为数字"),
                code='password_entirely_numeric',
            )

    def get_help_text(self):
        return _("密码不能全为数字")

class CustomCommonPasswordValidator:
    def validate(self, password, user=None):
        if len(set(password)) < 4:
            raise ValidationError(
                _("密码过于简单，请使用更复杂的密码"),
                code='password_too_common',
            )

    def get_help_text(self):
        return _("密码不能过于简单")

class CustomUserAttributeSimilarityValidator:
    def __init__(self, user_attributes=('username', 'email'), max_similarity=0.7):
        self.user_attributes = user_attributes
        self.max_similarity = max_similarity

    def validate(self, password, user=None):
        if not user:
            return

        for attribute_name in self.user_attributes:
            value = getattr(user, attribute_name, None)
            if not value or not isinstance(value, str):
                continue

            if value.lower() in password.lower():
                raise ValidationError(
                    _("密码不能包含用户名或邮箱"),
                    code='password_too_similar',
                )

    def get_help_text(self):
        return _("密码不能与个人信息太相似") 