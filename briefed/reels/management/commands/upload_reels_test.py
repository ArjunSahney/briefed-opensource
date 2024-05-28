import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'briefed.settings')
django.setup()

from reels.models import UserTable, TopicsTable, UserInterests

# Define a function to load users
def load_users(user_data):
    for user in user_data:
        user_instance = UserTable.objects.create(
            name=user['name'],
            email=user['email'],
            created_at=user['created_at'],
            updated_at=user['updated_at'],
            password=user['password']
        )
        user_instance.save()
def load_users_and_interests(user_data):
    for user in user_data:
        user_instance = UserTable.objects.create(
            name=user['name'],
            email=user['email'],
            created_at=datetime.fromisoformat(user['created_at']),
            updated_at=datetime.fromisoformat(user['updated_at']),
            password=user['password']
        )
        user_instance.save()

        for interest in user['interests']:
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

# Example usage
if __name__ == "__main__":
    # Load user data with multiple interests
    user_data = [
        {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "created_at": "2024-05-27T00:00:00Z",
            "updated_at": "2024-05-27T00:00:00Z",
            "password": "password123",
            "interests": [
                {
                    "topic_name": "Quantum Computing",
                    "topic": {
                        "date": "2024-05-27",
                        "datetime": "2024-05-27T10:00:00Z",
                        "briefs": [
                            {"summary": "Brief about Quantum Computing", "detail": "Details about Quantum Computing"}
                        ]
                    }
                },
                {
                    "topic_name": "Artificial Intelligence",
                    "topic": {
                        "date": "2024-05-28",
                        "datetime": "2024-05-28T11:00:00Z",
                        "briefs": [
                            {"summary": "Brief about AI", "detail": "Details about AI"}
                        ]
                    }
                }
            ]
        }
        # Add more user data as needed
    ]
    load_users_and_interests(user_data)