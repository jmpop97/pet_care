from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from users.models import User, CheckEmail, PetOwnerReview, PetSitterReview


class CommonDisplayAdmin(admin.ModelAdmin):
    fields=()
    list_display=()
    readonly_fields=()
    common_list_display=('created_at','updated_at',"show_status")
    common_fields =('created_at','updated_at',"show_status")
    common_readonly_fields = ('created_at','updated_at')
    def __init__(self, model: type, admin_site):
        self.fields+=self.common_fields
        self.list_display+=self.common_list_display
        self.readonly_fields+=self.common_readonly_fields
        super().__init__(model, admin_site)


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""

    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ["username","email"]

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = "__all__"


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ["username","email", "is_admin","photo"]
    list_filter = ["is_admin"]
    fieldsets = [
        (None, {"fields": ["username", "password"]}),
        ("Personal info", {"fields": ["email","photo"]}),
        ("Permissions", {"fields": ["is_admin"]}),
    ]
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["username","email","photo", "password1", "password2"],
            },
        ),
    ]
    search_fields = ["username"]
    ordering = ["username"]
    filter_horizontal = []


class CheckEmailAdmin(admin.ModelAdmin):
    list_display=('email','random_num','try_num','created_at')
    list_display=('email','random_num','try_num','created_at')
    readonly_fields=('created_at',)

class PetOwnerReviewDisplay(CommonDisplayAdmin):
    fields=('writer','owner','content','star')
    list_display=('writer','owner','content','star')


class PetSitterReviewDisplay(CommonDisplayAdmin):
    fields=('writer','sitter','content','star')
    list_display=('writer','sitter','content','star')




# Now register the new UserAdmin...
admin.site.register(User, UserAdmin)
admin.site.register(CheckEmail, CheckEmailAdmin)

admin.site.register(PetOwnerReview, PetOwnerReviewDisplay)
admin.site.register(PetSitterReview, PetSitterReviewDisplay)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)
