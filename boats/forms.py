from django import forms
from .models import OwnerProfileInfo, RenterProfileInfo, User, Boat, RentContract, BoatCrew, RepairContract, Crew
from django.utils import timezone

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']

class OwnerProfileInfoForm(forms.ModelForm):

    class Meta():
        model = OwnerProfileInfo
        fields = ('date_of_birth', 'phone_number', 'avatar')

class RenterProfileInfoForm(forms.ModelForm):

    class Meta():
        model = RenterProfileInfo
        fields = ('date_of_birth', 'phone_number', 'avatar')

class BoatForm(forms.ModelForm):
    #owner_id = forms.IntegerField(required=False, widget=forms.HiddenInput())
    type = forms.ChoiceField(widget=forms.Select(), choices=([('Go-Fast Boat', 'Go-Fast Boat'),
                                                              ('Luxury Yacht', 'Luxury Yacht'),
                                                              ('Cabin cruiser', 'Cabin cruiser'),
                                                              ('Yacht', 'Yacht'), ]))
    date_of_registration = forms.DateField(widget=forms.HiddenInput(), required=False,
                                     initial=timezone.localtime(timezone.now()).date())
    class Meta:
        model = Boat
        fields = ['name', 'type', 'licence_plate', 'price', 'date_of_registration', 'boat_photo', 'bay_id', 'owner_id']

class RentForm(forms.ModelForm):
    #renter = forms.IntegerField(required=False, widget=forms.HiddenInput())
    #boat = forms.IntegerField(required=False, widget=forms.HiddenInput())
    #total_price = forms.IntegerField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = RentContract
        fields = ['date_begin', 'date_end', 'renter', 'boat', 'total_price']

class CrewContractForm(forms.ModelForm):
    post = forms.ChoiceField(widget=forms.Select(), choices=([('Sailor', 'Sailor'),
                                                                  ('Lieutenant', 'Lieutenant'),
                                                                  ('Midshipman', 'Midshipman'),
                                                                  ('Navigator', 'Navigator'),
                                                                  ('Captain', 'Captain'), ]))
    date_take_post = forms.DateField(widget=forms.HiddenInput(), required=False, initial=timezone.localtime(timezone.now()).date())
    class Meta:
        model = BoatCrew
        fields = ['crew', 'boat', 'post', 'salary', 'date_take_post']

    def __init__(self, *args, **kwargs):
        super(CrewContractForm, self).__init__(*args, **kwargs)
        self.fields["crew"].queryset = Crew.objects.filter(recruited=False)

class RepairContractForm(forms.ModelForm):
    date_end = forms.DateField(widget=forms.HiddenInput(), required=False)
    class Meta:
        model = RepairContract
        fields = ['elling', 'boat', 'date_begin', 'date_end', 'repair_price', 'repair_cause']

    def __init__(self, u_id, *args, **kwargs):
        super(RepairContractForm, self).__init__(*args, **kwargs)
        self.fields["boat"].queryset = Boat.objects.filter(owner_id=u_id)

