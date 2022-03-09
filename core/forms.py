from django import forms
from django_summernote.widgets import SummernoteWidget
from crispy_forms.layout import Layout,HTML,Row,Column,Field
from crispy_forms.helper import FormHelper

from core.models import Contact, EvictionNotice, ServiceRating, UnitTour, MoveOutNotice


class DateInput(forms.DateInput):
    input_type = 'date'

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['full_name', 'email', 'subject', 'message']
        widgets = {
            "message": forms.Textarea(
                attrs={"placeholder": "Put your message here..."}
            ),
        }


class UnitTourForm(forms.ModelForm):
    class Meta:
        model = UnitTour
        fields = ['full_name', 'visitor_email', 'phone_number', 'visit_date', 'message']
        widgets = {
            'visit_date': DateInput(),
            'message': forms.Textarea,
        }

class VisitUpdateForm(forms.ModelForm):
    class Meta:
        model = UnitTour
        fields = ['full_name', 'visitor_email', 'phone_number', 'visit_date', 'message', 'visit_status',]
        widgets = {
            'full_name': forms.TextInput(attrs={'readonly':'readonly'}),
            'visitor_email': forms.EmailInput(attrs={'readonly':'readonly'}),
            'phone_number': forms.TextInput(attrs={'readonly':'readonly'}),
            'visit_date': DateInput(attrs={'readonly':'readonly'}),
            'message': forms.Textarea(attrs={'readonly':'readonly'}),    
        }

class EvictionNoticeForm(forms.ModelForm):
    class Meta:
        model = EvictionNotice
        fields = ['notice_detail','help_contact_phone', 'help_contact_email', 'eviction_status','eviction_due']
        widgets = {
            'notice_detail': SummernoteWidget(attrs={'summernote': {'width': '100%', 'height': '400px'}}),
            'eviction_due': DateInput(),
        }

class NewMoveOutNoticeForm(forms.ModelForm):
    class Meta:
        model = MoveOutNotice
        fields = ['move_out_date', 'reason', ]
        widgets = {
            'reason': SummernoteWidget(attrs={'summernote': {'width': '100%', 'height': '400px'}}),
            'move_out_date': DateInput(),
        }
        
class CancelMoveOutForm(forms.ModelForm):
    class Meta:
        model = MoveOutNotice
        fields = ['drop',]
        
class UpdateMoveOutNotice(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UpdateMoveOutNotice, self).__init__(*args, **kwargs)
        self.fields['code'].disabled = True
        self.fields['tenant'].disabled = True
        self.fields['move_out_date'].disabled = True
        self.fields['created'].disabled = True
        self.fields['drop'].disabled = True
    class Meta:
        model = MoveOutNotice
        exclude = ['updated','reason']
        
class ServiceRatingForm(forms.ModelForm):
    class Meta:
        model = ServiceRating
        exclude = ['updated','created','tenant']
        widgets = {
            'score': forms.NumberInput(attrs={
                'type': 'range','step': '1', 'min': '0', 'max': '10','id':'id_score'}),
            }