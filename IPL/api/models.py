from django.db import models
from django.utils import timezone

class Team(models.Model):
    """Model representing an IPL team."""
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=10)
    logo = models.URLField(blank=True, null=True)
    home_venue = models.ForeignKey('Stadium', on_delete=models.SET_NULL, null=True, related_name='home_teams')
    captain = models.ForeignKey('Player', on_delete=models.SET_NULL, null=True, related_name='captain_of')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class Player(models.Model):
    """Model representing an IPL player."""
    ROLE_CHOICES = [
        ('BAT', 'Batsman'),
        ('BWL', 'Bowler'),
        ('AR', 'All-Rounder'),
        ('WK', 'Wicket Keeper'),
    ]
    
    name = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='players')
    role = models.CharField(max_length=3, choices=ROLE_CHOICES)
    batting_style = models.CharField(max_length=50, blank=True, null=True)
    bowling_style = models.CharField(max_length=50, blank=True, null=True)
    nationality = models.CharField(max_length=50)
    date_of_birth = models.DateField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.team.short_name})"
    
    class Meta:
        ordering = ['name']

class Stadium(models.Model):
    """Model representing a cricket stadium."""
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    country = models.CharField(max_length=50, default='India')
    capacity = models.PositiveIntegerField(blank=True, null=True)
    pitch_type = models.CharField(max_length=50, blank=True, null=True)
    average_first_innings_score = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name}, {self.city}"
    
    class Meta:
        ordering = ['name']

class Match(models.Model):
    """Model representing an IPL match."""
    MATCH_STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('LIVE', 'Live'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    match_number = models.PositiveIntegerField()
    season = models.PositiveIntegerField()
    date = models.DateField()
    time = models.TimeField()
    team_home = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_matches')
    team_away = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_matches')
    venue = models.ForeignKey(Stadium, on_delete=models.CASCADE, related_name='matches')
    toss_winner = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='toss_won', blank=True, null=True)
    toss_decision = models.CharField(max_length=10, blank=True, null=True)
    match_winner = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_won', blank=True, null=True)
    win_type = models.CharField(max_length=20, blank=True, null=True)
    win_margin = models.PositiveIntegerField(blank=True, null=True)
    player_of_match = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='player_of_match_awards', blank=True, null=True)
    status = models.CharField(max_length=10, choices=MATCH_STATUS_CHOICES, default='SCHEDULED')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.team_home.short_name} vs {self.team_away.short_name} - {self.date}"
    
    class Meta:
        ordering = ['-date', '-time']
        verbose_name_plural = 'Matches'

class Innings(models.Model):
    """Model representing an innings in a match."""
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='innings')
    batting_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='batting_innings')
    bowling_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='bowling_innings')
    innings_number = models.PositiveIntegerField()
    runs = models.PositiveIntegerField(default=0)
    wickets = models.PositiveIntegerField(default=0)
    overs = models.FloatField(default=0)
    extras = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.match} - Innings {self.innings_number}"
    
    class Meta:
        ordering = ['match', 'innings_number']
        verbose_name_plural = 'Innings'

class PlayerPerformance(models.Model):
    """Model representing a player's performance in a match."""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='performances')
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='player_performances')
    innings = models.ForeignKey(Innings, on_delete=models.CASCADE, related_name='player_performances')
    
    # Batting stats
    batting_position = models.PositiveIntegerField(blank=True, null=True)
    runs_scored = models.PositiveIntegerField(default=0)
    balls_faced = models.PositiveIntegerField(default=0)
    fours = models.PositiveIntegerField(default=0)
    sixes = models.PositiveIntegerField(default=0)
    how_out = models.CharField(max_length=50, blank=True, null=True)
    
    # Bowling stats
    overs_bowled = models.FloatField(default=0)
    maidens = models.PositiveIntegerField(default=0)
    runs_conceded = models.PositiveIntegerField(default=0)
    wickets = models.PositiveIntegerField(default=0)
    economy = models.FloatField(blank=True, null=True)
    
    # Fielding stats
    catches = models.PositiveIntegerField(default=0)
    run_outs = models.PositiveIntegerField(default=0)
    stumpings = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.player} - {self.match}"
    
    class Meta:
        ordering = ['match', 'innings']

class Prediction(models.Model):
    """Model representing a match prediction."""
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='predictions')
    predicted_winner = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='predicted_wins')
    win_probability = models.FloatField()
    predicted_score_team1 = models.PositiveIntegerField()
    predicted_score_team2 = models.PositiveIntegerField()
    prediction_time = models.DateTimeField(default=timezone.now)
    reasoning = models.TextField(blank=True, null=True)
    model_version = models.CharField(max_length=50)
    was_correct = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Prediction for {self.match}"
    
    class Meta:
        ordering = ['-prediction_time']

class PlayerPrediction(models.Model):
    """Model representing a player performance prediction."""
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='player_predictions')
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='performance_predictions')
    predicted_runs = models.PositiveIntegerField(blank=True, null=True)
    predicted_wickets = models.PositiveIntegerField(blank=True, null=True)
    predicted_economy = models.FloatField(blank=True, null=True)
    predicted_strike_rate = models.FloatField(blank=True, null=True)
    prediction_time = models.DateTimeField(default=timezone.now)
    reasoning = models.TextField(blank=True, null=True)
    model_version = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Prediction for {self.player} in {self.match}"
    
    class Meta:
        ordering = ['-prediction_time']
