from django.contrib import admin

from railway.models import (
    Crew,
    Journey,
    Order,
    Route,
    Station,
    Ticket,
    Train,
    TrainType,
)


@admin.register(TrainType)
class TrainTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


@admin.register(Crew)
class CrewAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name")
    search_fields = ("first_name", "last_name")


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "latitude", "longitude")
    search_fields = ("name",)


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("id", "source", "destination", "distance")


@admin.register(Train)
class TrainAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "train_type",
        "cargo_num",
        "places_in_cargo",
    )
    search_fields = ("name",)


@admin.register(Journey)
class JourneyAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "route",
        "train",
        "departure_time",
        "arrival_time",
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at")


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "journey",
        "cargo",
        "seat",
        "order",
    )
