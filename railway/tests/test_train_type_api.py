from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status

from railway.models import Train, TrainType

TRAIN = reverse("railway:train-list")


def detail_url(train_id):
    return reverse("railway:train-detail", args=[train_id])


def image_upload_url(train_id):
    return reverse("railway:train-upload-file", args=[train_id])


def sample_train(**params):
    train_type = TrainType.objects.create(name="TEST")

    defaults = {
        "name": "Test",
        "cargo_num": 12,
        "places_in_cargo": 12,
        "train_type": train_type
    }
    defaults.update(params)

    return Train.objects.create(**defaults)


class TestNotAuthUser(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TRAIN)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TestAuthUser(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = get_user_model().objects.create_user(
            "test@gamail.com", "test_password"
        )

        self.client.force_authenticate(self.user)

    def test_user_can_access_train_list(self):
        res = self.client.get(TRAIN)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_user_cannot_post_train(self):
        train_type = TrainType.objects.create(name="TEST")

        payload = {
            "name": "Test",
            "cargo_num": 12,
            "places_in_cargo": 12,
            "train_type": train_type.id,
        }

        res = self.client.post(
            TRAIN,
            payload,
            format="json",
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_user_can_get_train_retrieve(self):

        train = sample_train()
        url = detail_url(train.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_user_cannot_train_patch(self):
        train = sample_train()
        url = detail_url(train.id)

        payload = {
            "name": "New_name",
        }

        res = self.client.patch(
            url,
            payload,
            format="json",
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_403_FORBIDDEN,
        )


class AdminTrainTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.admin = get_user_model().objects.create_user(
            email="admin@test.com",
            password="test_password",
            is_staff=True,
        )
        self.client.force_authenticate(self.admin)

        self.train_type = TrainType.objects.create(name="Intercity")

    def test_admin_create_train(self):
        payload = {
            "name": "Test",
            "cargo_num": 12,
            "places_in_cargo": 12,
            "train_type": self.train_type.id,
        }

        res = self.client.post(TRAIN, payload)

        self.assertEqual(
            res.status_code,
            status.HTTP_201_CREATED,
        )

        train = Train.objects.get(id=res.data["id"])

        self.assertEqual(train.name, payload["name"])
        self.assertEqual(train.cargo_num, payload["cargo_num"])
        self.assertEqual(
            train.places_in_cargo,
            payload["places_in_cargo"],
        )
        self.assertEqual(train.train_type, self.train_type)
