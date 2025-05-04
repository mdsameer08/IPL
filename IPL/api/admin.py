from django.contrib import admin
from .models import (
    Team, Player, Stadium, Match, Innings, 
    PlayerPerformance, Prediction, PlayerPrediction
)

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'home_venue', 'captain')
    search_fields = ('name', 'short_name')
    list_filter = ('created_at',)

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'team', 'role', 'nationality')
    search_fields = ('name', 'nationality')
    list_filter = ('team', 'role', 'nationality')

@admin.register(Stadium)
class StadiumAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'country', 'capacity')
    search_fields = ('name', 'city', 'country')
    list_filter = ('country',)

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('match_number', 'season', 'date', 'team_home', 'team_away', 'venue', 'status')
    search_fields = ('team_home__name', 'team_away__name', 'venue__name')
    list_filter = ('season', 'status', 'date')
    date_hierarchy = 'date'

@admin.register(Innings)
class InningsAdmin(admin.ModelAdmin):
    list_display = ('match', 'innings_number', 'batting_team', 'bowling_team', 'runs', 'wickets', 'overs')
    search_fields = ('match__team_home__name', 'match__team_away__name')
    list_filter = ('innings_number',)

@admin.register(PlayerPerformance)
class PlayerPerformanceAdmin(admin.ModelAdmin):
    list_display = ('player', 'match', 'runs_scored', 'wickets')
    search_fields = ('player__name', 'match__team_home__name', 'match__team_away__name')
    list_filter = ('player__team', 'match__season')

@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ('match', 'predicted_winner', 'win_probability', 'was_correct')
    search_fields = ('match__team_home__name', 'match__team_away__name', 'predicted_winner__name')
    list_filter = ('was_correct', 'model_version')

@admin.register(PlayerPrediction)
class PlayerPredictionAdmin(admin.ModelAdmin):
    list_display = ('player', 'match', 'predicted_runs', 'predicted_wickets')
    search_fields = ('player__name', 'match__team_home__name', 'match__team_away__name')
    list_filter = ('model_version',)
