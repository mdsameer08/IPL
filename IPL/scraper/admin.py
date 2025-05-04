from django.contrib import admin
from .models import ScraperJob, ScraperLog, DataSource, ScraperConfig

@admin.register(ScraperJob)
class ScraperJobAdmin(admin.ModelAdmin):
    list_display = ('job_type', 'url', 'status', 'scheduled_time', 'start_time', 'end_time')
    search_fields = ('url',)
    list_filter = ('job_type', 'status')
    date_hierarchy = 'scheduled_time'

@admin.register(ScraperLog)
class ScraperLogAdmin(admin.ModelAdmin):
    list_display = ('job', 'timestamp', 'level', 'message')
    search_fields = ('message',)
    list_filter = ('level', 'job__job_type')
    date_hierarchy = 'timestamp'

@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_url', 'is_active')
    search_fields = ('name', 'base_url')
    list_filter = ('is_active',)

@admin.register(ScraperConfig)
class ScraperConfigAdmin(admin.ModelAdmin):
    list_display = ('data_source', 'scraper_type', 'frequency', 'is_active', 'last_run', 'next_run')
    search_fields = ('data_source__name', 'url_pattern')
    list_filter = ('scraper_type', 'frequency', 'is_active')
