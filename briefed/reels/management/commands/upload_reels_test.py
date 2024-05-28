import os
import json
import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from your_app_name.models import UserTable, TopicsTable, UserInterests

class Command(BaseCommand):
    help = 'Load data into the database'

    def add_arguments(self, parser):
        parser.add_argument('--user-file', type=str, help='Path to the JSON file containing user data')
        parser.add_argument('--interests-file', type=str, help='Path to the JSON or CSV file containing interests data')

    def handle(self, *args, **kwargs):
        user_file = kwargs['user_file']
        interests_file = kwargs['interests_file']

        if user_file:
            self.load_users(user_file)
        if interests_file:
            self.load_interests_and_topics(interests_file)

    def load_users(self, user_file):
        with open(user_file, 'r') as file:
            user_data = json.load(file)
            for user in user_data:
                user_instance = UserTable.objects.create(
                    name=user['name'],
                    email=user['email'],
                    created_at=datetime.fromisoformat(user['created_at']),
                    updated_at=datetime.fromisoformat(user['updated_at']),
                    password=user['password']
                )
                user_instance.save()
                self.stdout.write(self.style.SUCCESS(f'Successfully added user: {user["name"]}'))

    def load_interests_and_topics(self, interests_file):
        if interests_file.endswith('.json'):
            with open(interests_file, 'r') as file:
                interests_data = json.load(file)
        elif interests_file.endswith('.csv'):
            interests_data = []
            with open(interests_file, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    interests_data.append({
                        "user_email": row['user_email'],
                        "topic_name": row['topic_name'],
                        "topic": {
                            "date": row['topic_date'],
                            "datetime": row['topic_datetime'],
                            "briefs": json.loads(row['topic_briefs'])
                        }
                    })

        for interest in interests_data:
            user_instance = UserTable.objects.get(email=interest['user_email'])
            topic_instance = TopicsTable.objects.create(
                date=datetime.strptime(interest['topic']['date'], "%Y-%m-%d").date(),
                datetime=datetime.fromisoformat(interest['topic']['datetime']),
                briefs=interest['topic']['briefs']
            )
            topic_instance.save()
            
            user_interest_instance = UserInterests.objects.create(
                user=user_instance,
                topic=topic_instance,
                topic_name=interest['topic_name']
            )
            user_interest_instance.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully added interest for user: {user_instance.name}'))

