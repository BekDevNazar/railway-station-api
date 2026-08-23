from django.db.models import F, Count
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from railway.models import TrainType, Crew, Station, Route, Train, Journey, Order
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from railway.permissions import IsAdminOrAuthenticatedReadOnly
from railway.serializers import (
    TrainTypeSerializer,
    CrewSerializer,
    StationSerializer,
    RouteDetailSerializer,
    RouteSerializer,
    TrainDetailSerializer,
    TrainSerializer,
    JourneyDetailSerializer,
    JourneySerializer,
    OrderSerializer,
    RouteListSerializer,
    TrainListSerializer,
    JourneyListSerializer,
    OrderListSerializer, TrainImageSerializer,
)


class TrainTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer
    permission_classes = (IsAdminOrAuthenticatedReadOnly,)


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (IsAdminOrAuthenticatedReadOnly,)


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    permission_classes = (IsAdminOrAuthenticatedReadOnly,)


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related(
        "source",
        "destination"
        )
    permission_classes = (IsAdminOrAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer

        if self.action == "retrieve":
            return RouteDetailSerializer

        return RouteSerializer


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.all()
    permission_classes = (IsAdminOrAuthenticatedReadOnly,)

    def get_queryset(self):
        queryset = self.queryset
        if self.action == "retrieve":
            queryset = queryset.select_related("train_type")
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return TrainListSerializer

        if self.action == "retrieve":
            return TrainDetailSerializer

        if self.action == "upload_file":
            return TrainImageSerializer

        return TrainSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_file(self, request, pk=None):
        train = self.get_object()
        serializers = self.get_serializer(train, data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response(
                serializers.data,
                status=status.HTTP_200_OK)
        return Response(serializers.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = Journey.objects.all()
    permission_classes = (IsAdminOrAuthenticatedReadOnly,)

    def get_queryset(self):
        queryset = self.queryset
        date = self.request.query_params.get("date")
        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")

        if date:
            queryset = queryset.filter(departure_time__date=date)

        if source:
            queryset = queryset.filter(route__source__name__icontains=source)

        if destination:
            queryset = queryset.filter(route__destination__name__icontains=destination)

        if self.action == "list":
            queryset = (
                queryset
                .select_related(
                    "route__source",
                    "route__destination",
                )
                .prefetch_related("crew")
                .annotate(
                    tickets_available=(
                            F("train__cargo_num")
                            * F("train__places_in_cargo")
                            - Count("tickets")
                    )
                )
            )

        if self.action == "retrieve":
            queryset = queryset.select_related(
                "route__source",
                "route__destination",
                "train__train_type",
            ).prefetch_related("crew", "tickets")

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return JourneyListSerializer

        if self.action == "retrieve":
            return JourneyDetailSerializer

        return JourneySerializer


class OrderPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class OrderViewSet(viewsets.GenericViewSet,
                   mixins.ListModelMixin,
                   mixins.CreateModelMixin):
    permission_classes = (IsAuthenticated,)
    pagination_class = OrderPagination

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        return OrderSerializer

    def get_queryset(self):
        queryset = (Order.objects.filter(user=self.request.user)
                    .order_by("-created_at"))

        if self.action == "list":
            queryset = queryset.prefetch_related("tickets__journey__crew")
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
