from django.db import transaction
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from railway.models import (
    Crew,
    Train,
    TrainType,
    Station,
    Route,
    Order,
    Ticket,
    Journey,
)


class TrainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = [
            "id",
            "name",
        ]


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = [
            "id",
            "first_name",
            "last_name",
        ]


class TrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = [
            "id",
            "name",
            "cargo_num",
            "places_in_cargo",
            "train_type",
        ]


class TrainListSerializer(TrainSerializer):
    train_type = serializers.SlugRelatedField(
        read_only=True,
        slug_field="name",
    )


class TrainDetailSerializer(TrainSerializer):
    train_type = TrainTypeSerializer(read_only=True)


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = [
            "id",
            "name",
            "latitude",
            "longitude",
        ]


class RouteSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        source = attrs.get(
            "source",
            getattr(self.instance, "source", None),
        )
        destination = attrs.get(
            "destination",
            getattr(self.instance, "destination", None),
        )

        if source == destination:
            raise serializers.ValidationError(
                {
                    "destination": (
                        "Source and destination must be different."
                    )
                }
            )

        return attrs

    class Meta:
        model = Route
        fields = [
            "id",
            "source",
            "destination",
            "distance",
        ]


class RouteListSerializer(RouteSerializer):
    source = serializers.SlugRelatedField(
        read_only=True,
        slug_field="name",
    )
    destination = serializers.SlugRelatedField(
        read_only=True,
        slug_field="name",
    )


class RouteDetailSerializer(RouteSerializer):
    source = StationSerializer(read_only=True)
    destination = StationSerializer(read_only=True)


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        journey = attrs["journey"]
        train = journey.train

        if attrs["cargo"] > train.cargo_num:
            raise serializers.ValidationError(
                {
                    "cargo": (
                        f"Cargo number must be between "
                        f"1 and {train.cargo_num}."
                    )
                }
            )

        if attrs["seat"] > train.places_in_cargo:
            raise serializers.ValidationError(
                {
                    "seat": (
                        f"Seat number must be between "
                        f"1 and {train.places_in_cargo}."
                    )
                }
            )

        return attrs

    class Meta:
        model = Ticket
        fields = [
            "id",
            "cargo",
            "seat",
            "journey",
        ]

        validators = [
            UniqueTogetherValidator(
                queryset=Ticket.objects.all(),
                fields=[
                    "cargo",
                    "seat",
                    "journey",
                ],
            )
        ]


class JourneySerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        departure_time = attrs.get(
            "departure_time",
            getattr(self.instance, "departure_time", None),
        )
        arrival_time = attrs.get(
            "arrival_time",
            getattr(self.instance, "arrival_time", None),
        )

        if (
                departure_time
                and arrival_time
                and arrival_time <= departure_time
        ):
            raise serializers.ValidationError(
                {
                    "arrival_time": (
                        "Arrival time must be later than departure time."
                    )
                }
            )

        return attrs
    
    class Meta:
        model = Journey
        fields = [
            "id",
            "route",
            "train",
            "departure_time",
            "arrival_time",
            "crew",
        ]


class JourneyListSerializer(JourneySerializer):
    route = RouteListSerializer(read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ["id", "tickets", "created_at"]


    def validate(self, attrs):
        tickets = attrs.get("tickets", [])

        ticket_places = [
            (
            ticket["journey"].id,
            ticket["cargo"],
            ticket["seat"],

            ) for ticket in tickets]

        if len(ticket_places) != len(set(ticket_places)):
            raise serializers.ValidationError(
                {"tickets": "Duplicate tickets are not allowed."}
            )
        return attrs


    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class TicketListSerializer(TicketSerializer):
    journey = JourneySerializer(read_only=True)


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True,read_only=True)


class JourneyDetailSerializer(JourneySerializer):
    route = RouteDetailSerializer(read_only=True)
    train = TrainDetailSerializer(read_only=True)
    crew = serializers.StringRelatedField(
        many=True,
        read_only=True,
    )
