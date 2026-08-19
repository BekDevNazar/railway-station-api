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
    source_name = serializers.CharField(
        source="source.name",
        read_only=True,
    )
    destination_name = serializers.CharField(
        source="destination.name",
        read_only=True,
    )

    class Meta:
        model = Route
        fields = [
            "id",
            "source",
            "source_name",
            "destination",
            "destination_name",
            "distance",
        ]


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "id",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            "id",
            "cargo",
            "seat",
            "journey",
            "order"
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
    train_name = serializers.CharField(
        source="train.name",
        read_only=True,
    )

    class Meta:
        model = Journey
        fields = [
            "id",
            "route",
            "train",
            "train_name",
            "departure_time",
            "arrival_time",
            "crew",
        ]


class TicketDetailSerializer(TicketSerializer):
    journey = JourneySerializer(read_only=True)
    order = OrderSerializer(read_only=True)


class JourneyDetailSerializer(JourneySerializer):
    route = RouteSerializer(read_only=True)
    train = TrainDetailSerializer(read_only=True)
    crew = serializers.StringRelatedField(
        many=True,
        read_only=True,
    )
