from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    Team, Player, Stadium, Match, Innings, 
    PlayerPerformance, Prediction, PlayerPrediction
)
from .serializers import (
    TeamSerializer, PlayerSerializer, StadiumSerializer, 
    MatchSerializer, MatchDetailSerializer, InningsSerializer, 
    PlayerPerformanceSerializer, PredictionSerializer, PlayerPredictionSerializer
)

class TeamViewSet(viewsets.ModelViewSet):
    """
    API endpoint for teams.
    """
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['name', 'short_name']
    search_fields = ['name', 'short_name']
    ordering_fields = ['name', 'created_at']
    
    @action(detail=True, methods=['get'])
    def players(self, request, pk=None):
        """Get all players for a team."""
        team = self.get_object()
        players = Player.objects.filter(team=team)
        serializer = PlayerSerializer(players, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def matches(self, request, pk=None):
        """Get all matches for a team."""
        team = self.get_object()
        matches = Match.objects.filter(team_home=team) | Match.objects.filter(team_away=team)
        serializer = MatchSerializer(matches, many=True)
        return Response(serializer.data)

class PlayerViewSet(viewsets.ModelViewSet):
    """
    API endpoint for players.
    """
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['name', 'team', 'role', 'nationality']
    search_fields = ['name', 'team__name', 'nationality']
    ordering_fields = ['name', 'team__name', 'created_at']
    
    @action(detail=True, methods=['get'])
    def performances(self, request, pk=None):
        """Get all performances for a player."""
        player = self.get_object()
        performances = PlayerPerformance.objects.filter(player=player)
        serializer = PlayerPerformanceSerializer(performances, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def predictions(self, request, pk=None):
        """Get all predictions for a player."""
        player = self.get_object()
        predictions = PlayerPrediction.objects.filter(player=player)
        serializer = PlayerPredictionSerializer(predictions, many=True)
        return Response(serializer.data)

class StadiumViewSet(viewsets.ModelViewSet):
    """
    API endpoint for stadiums.
    """
    queryset = Stadium.objects.all()
    serializer_class = StadiumSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['name', 'city', 'country']
    search_fields = ['name', 'city', 'country']
    ordering_fields = ['name', 'city', 'created_at']
    
    @action(detail=True, methods=['get'])
    def matches(self, request, pk=None):
        """Get all matches at a stadium."""
        stadium = self.get_object()
        matches = Match.objects.filter(venue=stadium)
        serializer = MatchSerializer(matches, many=True)
        return Response(serializer.data)

class MatchViewSet(viewsets.ModelViewSet):
    """
    API endpoint for matches.
    """
    queryset = Match.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['season', 'team_home', 'team_away', 'venue', 'status']
    search_fields = ['team_home__name', 'team_away__name', 'venue__name']
    ordering_fields = ['date', 'time', 'match_number', 'season']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MatchDetailSerializer
        return MatchSerializer
    
    @action(detail=True, methods=['get'])
    def innings(self, request, pk=None):
        """Get all innings for a match."""
        match = self.get_object()
        innings = Innings.objects.filter(match=match)
        serializer = InningsSerializer(innings, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def performances(self, request, pk=None):
        """Get all player performances for a match."""
        match = self.get_object()
        performances = PlayerPerformance.objects.filter(match=match)
        serializer = PlayerPerformanceSerializer(performances, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def predictions(self, request, pk=None):
        """Get all predictions for a match."""
        match = self.get_object()
        predictions = Prediction.objects.filter(match=match)
        serializer = PredictionSerializer(predictions, many=True)
        return Response(serializer.data)

class PredictionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for match predictions.
    """
    queryset = Prediction.objects.all()
    serializer_class = PredictionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['match', 'predicted_winner', 'model_version', 'was_correct']
    search_fields = ['match__team_home__name', 'match__team_away__name', 'predicted_winner__name']
    ordering_fields = ['prediction_time', 'win_probability']

class PlayerPredictionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for player performance predictions.
    """
    queryset = PlayerPrediction.objects.all()
    serializer_class = PlayerPredictionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['match', 'player', 'model_version']
    search_fields = ['player__name', 'match__team_home__name', 'match__team_away__name']
    ordering_fields = ['prediction_time', 'predicted_runs', 'predicted_wickets']
