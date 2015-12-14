"""
Forms and validation code for user registration.

"""

from django import forms
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth import authenticate, login

from django_facebook.utils import get_user_model
import inspect

attrs_dict = {'class': 'required'}

def my_login(request,user):
    login(request, user)


def get_request():
    """Walk up the stack, return the nearest first argument named "request"."""
    frame = None
    try:
        for f in inspect.stack()[1:]:
            frame = f[0]
            code = frame.f_code
            if code.co_varnames and code.co_varnames[0] == "request":
                return frame.f_locals['request']
    finally:
        del frame


class FacebookRegistrationFormUniqueEmail(forms.Form):

    """
    Some basic validation, adapted from django registration
    """
    username = forms.RegexField(regex=r'^\w+$',
                                max_length=30,
                                widget=forms.TextInput(attrs=attrs_dict),
                                label=_("Username"),
                                error_messages={'invalid': _("This value must contain only letters, numbers and underscores.")})
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict,
                                                               maxlength=75)),
                             label=_("Email address"))
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
        label=_("Password"))
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
        label=_("Password (again)"))

    def clean_username(self):
        """
        Validate that the username is alphanumeric and is not already
        in use.

        """
        try:
            get_user_model().objects.get(
                username__iexact=self.cleaned_data['username'])
        except get_user_model().DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError(
            _("A user with that username already exists."))

    def clean(self):
        """
        Verifiy that the values entered into the two password fields
        match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single
        field.
        """
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(
                    _("The two password fields didn't match."))
        return self.cleaned_data

    def clean_email(self):
        """
        Validate that the supplied email address is unique for the
        site.
        """
        if get_user_model().objects.filter(email__iexact=self.cleaned_data['email']):
            user = get_user_model().objects.get(email__iexact=self.cleaned_data['email'])
            request = get_request()
            my_login(request, user)
            print("email already in use, logged in!")
            #raise forms.ValidationError(_(
            #    "This email address is already in use. Please supply a different email address."))
        return self.cleaned_data['email']
