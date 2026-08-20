from rest_framework.routers import DefaultRouter

from railway.views import (
    TrainTypeViewSet,
    CrewViewSet,
    StationViewSet,
    RouteViewSet,
    TrainViewSet,
    JourneyViewSet,
    OrderViewSet,
)

router = DefaultRouter()

router.register("train-types", TrainTypeViewSet)
router.register("crew", CrewViewSet)
router.register("stations", StationViewSet)
router.register("routes", RouteViewSet)
router.register("trains", TrainViewSet)
router.register("journeys", JourneyViewSet)
router.register("orders", OrderViewSet, basename="order")

urlpatterns = router.urls
