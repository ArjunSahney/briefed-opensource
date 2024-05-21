import json
from django.core.management.base import BaseCommand
from reels.models import Reel

class Command(BaseCommand):
    help = 'Loads reels from a JSON file into the database'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='The JSON file path')

    def handle(self, *args, **options):
        # Open and load the JSON file
        with open(options['json_file'], 'r') as file:
            data = json.load(file)
        
        # Iterate over each reel in the JSON
        for reel_data in data:
            # Create a new Reel instance for each item
            sources_list = reel_data['sources']
            sources_string = ""
            for source in sources_list:
                sources += source[0] + " - " + source[1] + ", " + source[2] + "\n"
            reel = Reel(
                title=reel_data['Title'],
                summary=reel_data['Summary'],
                image_url=reel_data['Image Filepath'],
                sources=sources_string
            )
            reel.save()  # Save the Reel object to the database
            
        self.stdout.write(self.style.SUCCESS('Successfully loaded all reels into the database.'))
