from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import User
from .models import Profile

class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['image', 'displayname', 'first_name', 'last_name', 'info']
        widgets = {
            'image': forms.FileInput(),
            'displayname' : forms.TextInput(attrs={'placeholder': 'Thêm tên hiển thị'}),
            'first_name' : forms.TextInput(attrs={'placeholder': 'Thêm tên'}),
            'last_name' : forms.TextInput(attrs={'placeholder': 'Thêm họ'}),
            'info' : forms.Textarea(attrs={'rows':3, 'placeholder': 'Thêm tiểu sử'})
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].label = 'Ảnh đại diện'
        self.fields['displayname'].label = 'Tên hiển thị'
        self.fields['first_name'].label = 'Tên'
        self.fields['last_name'].label = 'Họ'
        self.fields['info'].label = 'Tiểu sử'
        
        
class EmailForm(ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['email']