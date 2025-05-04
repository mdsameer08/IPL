from django.db import models
from django.utils import timezone

class ScraperJob(models.Model):
    """Model representing a web scraping job."""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('RUNNING', 'Running'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    TYPE_CHOICES = [
        ('TEAM', 'Team Data'),
        ('PLAYER', 'Player Data'),
        ('MATCH', 'Match Data'),
        ('STADIUM', 'Stadium Data'),
        ('LIVE', 'Live Match Data'),
    ]
    
    job_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    url = models.URLField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    scheduled_time = models.DateTimeField(default=timezone.now)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_job_type_display()} Scraper Job - {self.status}"
    
    class Meta:
        ordering = ['-scheduled_time']

class ScraperLog(models.Model):
    """Model representing a log entry for a scraper job."""
    job = models.ForeignKey(ScraperJob, on_delete=models.CASCADE, related_name='logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    level = models.CharField(max_length=10)
    message = models.TextField()
    
    def __str__(self):
        return f"{self.timestamp} - {self.level}: {self.message[:50]}"
    
    class Meta:
        ordering = ['-timestamp']

class DataSource(models.Model):
    """Model representing a data source for scraping."""
    name = models.CharField(max_length=100)
    base_url = models.URLField()
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class ScraperConfig(models.Model):
    """Model representing configuration for a scraper."""
    FREQUENCY_CHOICES = [
        ('HOURLY', 'Hourly'),
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('MATCH_DAY', 'Match Day Only'),
    ]
    
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE, related_name='configs')
    scraper_type = models.CharField(max_length=10, choices=ScraperJob.TYPE_CHOICES)
    url_pattern = models.CharField(max_length=255)
    css_selectors = models.JSONField(blank=True, null=True)
    xpath_selectors = models.JSONField(blank=True, null=True)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)
    is_active = models.BooleanField(default=True)
    last_run = models.DateTimeField(blank=True, null=True)
    next_run = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_scraper_type_display()} Config for {self.data_source.name}"
    
    class Meta:
        ordering = ['data_source', 'scraper_type']
