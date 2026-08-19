from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class Crew(models.Model):
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class TrainType(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Train(models.Model):
    name = models.CharField(max_length=64)
    cargo_num = models.IntegerField(
        validators=[MinValueValidator(1)]
    )
    places_in_cargo = models.IntegerField(
        validators=[MinValueValidator(1)]
    )
    train_type = models.ForeignKey(
        TrainType,
        on_delete=models.PROTECT,
        related_name="trains",
    )

    def __str__(self):
        return self.name


class Station(models.Model):
    name = models.CharField(max_length=64)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name="routes_from",
    )
    destination = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name="routes_to",
    )
    distance = models.IntegerField(
        validators=[MinValueValidator(1)]
    )

    def clean(self):
        if (
            self.source_id
            and self.destination_id
            and self.source_id == self.destination_id
        ):
            raise ValidationError(
                {"destination": "Source and destination must be different."}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.source} - {self.destination}"


class Journey(models.Model):
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="journeys",
    )
    train = models.ForeignKey(
        Train,
        on_delete=models.CASCADE,
        related_name="journeys",
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(
        Crew,
        related_name="journeys",
    )

    def clean(self):
        if (
            self.departure_time
            and self.arrival_time
            and self.arrival_time <= self.departure_time
        ):
            raise ValidationError(
                {
                    "arrival_time": (
                        "Arrival time must be later than departure time."
                    )
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.route}: "
            f"{self.departure_time} - {self.arrival_time}"
        )


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )

    def __str__(self):
        return f"Order {self.pk} - {self.user}"


class Ticket(models.Model):
    cargo = models.IntegerField(
        validators=[MinValueValidator(1)]
    )
    seat = models.IntegerField(
        validators=[MinValueValidator(1)]
    )
    journey = models.ForeignKey(
        Journey,
        on_delete=models.CASCADE,
        related_name="tickets",
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="tickets",
    )

    def clean(self):
        if not self.journey_id:
            return

        train = self.journey.train

        if self.cargo > train.cargo_num:
            raise ValidationError(
                {
                    "cargo": (
                        f"Cargo number must be between "
                        f"1 and {train.cargo_num}."
                    )
                }
            )

        if self.seat > train.places_in_cargo:
            raise ValidationError(
                {
                    "seat": (
                        f"Seat number must be between "
                        f"1 and {train.places_in_cargo}."
                    )
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"Journey {self.journey_id}: "
            f"cargo {self.cargo}, seat {self.seat}"
        )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["cargo", "seat", "journey"],
                name="unique_cargo_seat_journey",
            )
        ]
