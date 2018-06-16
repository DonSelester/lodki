from django.views import generic
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import Group
from .models import Boat, Bay, Competitions, OwnerProfileInfo, RenterProfileInfo, RentContract, Crew, BoatCrew, RepairContract, Elling, PriceList, privilege_m
from .forms import UserForm, OwnerProfileInfoForm, RenterProfileInfoForm, BoatForm, RentForm, CrewContractForm, RepairContractForm
from django.utils import timezone
import datetime
from datetime import timedelta
from django.core.exceptions import ValidationError

def IndexView(request):
    if request.method == 'GET':
        if 'by_price' in request.GET and request.GET['by_price']:
            boats = Boat.objects.all().order_by('price')
        elif 'by_repair' in request.GET and request.GET['by_repair']:
            boats = Boat.objects.raw('SELECT Distinct b.id, b.name, b.type, b.price, b.boat_photo FROM boats_boat AS b INNER JOIN boats_repaircontract r ON b.id != r.boat_id;')
        elif 'by_popular' in request.GET and request.GET['by_popular']:
            boats = Boat.objects.raw(
                'SELECT b.id, b.name, b.type, b.price, b.boat_photo, count(r.boat_id) as count FROM boats_boat AS b INNER JOIN boats_rentcontract r ON b.id = r.boat_id group by b.id, b.name, b.type, b.price, b.boat_photo order by count desc;')
        elif 'by_names' in request.GET and request.GET['by_names']:
            boats = Boat.objects.all().order_by('name')
        elif 'by_type' in request.GET and request.GET['by_type']:
            boats = Boat.objects.all().order_by('type')
        elif 'by_price_desc' in request.GET and request.GET['by_price_desc']:
            boats = Boat.objects.all().order_by('-price')
        elif 'by_price_low' in request.GET and request.GET['by_price_low'] and 'by_price_top' in request.GET and request.GET['by_price_top']:
            boats = Boat.objects.all().filter(price__gte=request.GET['by_price_low'], price__lte=request.GET['by_price_top']).order_by('price')
        else:
            boats = Boat.objects.all()
        redirect('boats/index.html')
        context = {'all_boats': boats, }
        return render(request, 'boats/index.html', context)
    else:
        boats = Boat.objects.all()
        context = {'all_boats': boats, }
        return render(request, 'boats/index.html', context)

def boat_detail(request,boat_id_id):
    boat = get_object_or_404(Boat, pk=boat_id_id)
    bay = Bay.objects.get(pk=boat.bay_id_id)
    owner = OwnerProfileInfo.objects.get(pk=boat.owner_id_id)
    contracts = RentContract.objects.filter(boat_id=boat_id_id)
    repairs = RepairContract.objects.filter(boat_id=boat_id_id)
    crews = Crew.objects.all()
    cap = BoatCrew.objects.filter(boat_id=boat_id_id, post='Captain')
    boat_crews = BoatCrew.objects.filter(boat_id=boat_id_id)
    if request.method == "POST":
        if 'new_salary' in request.POST and request.POST['new_salary']:
            BoatCrew.objects.filter(crew_id=request.POST['crew_id_id']).update(salary=request.POST['new_salary'])
        if 'new_post' in request.POST and request.POST['new_post']:
            BoatCrew.objects.filter(crew_id=request.POST['crew_id_id']).update(post=request.POST['new_post'])
        if 'crew_id' in request.POST and request.POST['crew_id']:
            BoatCrew.objects.get(crew=request.POST['crew_id']).delete()
            Crew.objects.filter(pk=request.POST['crew_id']).update(recruited=False)
    context = {'boat': boat, 'bay': bay, 'owner': owner, 'contracts': contracts, 'boat_crews': boat_crews, 'crews': crews, 'repairs': repairs, 'cap': cap,}
    return render(request, 'boats/detail.html', context)

class BayDetailView(generic.DetailView):
    model = Bay
    template_name = 'boats/bay_detail.html'

def Competetions(request):
    comp = Competitions.objects.all()
    boat = Boat.objects.all()
    context = {'competitions': comp, 'boats': boat, }
    return render(request, 'boats/competitions.html', context)

def bays(request):
    bays = Bay.objects.all()
    return render(request, 'boats/bays.html', {'bays': bays, })

def elling(request):
    ell = Elling.objects.all()
    context = {'elling': ell, }
    return render(request, 'boats/elling.html', context)

def elling_detail(request, el_id):
    ell = Elling.objects.get(pk=el_id)
    prices = PriceList.objects.all()
    deal = False
    if request.method == "POST":
        repair_form = RepairContractForm(data=request.POST, u_id=request.user.id)
        if repair_form.is_valid():
            repair = repair_form.save()
            if request.user.id == repair.boat.owner_id_id:
                caus = PriceList.objects.get(cause=repair.repair_cause)
                repair.elling = ell
                repair.date_end = repair.date_begin + timedelta(days=caus.days)
                repair.repair_price = caus.price
                repair.save()
                deal = True
            else:
                raise ValidationError('This is not your boat')
        else:
            print(repair_form.errors)
    else:
        repair_form = RepairContractForm(initial={'elling': ell, 'date_end': datetime.date.today(),}, u_id=request.user.id)

    context = { 'repair_form': repair_form, 'deal': deal, 'elling': ell, 'prices': prices,}
    return render(request, 'boats/elling_detail.html', context)

def CrewIndex(request):
    crews = Crew.objects.all()
    context = {'crews': crews,}
    return render(request, 'boats/crew.html', context)

def CrewDetail(request, cr_id):
    crew = Crew.objects.get(pk=cr_id)
    contracts = BoatCrew.objects.filter(crew_id=cr_id)
    boats = Boat.objects.all()
    context = {'crew': crew, 'contracts': contracts, 'boats': boats,}
    return render(request, 'boats/crew_profile.html', context)

@login_required
def rent_contract(request, user_id_id, boat_id_id):
    rented = False
    renter_id = RenterProfileInfo.objects.get(pk=user_id_id)
    priv = privilege_m.objects.filter(id=request.user.id, role_name='RenterUser')
    boat_id = Boat.objects.get(pk=boat_id_id)
    hacker = False
    if request.method == "POST":
        if priv:
            rent_form = RentForm(data=request.POST)
            if rent_form.is_valid():
                rent = rent_form.save()
                total = rent.date_end - rent.date_begin
                rent.total_price = total.days * boat_id.price
                rent.renter = renter_id
                rent.boat = boat_id
                rent.save()
                rented = True
            else:
                print(rent_form.errors)
        else:
            hacker = True
            rent_form = BoatForm(initial={'boat': boat_id, 'renter': renter_id})
    else:
        rent_form = RentForm(initial={'boat': boat_id, 'renter': renter_id})
    return render(request, 'boats/rent_contract.html', {'rent_form': rent_form, 'renter': renter_id, 'rented': rented, 'hacker': hacker})

@login_required
def add_boat(request, user_id_id):
    if request.user.is_owner:
        added = False
        owner = OwnerProfileInfo.objects.get(pk=user_id_id)
        priv = privilege_m.objects.filter(id=request.user.id, role_name='OwnerUser')
        hacker = False
        if request.method == "POST":
            if priv:
                boat_form = BoatForm(data=request.POST)
                if boat_form.is_valid():
                    boat = boat_form.save()
                    boat.owner_id = owner
                    if boat.type == 'Yacht':
                        boat.bay_id = Bay.objects.get(pk=2)
                    elif boat.type == 'Go-Fast Boat' or boat.type == 'Cabin cruiser':
                        boat.bay_id = Bay.objects.get(pk=1)
                    else:
                        boat.bay_id = Bay.objects.get(pk=3)
                    boat.date_of_registration = timezone.localtime(timezone.now()).date()
                    boat.save()
                    added = True
                else:
                    print(boat_form.errors, boat_form.errors)
            else:
                hacker = True
                boat_form = BoatForm(initial={'owner_id': owner})
        else:
            boat_form = BoatForm(initial={'owner_id': owner})

        return render(request, 'boats/add_boat.html', {'boat_form': boat_form, 'owner': owner, 'added': added, 'hacker': hacker})
    else:
        return render(request, 'boats/add_boat.html',{'wrong': 'Something goes wrong!'})
@login_required
def boat_info(request, boat_id_id):
    if request.method == 'POST':
        if 'new_price' in request.POST and request.POST['new_price']:
            Boat.objects.filter(pk=boat_id_id, owner_id=request.user.id).update(price=request.POST['new_price'])
    boat = Boat.objects.get(id=boat_id_id)
    info = Boat.objects.raw('SELECT * FROM maintance_month(%s)' % boat_id_id)
    crews = BoatCrew.objects.filter(boat_id=boat_id_id).values('date_take_post', 'salary')
    context = {'boat': boat, 'crews': crews, 'infos': info}
    return render(request, 'boats/boat_info.html', context)

@login_required
def crew_contract(request, boat_id_id):
    recruited = False
    boat = Boat.objects.get(pk=boat_id_id)
    priv = privilege_m.objects.filter(id=request.user.id, role_name='OwnerUser')
    hacker = False
    if request.method == "POST":
        if priv:
            cr_contr_form = CrewContractForm(data=request.POST)
            if cr_contr_form.is_valid():
                cr_cntr = cr_contr_form.save()
                cr_cntr.boat = boat
                cr_cntr.save()
                recruited = True
            else:
                print(cr_contr_form.errors, cr_contr_form.errors)
        else:
            hacker = True
            cr_contr_form = BoatForm(initial={'boat': boat})
    else:
        cr_contr_form = CrewContractForm(initial={'boat': boat})

    return render(request, 'boats/crew_contract.html', {'cr_contr_form': cr_contr_form, 'boat': boat,'recruited': recruited, 'hacker': hacker})

@login_required
def user_logout(request):
    logout(request)
    return redirect('boats:index')

@login_required
def owner_profile(request, user_id_id):
    user_info = OwnerProfileInfo.objects.get(user_id=user_id_id)
    boats = Boat.objects.all()
    context = {'user_info': user_info, 'boats': boats, }
    return render(request, 'boats/owner_profile.html', context)

@login_required
def renter_profile(request, user_id_id):
    user_info = RenterProfileInfo.objects.get(user_id=user_id_id)
    contracts = RentContract.objects.filter(renter_id=user_id_id)
    boats = Boat.objects.all()
    context = {'user_info': user_info, 'contracts': contracts, 'boats': boats, }
    return render(request, 'boats/renter_profile.html', context)

def register(request):
    return render(request, 'boats/registration_form.html')

def register_owner(request):

    registered = False
    my_group = Group.objects.get(name='Owners')

    if request.method == "POST":
        user_form = UserForm(data=request.POST)
        profile_form = OwnerProfileInfoForm(data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():

            user = user_form.save()
            my_group.user_set.add(user.id)
            user.is_owner = True
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = OwnerProfileInfoForm()

    return render(request, 'boats/registration_form_owner.html',
                  {'user_form': user_form,
                   'profile_form': profile_form,
                   'registered': registered})

def register_renter(request):

    registered = False
    my_group = Group.objects.get(name='Renters')

    if request.method == "POST":
        user_form = UserForm(data=request.POST)
        profile_form = RenterProfileInfoForm(data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():

            user = user_form.save()
            my_group.user_set.add(user.id)
            user.is_renter = True
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = RenterProfileInfoForm()

    return render(request, 'boats/registration_form_renter.html',
                  {'user_form': user_form,
                   'profile_form': profile_form,
                   'registered': registered})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username,password=password)

        if user:
            if user.is_active:
                login(request,user)
                return redirect('boats:index')
            else:
                return HttpResponse('Account not active')
        else:
            print("Username: {} and password {}".format(username,password))
            return HttpResponse("invalid login details supplied!")
    else:
        return render(request, 'boats/login.html')
