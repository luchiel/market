from django import forms
from django.forms import ModelForm
from market.models import User, Address, Comment, Mark
from market.report_utils import REPORT_CHOICES


class UserBaseForm(forms.Form):
    login            = forms.RegexField(
        regex='^[\w-]+$',
        max_length=200,
        error_messages={'invalid': 'Only latin letters, symbols \'-\', \'_\' and digits are accepted.'},
    )
    password         = forms.CharField(widget=forms.PasswordInput(render_value=False))
    password_confirm = forms.CharField(widget=forms.PasswordInput(render_value=False))
    email            = forms.EmailField()
    def clean(self):
        data = self.cleaned_data
        if data.get('password') != data.get('password_confirm'):
            self._errors['password'] = self.error_class(['Passwords do not match.'])
        return data


class LoginForm(forms.Form):
    login    = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput(render_value=False))
    def clean(self):
        data = self.cleaned_data
        try:
            self.user = User.objects.get(login=data.get('login'))
        except User.DoesNotExist:
            self._errors['login'] = self.error_class(['Login is incorrect.'])
        else:
            if not 'password' in data or self.user.password != self.user.get_password_hash(data['password']):
                self._errors['password'] = self.error_class(['Password is incorrect.'])
        return data


class RegistrationForm(UserBaseForm):
    def clean_login(self):
        new_login = self.cleaned_data.get('login')
        if User.objects.filter(login=new_login).exists():
            raise forms.ValidationError('User with login \'%s\' already exists.' % new_login)
        return new_login


class AdminRegistrationForm(RegistrationForm):
    is_admin = forms.BooleanField(required=False)


class AccountForm(UserBaseForm):
    password         = forms.CharField(widget=forms.PasswordInput(render_value=False), required=False)
    password_confirm = forms.CharField(widget=forms.PasswordInput(render_value=False), required=False)
    
    def __init__(self, user=None, *args, **kwargs):
        super(AccountForm, self).__init__(*args, **kwargs)
        self.user = user
    
    def clean_login(self):
        new_login = self.cleaned_data.get('login')
        if User.objects.filter(login=new_login).exists() and self.user.login != new_login:
            raise forms.ValidationError('User with login \'%s\' already exists.' % new_login)
        return new_login


class AdminAccountForm(AccountForm):
    is_admin = forms.BooleanField(required=False)
        
    def clean_is_admin(self):
        new_is_admin = self.cleaned_data.get('is_admin')
        if self.user.is_admin and User.objects.filter(is_admin=True).count() == 1 and not new_is_admin:
            raise forms.ValidationError('At least one administrator should exist.')
        return new_is_admin


class CategoryForm(forms.Form):
    name = forms.CharField(max_length=200)


class MoveForm(forms.Form):
    parent    = forms.CharField(max_length=200, widget = forms.TextInput(attrs={'readonly':'readonly'}))
    parent_id = forms.IntegerField(widget=forms.HiddenInput)


class ProductForm(forms.Form):
    name        = forms.CharField(max_length=200)
    price       = forms.IntegerField()
    description = forms.CharField(widget=forms.Textarea)
    image       = forms.ImageField(required=False)
    
    def clean_image(self):
        SIZE_CONST = 1024 * 1024
        new_image = self.cleaned_data.get('image')
        if new_image and new_image.size > SIZE_CONST:
            raise forms.ValidationError('File is too big: size > 1Mb')
        return new_image


class ProductChoiceForm(forms.Form):
    INTEGER_CHOICES = []
    for i in range(20):
        INTEGER_CHOICES.append((i + 1, i + 1));
    product_id   = forms.IntegerField(required=False, widget=forms.HiddenInput)
    purchased_id = forms.IntegerField(required=False, widget=forms.HiddenInput)
    name         = forms.CharField(max_length=200, required=False)
    price        = forms.IntegerField(required=False)
    quantity     = forms.TypedChoiceField(choices=INTEGER_CHOICES, empty_value=1, coerce=int)


class AddressForm(ModelForm):
    class Meta:
        model = Address


class CommentForm(ModelForm):
    class Meta:
        model = Comment


class MarkForm(ModelForm):
    class Meta:
        model = Mark


class ReportForm(MoveForm):
    DATE_FORMATS = ['%d.%m.%Y']
    row        = forms.TypedChoiceField(choices=REPORT_CHOICES, empty_value=0, coerce=int)
    column     = forms.TypedChoiceField(choices=REPORT_CHOICES, empty_value=0, coerce=int)
    start_date = forms.DateField(input_formats=DATE_FORMATS)
    end_date   = forms.DateField(input_formats=DATE_FORMATS)
