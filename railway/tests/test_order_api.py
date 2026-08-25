from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIClient

from railway.models import (
    Journey,
    Order,
    Route,
    Station,
    Ticket,
    Train,
    TrainType,
)


ORDER_URL = reverse("railway:order-list")


def sample_journey():
    source = Station.objects.create(
        name="Kyiv",
        latitude=50.45,
        longitude=30.52,
    )

    destination = Station.objects.create(
        name="Lviv",
        latitude=49.84,
        longitude=24.03,
    )

    route = Route.objects.create(
        source=source,
        destination=destination,
        distance=500,
    )

    train_type = TrainType.objects.create(
        name="Intercity",
    )

    train = Train.objects.create(
        name="Test train",
        cargo_num=2,
        places_in_cargo=3,
        train_type=train_type,
    )

    return Journey.objects.create(
        route=route,
        train=train,
        departure_time=timezone.make_aware(
            datetime(2026, 8, 21, 10, 0)
        ),
        arrival_time=timezone.make_aware(
            datetime(2026, 8, 21, 15, 0)
        ),
    )


class OrderApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = get_user_model().objects.create_user(
            email="user@test.com",
            password="test_password",
        )

        self.client.force_authenticate(self.user)

    def test_create_order(self):
        journey = sample_journey()

        payload = {
            "tickets": [
                {
                    "cargo": 1,
                    "seat": 1,
                    "journey": journey.id,
                }
            ]
        }

        res = self.client.post(
            ORDER_URL,
            payload,
            format="json",
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(
            Order.objects.count(),
            1,
        )
        self.assertEqual(
            Ticket.objects.count(),
            1,
        )

    def test_user_sees_only_own_orders(self):
        other_user = get_user_model().objects.create_user(
            email="other@test.com",
            password="test_password",
        )

        Order.objects.create(
            user=self.user,
        )

        Order.objects.create(
            user=other_user,
        )

        res = self.client.get(ORDER_URL)

        self.assertEqual(
            res.data["count"],
            1,
        )

    def test_cannot_create_duplicate_ticket(self):
        journey = sample_journey()

        payload = {
            "tickets": [
                {
                    "cargo": 1,
                    "seat": 1,
                    "journey": journey.id,
                },
                {
                    "cargo": 1,
                    "seat": 1,
                    "journey": journey.id,
                },
            ]
        }

        res = self.client.post(
            ORDER_URL,
            payload,
            format="json",
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_invalid_seat(self):
        journey = sample_journey()

        payload = {
            "tickets": [
                {
                    "cargo": 1,
                    "seat": 100,
                    "journey": journey.id,
                }
            ]
        }

        res = self.client.post(
            ORDER_URL,
            payload,
            format="json",
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
