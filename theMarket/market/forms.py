from django import forms
from market.models import User

class LoginForm(forms.Form):
    login    = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput(render_value=False))
    def clean(self):
        data = self.cleaned_data
        try:
            self.user = User.objects.get(login=data['login'])
        except User.DoesNotExist:
            self._errors['login'] = self.error_class(['Login is incorrect.'])
        else:
            if self.user.password != self.user.get_password_hash(data['password']):
                self._errors['password'] = self.error_class(['Password is incorrect.'])
        return data
        
class RegistrationForm(forms.Form):
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
    def clean_login(self):
        data = self.cleaned_data.get('login')
        try:
            User.objects.get(login=data)
        except User.DoesNotExist:
            return data
        else:
            raise forms.ValidationError('User with login "%s" already exists.' % data)

class AccountForm(forms.Form):
    new_password         = forms.CharField(widget=forms.PasswordInput(render_value=False), required=False)
    new_password_confirm = forms.CharField(widget=forms.PasswordInput(render_value=False), required=False)
    email                = forms.EmailField()
    def clean(self):
        data = self.cleaned_data
        if data.get('new_password') != data.get('new_password_confirm'):
            self._errors['new_password'] = self.error_class(['Passwords do not match.'])
        return data
