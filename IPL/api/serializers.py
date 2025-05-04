from rest_framework import serializers
from .models import (
    Team, Player, Stadium, Match, Innings, 
    PlayerPerformance, Prediction, PlayerPrediction
)

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'

class PlayerSerializer(serializers.ModelSerializer):
    team_name = serializers.ReadOnlyField(source='team.name')
    
    class Meta:
        model = Player
        fields = '__all__'

class StadiumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stadium
        fields = '__all__'

class InningsSerializer(serializers.ModelSerializer):
    batting_team_name = serializers.ReadOnlyField(source='batting_team.name')
    bowling_team_name = serializers.ReadOnlyField(source='bowling_team.name')
    
    class Meta:
        model = Innings
        fields = '__all__'

class PlayerPerformanceSerializer(serializers.ModelSerializer):
    player_name = serializers.ReadOnlyField(source='player.name')
    
    class Meta:
        model = PlayerPerformance
        fields = '__all__'

class MatchSerializer(serializers.ModelSerializer):
    team_home_name = serializers.ReadOnlyField(source='team_home.name')
    team_away_name = serializers.ReadOnlyField(source='team_away.name')
    venue_name = serializers.ReadOnlyField(source='venue.name')
    
    class Meta:
        model = Match
        fields = '__all__'

class MatchDetailSerializer(serializers.ModelSerializer):
    team_home = TeamSerializer(read_only=True)
    team_away = TeamSerializer(read_only=True)
    venue = StadiumSerializer(read_only=True)
    innings = InningsSerializer(many=True, read_only=True)
    player_performances = PlayerPerformanceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Match
        fields = '__all__'

class PredictionSerializer(serializers.ModelSerializer):
    match_details = serializers.ReadOnlyField(source='match.__str__')
    predicted_winner_name = serializers.ReadOnlyField(source='predicted_winner.name')
    
    class Meta:
        model = Prediction
        fields = '__all__'

class PlayerPredictionSerializer(serializers.ModelSerializer):
    player_name = serializers.ReadOnlyField(source='player.name')
    match_details = serializers.ReadOnlyField(source='match.__str__')
    
    class Meta:
        model = PlayerPrediction
        fields = '__all__'