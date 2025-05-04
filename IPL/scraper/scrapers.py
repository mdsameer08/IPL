import os
import time
import logging
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from django.utils import timezone
from .models import ScraperJob, ScraperLog, DataSource, ScraperConfig
from api.models import Team, Player, Stadium, Match

logger = logging.getLogger(__name__)

class BaseScraper:
    """Base class for all scrapers."""
    
    def __init__(self, job_id=None):
        self.job = None
        if job_id:
            try:
                self.job = ScraperJob.objects.get(id=job_id)
                self.job.status = 'RUNNING'
                self.job.start_time = timezone.now()
                self.job.save()
            except ScraperJob.DoesNotExist:
                logger.error(f"ScraperJob with ID {job_id} does not exist")
    
    def log(self, message, level='INFO'):
        """Log a message to the database."""
        if self.job:
            ScraperLog.objects.create(
                job=self.job,
                level=level,
                message=message
            )
        logger.log(getattr(logging, level), message)
    
    def get_soup(self, url):
        """Get BeautifulSoup object from URL."""
        try:
            response = requests.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            self.log(f"Error fetching URL {url}: {str(e)}", 'ERROR')
            if self.job:
                self.job.status = 'FAILED'
                self.job.error_message = str(e)
                self.job.end_time = timezone.now()
                self.job.save()
            return None
    
    def get_selenium_driver(self):
        """Get Selenium WebDriver."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            return driver
        except Exception as e:
            self.log(f"Error initializing Selenium WebDriver: {str(e)}", 'ERROR')
            if self.job:
                self.job.status = 'FAILED'
                self.job.error_message = str(e)
                self.job.end_time = timezone.now()
                self.job.save()
            return None
    
    def finish_job(self, status='COMPLETED', error_message=None):
        """Mark the job as finished."""
        if self.job:
            self.job.status = status
            self.job.error_message = error_message
            self.job.end_time = timezone.now()
            self.job.save()
    
    def run(self):
        """Run the scraper."""
        raise NotImplementedError("Subclasses must implement run() method")


class TeamScraper(BaseScraper):
    """Scraper for team data."""
    
    def run(self):
        """Run the team scraper."""
        if not self.job:
            self.log("No job specified", 'ERROR')
            return
        
        self.log(f"Starting team scraper for URL: {self.job.url}")
        
        try:
            soup = self.get_soup(self.job.url)
            if not soup:
                return
            
            # Example implementation - adjust based on actual website structure
            team_containers = soup.select('.team-container')
            
            for container in team_containers:
                name = container.select_one('.team-name').text.strip()
                short_name = container.select_one('.team-short-name').text.strip()
                logo = container.select_one('.team-logo img')['src']
                
                # Create or update team
                team, created = Team.objects.update_or_create(
                    name=name,
                    defaults={
                        'short_name': short_name,
                        'logo': logo
                    }
                )
                
                if created:
                    self.log(f"Created new team: {name}")
                else:
                    self.log(f"Updated team: {name}")
            
            self.finish_job()
            self.log(f"Team scraper completed successfully")
            
        except Exception as e:
            self.log(f"Error in team scraper: {str(e)}", 'ERROR')
            self.finish_job('FAILED', str(e))


class PlayerScraper(BaseScraper):
    """Scraper for player data."""
    
    def run(self):
        """Run the player scraper."""
        if not self.job:
            self.log("No job specified", 'ERROR')
            return
        
        self.log(f"Starting player scraper for URL: {self.job.url}")
        
        try:
            driver = self.get_selenium_driver()
            if not driver:
                return
            
            driver.get(self.job.url)
            
            # Wait for the page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".player-container"))
            )
            
            # Example implementation - adjust based on actual website structure
            player_elements = driver.find_elements(By.CSS_SELECTOR, ".player-container")
            
            for element in player_elements:
                name = element.find_element(By.CSS_SELECTOR, ".player-name").text
                team_name = element.find_element(By.CSS_SELECTOR, ".player-team").text
                role = element.find_element(By.CSS_SELECTOR, ".player-role").text
                
                # Map role to choices
                role_map = {
                    "Batsman": "BAT",
                    "Bowler": "BWL",
                    "All-Rounder": "AR",
                    "Wicket Keeper": "WK"
                }
                role_code = role_map.get(role, "BAT")
                
                # Get or create team
                try:
                    team = Team.objects.get(name=team_name)
                except Team.DoesNotExist:
                    self.log(f"Team {team_name} does not exist, creating placeholder", 'WARNING')
                    team = Team.objects.create(name=team_name, short_name=team_name[:3].upper())
                
                # Create or update player
                player, created = Player.objects.update_or_create(
                    name=name,
                    team=team,
                    defaults={
                        'role': role_code,
                        'nationality': 'Unknown'  # This would be scraped in a real implementation
                    }
                )
                
                if created:
                    self.log(f"Created new player: {name} ({team.name})")
                else:
                    self.log(f"Updated player: {name} ({team.name})")
            
            driver.quit()
            self.finish_job()
            self.log(f"Player scraper completed successfully")
            
        except Exception as e:
            self.log(f"Error in player scraper: {str(e)}", 'ERROR')
            self.finish_job('FAILED', str(e))
            if 'driver' in locals():
                driver.quit()


class MatchScraper(BaseScraper):
    """Scraper for match data."""
    
    def run(self):
        """Run the match scraper."""
        if not self.job:
            self.log("No job specified", 'ERROR')
            return
        
        self.log(f"Starting match scraper for URL: {self.job.url}")
        
        try:
            soup = self.get_soup(self.job.url)
            if not soup:
                return
            
            # Example implementation - adjust based on actual website structure
            match_containers = soup.select('.match-container')
            
            for container in match_containers:
                match_number = int(container.select_one('.match-number').text.strip().split('#')[1])
                season = int(container.select_one('.season').text.strip())
                date_str = container.select_one('.match-date').text.strip()
                time_str = container.select_one('.match-time').text.strip()
                
                # Parse date and time
                from datetime import datetime
                date_obj = datetime.strptime(date_str, '%d %b %Y').date()
                time_obj = datetime.strptime(time_str, '%H:%M').time()
                
                team_home_name = container.select_one('.team-home').text.strip()
                team_away_name = container.select_one('.team-away').text.strip()
                venue_name = container.select_one('.venue').text.strip()
                
                # Get or create teams and venue
                try:
                    team_home = Team.objects.get(name=team_home_name)
                except Team.DoesNotExist:
                    self.log(f"Team {team_home_name} does not exist, creating placeholder", 'WARNING')
                    team_home = Team.objects.create(name=team_home_name, short_name=team_home_name[:3].upper())
                
                try:
                    team_away = Team.objects.get(name=team_away_name)
                except Team.DoesNotExist:
                    self.log(f"Team {team_away_name} does not exist, creating placeholder", 'WARNING')
                    team_away = Team.objects.create(name=team_away_name, short_name=team_away_name[:3].upper())
                
                try:
                    venue = Stadium.objects.get(name=venue_name)
                except Stadium.DoesNotExist:
                    self.log(f"Stadium {venue_name} does not exist, creating placeholder", 'WARNING')
                    venue = Stadium.objects.create(name=venue_name, city='Unknown', country='India')
                
                # Create or update match
                match, created = Match.objects.update_or_create(
                    match_number=match_number,
                    season=season,
                    defaults={
                        'date': date_obj,
                        'time': time_obj,
                        'team_home': team_home,
                        'team_away': team_away,
                        'venue': venue,
                        'status': 'SCHEDULED'
                    }
                )
                
                if created:
                    self.log(f"Created new match: {match}")
                else:
                    self.log(f"Updated match: {match}")
            
            self.finish_job()
            self.log(f"Match scraper completed successfully")
            
        except Exception as e:
            self.log(f"Error in match scraper: {str(e)}", 'ERROR')
            self.finish_job('FAILED', str(e))


class StadiumScraper(BaseScraper):
    """Scraper for stadium data."""
    
    def run(self):
        """Run the stadium scraper."""
        if not self.job:
            self.log("No job specified", 'ERROR')
            return
        
        self.log(f"Starting stadium scraper for URL: {self.job.url}")
        
        try:
            soup = self.get_soup(self.job.url)
            if not soup:
                return
            
            # Example implementation - adjust based on actual website structure
            stadium_containers = soup.select('.stadium-container')
            
            for container in stadium_containers:
                name = container.select_one('.stadium-name').text.strip()
                city = container.select_one('.stadium-city').text.strip()
                country = container.select_one('.stadium-country').text.strip()
                capacity_text = container.select_one('.stadium-capacity').text.strip()
                
                # Parse capacity
                capacity = int(capacity_text.replace(',', '')) if capacity_text else None
                
                # Create or update stadium
                stadium, created = Stadium.objects.update_or_create(
                    name=name,
                    defaults={
                        'city': city,
                        'country': country,
                        'capacity': capacity
                    }
                )
                
                if created:
                    self.log(f"Created new stadium: {name}, {city}")
                else:
                    self.log(f"Updated stadium: {name}, {city}")
            
            self.finish_job()
            self.log(f"Stadium scraper completed successfully")
            
        except Exception as e:
            self.log(f"Error in stadium scraper: {str(e)}", 'ERROR')
            self.finish_job('FAILED', str(e))


# Factory function to get the appropriate scraper
def get_scraper(job_type, job_id):
    """Get the appropriate scraper based on job type."""
    scrapers = {
        'TEAM': TeamScraper,
        'PLAYER': PlayerScraper,
        'MATCH': MatchScraper,
        'STADIUM': StadiumScraper,
    }
    
    scraper_class = scrapers.get(job_type)
    if not scraper_class:
        logger.error(f"Unknown scraper type: {job_type}")
        return None
    
    return scraper_class(job_id)