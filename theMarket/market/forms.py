from django import forms
from market.models import User


class UserBaseForm(forms.Form):
    login            = forms.RegexField(
        regex='^[a-zA-Z0-9_-]+$',
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
        login = self.cleaned_data.get('login')
        try:
            User.objects.get(login=login)
        except User.DoesNotExist:
            return login
        else:
            raise forms.ValidationError('User with login "%s" already exists.' % login)


class AdminRegistrationForm(RegistrationForm):
    is_admin = forms.BooleanField(required=False)


class AccountForm(UserBaseForm):
    password         = forms.CharField(widget=forms.PasswordInput(render_value=False), required=False)
    password_confirm = forms.CharField(widget=forms.PasswordInput(render_value=False), required=False)
    
    def __init__(self, user=None, *args, **kwargs):
        super(AccountForm, self).__init__(*args, **kwargs)
        self.user = user
    
    def clean_login(self):
        login = self.cleaned_data.get('login')
        if User.objects.filter(login=login).exists():
            if self.user.login != login:
                raise forms.ValidationError('User with login "%s" already exists.' % login)
        return login


class AdminAccountForm(AccountForm):
    is_admin = forms.BooleanField(required=False)
        
    def clean_is_admin(self):
        is_admin = self.cleaned_data.get('is_admin')
        if self.user.is_admin and User.objects.filter(is_admin=True).count() == 1 and not is_admin:
            raise forms.ValidationError('At least one administrator should exist.')
        return is_admin