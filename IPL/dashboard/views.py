from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Q
from scraper.models import ScraperJob, ScraperLog, DataSource, ScraperConfig
from api.models import Team, Player, Match, Stadium

def index(request):
    """Dashboard home page."""
    # Get counts of various models
    context = {
        'team_count': Team.objects.count(),
        'player_count': Player.objects.count(),
        'match_count': Match.objects.count(),
        'stadium_count': Stadium.objects.count(),
        
        # Scraper stats
        'scraper_job_count': ScraperJob.objects.count(),
        'pending_jobs': ScraperJob.objects.filter(status='PENDING').count(),
        'running_jobs': ScraperJob.objects.filter(status='RUNNING').count(),
        'completed_jobs': ScraperJob.objects.filter(status='COMPLETED').count(),
        'failed_jobs': ScraperJob.objects.filter(status='FAILED').count(),
        
        # Recent activity
        'recent_jobs': ScraperJob.objects.order_by('-created_at')[:10],
        'recent_logs': ScraperLog.objects.order_by('-timestamp')[:10],
    }
    
    return render(request, 'dashboard/index.html', context)

@login_required
def scraper_jobs(request):
    """View all scraper jobs."""
    jobs = ScraperJob.objects.all().order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        jobs = jobs.filter(status=status_filter)
    
    # Filter by job type if provided
    job_type_filter = request.GET.get('job_type')
    if job_type_filter:
        jobs = jobs.filter(job_type=job_type_filter)
    
    context = {
        'jobs': jobs,
        'status_choices': ScraperJob.STATUS_CHOICES,
        'job_type_choices': ScraperJob.TYPE_CHOICES,
        'selected_status': status_filter,
        'selected_job_type': job_type_filter,
    }
    
    return render(request, 'dashboard/scraper_jobs.html', context)

@login_required
def scraper_job_detail(request, job_id):
    """View details of a specific scraper job."""
    try:
        job = ScraperJob.objects.get(id=job_id)
    except ScraperJob.DoesNotExist:
        return redirect('dashboard:scraper_jobs')
    
    logs = ScraperLog.objects.filter(job=job).order_by('-timestamp')
    
    context = {
        'job': job,
        'logs': logs,
    }
    
    return render(request, 'dashboard/scraper_job_detail.html', context)

@login_required
def data_sources(request):
    """View all data sources."""
    sources = DataSource.objects.all().order_by('name')
    
    context = {
        'sources': sources,
    }
    
    return render(request, 'dashboard/data_sources.html', context)

@login_required
def data_source_detail(request, source_id):
    """View details of a specific data source."""
    try:
        source = DataSource.objects.get(id=source_id)
    except DataSource.DoesNotExist:
        return redirect('dashboard:data_sources')
    
    configs = ScraperConfig.objects.filter(data_source=source).order_by('scraper_type')
    
    context = {
        'source': source,
        'configs': configs,
    }
    
    return render(request, 'dashboard/data_source_detail.html', context)

@login_required
def scraper_configs(request):
    """View all scraper configurations."""
    configs = ScraperConfig.objects.all().order_by('data_source__name', 'scraper_type')
    
    context = {
        'configs': configs,
    }
    
    return render(request, 'dashboard/scraper_configs.html', context)
