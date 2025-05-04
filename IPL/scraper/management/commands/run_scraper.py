import logging
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from scraper.models import ScraperJob, DataSource, ScraperConfig
from scraper.scrapers import get_scraper

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Run a scraper job'

    def add_arguments(self, parser):
        parser.add_argument('--job-id', type=int, help='ID of the scraper job to run')
        parser.add_argument('--job-type', type=str, choices=['TEAM', 'PLAYER', 'MATCH', 'STADIUM', 'LIVE'], 
                            help='Type of scraper job to run')
        parser.add_argument('--url', type=str, help='URL to scrape')
        parser.add_argument('--data-source', type=str, help='Name of the data source')
        parser.add_argument('--config-id', type=int, help='ID of the scraper configuration to use')

    def handle(self, *args, **options):
        job_id = options.get('job_id')
        job_type = options.get('job_type')
        url = options.get('url')
        data_source_name = options.get('data_source')
        config_id = options.get('config_id')
        
        # If job_id is provided, run that specific job
        if job_id:
            try:
                job = ScraperJob.objects.get(id=job_id)
                self.stdout.write(self.style.SUCCESS(f'Running job {job_id} of type {job.job_type}'))
                
                scraper = get_scraper(job.job_type, job.id)
                if scraper:
                    scraper.run()
                    self.stdout.write(self.style.SUCCESS(f'Job {job_id} completed'))
                else:
                    self.stdout.write(self.style.ERROR(f'Failed to create scraper for job {job_id}'))
                
                return
            except ScraperJob.DoesNotExist:
                raise CommandError(f'ScraperJob with ID {job_id} does not exist')
        
        # If config_id is provided, use that configuration
        if config_id:
            try:
                config = ScraperConfig.objects.get(id=config_id)
                data_source = config.data_source
                job_type = config.scraper_type
                url = config.url_pattern
                
                self.stdout.write(self.style.SUCCESS(
                    f'Using configuration {config_id} for {data_source.name} - {job_type}'
                ))
            except ScraperConfig.DoesNotExist:
                raise CommandError(f'ScraperConfig with ID {config_id} does not exist')
        
        # If data_source is provided, find the appropriate configuration
        elif data_source_name and job_type:
            try:
                data_source = DataSource.objects.get(name=data_source_name)
                try:
                    config = ScraperConfig.objects.get(
                        data_source=data_source,
                        scraper_type=job_type,
                        is_active=True
                    )
                    url = config.url_pattern
                    
                    self.stdout.write(self.style.SUCCESS(
                        f'Using configuration for {data_source.name} - {job_type}'
                    ))
                except ScraperConfig.DoesNotExist:
                    if not url:
                        raise CommandError(
                            f'No active configuration found for {data_source_name} - {job_type} and no URL provided'
                        )
            except DataSource.DoesNotExist:
                if not url:
                    raise CommandError(f'DataSource {data_source_name} does not exist and no URL provided')
        
        # Ensure we have the minimum required parameters
        if not job_type or not url:
            raise CommandError('You must provide either a job ID, a configuration ID, or job type and URL')
        
        # Create a new job
        job = ScraperJob.objects.create(
            job_type=job_type,
            url=url,
            status='PENDING',
            scheduled_time=timezone.now()
        )
        
        self.stdout.write(self.style.SUCCESS(f'Created new job {job.id} of type {job_type}'))
        
        # Run the job
        scraper = get_scraper(job_type, job.id)
        if scraper:
            scraper.run()
            self.stdout.write(self.style.SUCCESS(f'Job {job.id} completed'))
        else:
            self.stdout.write(self.style.ERROR(f'Failed to create scraper for job {job.id}'))