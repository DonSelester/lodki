from django.contrib import admin
from .models import User, Bay, Boat, Competitions, OwnerProfileInfo, RenterProfileInfo, RentContract, Crew, BoatCrew, Elling, RepairContract, PriceList

admin.site.register(Bay)
admin.site.register(Boat)
admin.site.register(Competitions)
admin.site.register(OwnerProfileInfo)
admin.site.register(RenterProfileInfo)
admin.site.register(User)
admin.site.register(RentContract)
admin.site.register(Crew)
admin.site.register(BoatCrew)
admin.site.register(Elling)
admin.site.register(RepairContract)
admin.site.register(PriceList)
