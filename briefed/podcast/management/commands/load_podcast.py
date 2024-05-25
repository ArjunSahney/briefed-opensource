import json
import os
from django.core.management.base import BaseCommand
from podcast.models import Podcast

class Command(BaseCommand):
    help = 'Load podcasts from a JSON file into the database'

    def add_arguments(self, parser):
        parser.add_argument('txt_file', type=str, help='Path to the TXT file containing the podcast data')

    def handle(self, *args, **kwargs):
        txt_file = kwargs['txt_file']
        # username = kwargs['username']

        if not os.path.exists(txt_file):
            self.stderr.write(self.style.ERROR(f'File "{txt_file}" does not exist'))
            return

        with open(txt_file, 'r') as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError as e:
                self.stderr.write(self.style.ERROR(f'Error parsing JSON from file "{txt_file}": {e}'))
                return
            
            Podcast.objects.create(
                # user_name=data['user_name'],
                mp3_url=data['Audio URL']
            )
        self.stdout.write(self.style.SUCCESS('Successfully loaded podcasts from JSON file'))
