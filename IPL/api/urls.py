from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TeamViewSet, PlayerViewSet, StadiumViewSet, MatchViewSet,
    PredictionViewSet, PlayerPredictionViewSet
)

router = DefaultRouter()
router.register(r'teams', TeamViewSet)
router.register(r'players', PlayerViewSet)
router.register(r'stadiums', StadiumViewSet)
router.register(r'matches', MatchViewSet)
router.register(r'predictions', PredictionViewSet)
router.register(r'player-predictions', PlayerPredictionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]