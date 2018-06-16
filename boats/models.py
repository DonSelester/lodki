from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

class User(AbstractUser):
    is_owner = models.BooleanField(default=False)
    is_renter = models.BooleanField(default=False)

class OwnerProfileInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    date_of_birth = models.DateField()
    phone_number = models.CharField(max_length=13, unique=True)
    avatar = models.CharField(max_length=1000)

    def __str__(self):
        return self.user.username

class RenterProfileInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    date_of_birth = models.DateField()
    phone_number = models.CharField(max_length=13, unique=True)
    avatar = models.CharField(max_length=1000)

    def __str__(self):
        return self.user.username

class privilege_m(models.Model):
    id = models.OneToOneField(User, on_delete=models.DO_NOTHING, primary_key=True)
    role_name = models.TextField()

    class Meta:
        managed = False
        db_table = 'privilege'

class Bay(models.Model):
    address = models.CharField(max_length=100, unique=True)
    sector = models.CharField(max_length=20)
    pier = models.IntegerField()
    bay_photo = models.CharField(max_length=1000)

    def __str__(self):
        return self.address

class Elling(models.Model):
    address = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=20, unique=True)
    phone_number = models.CharField(max_length=13, unique=True)
    elling_photo = models.CharField(max_length=1000)

    def __str__(self):
        return self.name

class Crew(models.Model):
    full_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    experience = models.IntegerField(default=0)
    avatar = models.CharField(max_length=1000, default='')
    recruited = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name + " - Exp: " + str(self.experience) + " years" + " - Recruited:" + str(self.recruited)

class Boat(models.Model):
    name = models.CharField(max_length=50, unique=True)
    type = models.CharField(max_length=30)
    bay_id = models.ForeignKey(Bay, default=1, on_delete=models.CASCADE)
    licence_plate = models.CharField(max_length=10, unique=True)
    owner_id = models.ForeignKey(OwnerProfileInfo, on_delete=models.CASCADE)
    price = models.IntegerField()
    date_of_registration = models.DateField()
    boat_photo = models.CharField(max_length=1000)

    def get_absolute_url(self):
        return reverse('boats:detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name + " - " + self.type

class PriceList(models.Model):
    cause = models.CharField(max_length=30, default='', primary_key=True)
    price = models.IntegerField()
    days = models.IntegerField()
    def __str__(self):
        return str(self.cause)

class RepairContract(models.Model):
    elling = models.ForeignKey(Elling, default=1, on_delete=models.CASCADE)
    boat = models.ForeignKey(Boat, on_delete=models.CASCADE)
    date_begin = models.DateField()
    date_end = models.DateField()
    repair_price = models.IntegerField(default=0)
    repair_cause = models.ForeignKey(PriceList, default='', on_delete=models.CASCADE)

    def check_overlap(self, fixed_start, fixed_end, new_start, new_end):
        overlap = False
        if new_start == fixed_end or new_end == fixed_start:  # edge case
            overlap = False
        elif (new_start >= fixed_start and new_start <= fixed_end) or (
                new_end >= fixed_start and new_end <= fixed_end):  # innner limits
            overlap = True
        elif new_start <= fixed_start and new_end >= fixed_end:  # outter limits
            overlap = True

        return overlap

    def clean(self):
        boat = Boat.objects.get(pk=self.boat.pk)
        if self.date_begin < boat.date_of_registration:
            raise ValidationError('Boat not available in this dates. Chose after this: ' + str(boat.date_of_registration))

        contracts = RentContract.objects.filter(boat=self.boat)
        repairs = RepairContract.objects.filter(boat=self.boat)
        if contracts.exists():
            for contract in contracts:
                if self.check_overlap(contract.date_begin, contract.date_end, self.date_begin, self.date_end):
                    raise ValidationError(
                        'There is an overlap with rent contract: ' + str(contract.date_begin) + '-' + str(contract.date_end))
        if repairs.exists():
            for repair in repairs:
                if self.check_overlap(repair.date_begin, repair.date_end, self.date_begin, self.date_end):
                    raise ValidationError(
                        'You already have repair contract in this dates: ' + str(repair.date_begin) + '-' + str(repair.date_end))
    def __str__(self):
        return str(self.boat) + ", " + str(self.repair_cause) + " - " + str(self.date_begin) + " : " + str(self.date_end)

class BoatCrew(models.Model):
    crew = models.ForeignKey(Crew, on_delete=models.CASCADE)
    boat = models.ForeignKey(Boat, default=1, on_delete=models.CASCADE)
    post = models.CharField(max_length=20)
    salary = models.IntegerField()
    date_take_post = models.DateField()

    def clean(self):
        boat = BoatCrew.objects.filter(boat=self.boat, post='Captain')
        if boat.exists() and self.post == 'Captain':
            raise ValidationError('This yacht already have captain')

    def __str__(self):
        return str(self.id)

class RentContract(models.Model):
    renter = models.ForeignKey(RenterProfileInfo, on_delete=models.CASCADE)
    boat = models.ForeignKey(Boat, on_delete=models.CASCADE) # blank=True,
    date_begin = models.DateField()
    date_end = models.DateField()
    total_price = models.IntegerField(default=0)

    def check_overlap(self, fixed_start, fixed_end, new_start, new_end):
        overlap = False
        if new_start == fixed_end or new_end == fixed_start:  # edge case
            overlap = False
        elif (new_start >= fixed_start and new_start <= fixed_end) or (
                new_end >= fixed_start and new_end <= fixed_end):  # innner limits
            overlap = True
        elif new_start <= fixed_start and new_end >= fixed_end:  # outter limits
            overlap = True

        return overlap

    def clean(self):
        boat = Boat.objects.get(pk=self.boat.pk)
        crewcap = BoatCrew.objects.filter(boat=self.boat, post='Captain')
        crew = BoatCrew.objects.filter(boat=self.boat)
        if not crew:
            raise ValidationError('Boat not available, there is no crew')
        if not crewcap:
            raise ValidationError('Boat not available, there is no Captain')
        if self.date_begin < boat.date_of_registration:
            raise ValidationError('Boat not available in this dates. Chose after this: ' + str(boat.date_of_registration))
        if self.date_end <= self.date_begin:
            raise ValidationError('Ending date must be after starting date')

        contracts = RentContract.objects.filter(boat=self.boat)
        repairs = RepairContract.objects.filter(boat=self.boat)
        if contracts.exists():
            for contract in contracts:
                if self.check_overlap(contract.date_begin, contract.date_end, self.date_begin, self.date_end):
                    raise ValidationError(
                        'There is an overlap with another contract: ' + str(contract.date_begin) + '-' + str(contract.date_end))
        if repairs.exists():
            for repair in repairs:
                if self.check_overlap(repair.date_begin, repair.date_end, self.date_begin, self.date_end):
                    raise ValidationError(
                        'There is an overlap with repair contract: ' + str(repair.date_begin) + '-' + str(repair.date_end))
    def __str__(self):
        return str(self.id) + " - " + str(self.date_begin) + " : " + str(self.date_end)

class Competitions(models.Model):
    comp_title = models.CharField(max_length=100)
    member_boat_id = models.ForeignKey(Boat, on_delete=models.CASCADE)
    comp_type = models.CharField(max_length=20)
    date = models.DateField()
    place = models.IntegerField()
    logo = models.CharField(max_length=1000)

    def __str__(self):
        return self.comp_title
