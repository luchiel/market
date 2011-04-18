from django import forms
from market.models import User


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


class MoveCategoryForm(forms.Form):
    parent = forms.CharField(max_length=200, widget = forms.TextInput(attrs={'readonly':'readonly'}))
    parent_id = forms.IntegerField(widget=forms.HiddenInput)


class AddProductForm(forms.Form):
    name = forms.CharField(max_length=200)
    image = forms.ImageField()
    description = forms.CharField()


class ProductForm(forms.Form):
    pass
