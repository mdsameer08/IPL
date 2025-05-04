from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import ScraperJob, ScraperLog, DataSource, ScraperConfig
from .serializers import (
    ScraperJobSerializer, ScraperLogSerializer, 
    DataSourceSerializer, ScraperConfigSerializer
)
from .scrapers import get_scraper

class ScraperJobViewSet(viewsets.ModelViewSet):
    """
    API endpoint for scraper jobs.
    """
    queryset = ScraperJob.objects.all()
    serializer_class = ScraperJobSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['job_type', 'status']
    search_fields = ['url']
    ordering_fields = ['scheduled_time', 'start_time', 'end_time']
    
    @action(detail=True, methods=['post'])
    def run(self, request, pk=None):
        """Run a specific scraper job."""
        job = self.get_object()
        
        if job.status == 'RUNNING':
            return Response(
                {'error': 'Job is already running'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Reset job status
        job.status = 'PENDING'
        job.start_time = None
        job.end_time = None
        job.error_message = None
        job.save()
        
        # Run the job
        scraper = get_scraper(job.job_type, job.id)
        if scraper:
            scraper.run()
            return Response({'status': 'Job completed'})
        else:
            return Response(
                {'error': 'Failed to create scraper'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """Get logs for a specific job."""
        job = self.get_object()
        logs = ScraperLog.objects.filter(job=job)
        serializer = ScraperLogSerializer(logs, many=True)
        return Response(serializer.data)

class ScraperLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for scraper logs.
    """
    queryset = ScraperLog.objects.all()
    serializer_class = ScraperLogSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['job', 'level']
    search_fields = ['message']
    ordering_fields = ['timestamp']

class DataSourceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for data sources.
    """
    queryset = DataSource.objects.all()
    serializer_class = DataSourceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'base_url']
    ordering_fields = ['name', 'created_at']
    
    @action(detail=True, methods=['get'])
    def configs(self, request, pk=None):
        """Get configurations for a specific data source."""
        data_source = self.get_object()
        configs = ScraperConfig.objects.filter(data_source=data_source)
        serializer = ScraperConfigSerializer(configs, many=True)
        return Response(serializer.data)

class ScraperConfigViewSet(viewsets.ModelViewSet):
    """
    API endpoint for scraper configurations.
    """
    queryset = ScraperConfig.objects.all()
    serializer_class = ScraperConfigSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['data_source', 'scraper_type', 'frequency', 'is_active']
    search_fields = ['data_source__name', 'url_pattern']
    ordering_fields = ['data_source__name', 'scraper_type', 'last_run', 'next_run']
    
    @action(detail=True, methods=['post'])
    def schedule(self, request, pk=None):
        """Schedule a job using this configuration."""
        config = self.get_object()
        
        # Create a new job
        job = ScraperJob.objects.create(
            job_type=config.scraper_type,
            url=config.url_pattern,
            status='PENDING',
            scheduled_time=timezone.now()
        )
        
        # Update the configuration's last_run
        config.last_run = timezone.now()
        config.save()
        
        return Response({
            'status': 'Job scheduled',
            'job_id': job.id
        })
