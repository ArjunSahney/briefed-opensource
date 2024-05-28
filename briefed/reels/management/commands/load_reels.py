import json
import os
from django.core.management.base import BaseCommand
from reels.models import Reel, Topic

class Command(BaseCommand):
    help = 'Loads reels from a txt file into the database'

    def add_arguments(self, parser):
        parser.add_argument('txt_file', type=str, help='Path to the TXT file containing the reels data')
        # parser.add_argument('username', type=str, help='Username of the user')

    def handle(self, *args, **kwargs):
        txt_file = kwargs['txt_file']
        # username = kwargs['username']

        if not os.path.exists(txt_file):
            self.stderr.write(self.style.ERROR(f'File "{txt_file}" does not exist'))
            return

        # try:
        #     user = User.objects.get(username=username)
        # except User.DoesNotExist:
        #     self.stderr.write(self.style.ERROR(f'User "{username}" does not exist'))
        #     return

        with open(txt_file, 'r') as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError as e:
                self.stderr.write(self.style.ERROR(f'Error parsing JSON from file "{txt_file}": {e}'))
                return

        # Iterate over each topic and reel in the JSON
        for topic, reels in data.items():
            for reel_data in reels:
                topic_name = topic
                topic, created = Topic.objects.get_or_create(name=topic_name)
                # Create a new Reel instance for each item
                sources_list = reel_data['sources']
                # sources_string = ""
                # for source in sources_list:
                #     sources_string += source[0] + " - " + source[1] + ", " + source[2] + "\n"
                reel = Reel(
                    topic=topic,
                    title=reel_data['Title'],
                    summary=reel_data['Summary'],
                    image_url=reel_data['Image Filepath'],
                    sources=sources_list
                )
                reel.save()  # Save the Reel object to the database
            
        self.stdout.write(self.style.SUCCESS('Successfully loaded all reels into the database.'))
