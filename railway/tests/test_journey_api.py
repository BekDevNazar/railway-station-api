from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIClient

from railway.models import (
    Journey,
    Route,
    Station,
    Train,
    TrainType,
)


JOURNEY_URL = reverse("railway:journey-list")


def sample_station(
    name="Kyiv",
    latitude=50.45,
    longitude=30.52,
):
    return Station.objects.create(
        name=name,
        latitude=latitude,
        longitude=longitude,
    )


def sample_route(
    source,
    destination,
    distance=500,
):
    return Route.objects.create(
        source=source,
        destination=destination,
        distance=distance,
    )


def sample_train(
    name="Test train",
    cargo_num=2,
    places_in_cargo=3,
):
    train_type = TrainType.objects.create(
        name="Intercity",
    )

    return Train.objects.create(
        name=name,
        cargo_num=cargo_num,
        places_in_cargo=places_in_cargo,
        train_type=train_type,
    )


def sample_journey(
    route,
    train=None,
    departure_time=None,
    arrival_time=None,
):
    if train is None:
        train = sample_train()

    if departure_time is None:
        departure_time = timezone.make_aware(
            datetime(2026, 8, 21, 10, 0)
        )

    if arrival_time is None:
        arrival_time = timezone.make_aware(
            datetime(2026, 8, 21, 15, 0)
        )

    return Journey.objects.create(
        route=route,
        train=train,
        departure_time=departure_time,
        arrival_time=arrival_time,
    )


class JourneyApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = get_user_model().objects.create_user(
            email="user@test.com",
            password="test_password",
        )

        self.client.force_authenticate(self.user)

    def test_filter_journey_by_source(self):
        kyiv = sample_station(name="Kyiv")
        lviv = sample_station(name="Lviv")
        odesa = sample_station(name="Odesa")
        dnipro = sample_station(name="Dnipro")

        route_1 = sample_route(
            kyiv,
            lviv,
        )
        route_2 = sample_route(
            odesa,
            dnipro,
        )

        journey_1 = sample_journey(route_1)
        journey_2 = sample_journey(route_2)

        res = self.client.get(
            JOURNEY_URL,
            {"source": "Kyiv"},
        )

        journey_ids = [
            journey["id"]
            for journey in res.data
        ]

        self.assertIn(
            journey_1.id,
            journey_ids,
        )
        self.assertNotIn(
            journey_2.id,
            journey_ids,
        )

    def test_filter_journey_by_destination(self):
        kyiv = sample_station(name="Kyiv")
        lviv = sample_station(name="Lviv")
        odesa = sample_station(name="Odesa")

        route_1 = sample_route(
            kyiv,
            lviv,
        )
        route_2 = sample_route(
            kyiv,
            odesa,
        )

        journey_1 = sample_journey(route_1)
        journey_2 = sample_journey(route_2)

        res = self.client.get(
            JOURNEY_URL,
            {"destination": "Lviv"},
        )

        journey_ids = [
            journey["id"]
            for journey in res.data
        ]

        self.assertIn(
            journey_1.id,
            journey_ids,
        )
        self.assertNotIn(
            journey_2.id,
            journey_ids,
        )

    def test_tickets_available(self):
        kyiv = sample_station(name="Kyiv")
        lviv = sample_station(name="Lviv")

        route = sample_route(
            kyiv,
            lviv,
        )

        train = sample_train(
            cargo_num=2,
            places_in_cargo=3,
        )

        sample_journey(
            route,
            train,
        )

        res = self.client.get(JOURNEY_URL)

        self.assertEqual(
            res.data[0]["tickets_available"],
            6,
        )


class AdminJourneyApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.admin = get_user_model().objects.create_user(
            email="admin@test.com",
            password="test_password",
            is_staff=True,
        )

        self.client.force_authenticate(self.admin)

    def test_invalid_journey_time(self):
        kyiv = sample_station(name="Kyiv")
        lviv = sample_station(name="Lviv")

        route = sample_route(
            kyiv,
            lviv,
        )

        train = sample_train()

        payload = {
            "route": route.id,
            "train": train.id,
            "departure_time": "2026-08-21T15:00:00Z",
            "arrival_time": "2026-08-21T10:00:00Z",
            "crew": [],
        }

        res = self.client.post(
            JOURNEY_URL,
            payload,
            format="json",
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
