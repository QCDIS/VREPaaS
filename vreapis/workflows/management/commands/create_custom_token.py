import os

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Create a custom token for a specific user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username of the user')
        parser.add_argument('--token', type=str, help='token')
        parser.add_argument('--password', type=str, help='password')
    def handle(self, *args, **options):

        self.stdout.write(self.style.ERROR('------------------------------Create Custom Token------------------------------'))
        username = options['username']
        self.stdout.write('Will create user: '+username)
        if not username:
            self.stdout.write(self.style.ERROR('username argument not found.'))
        password = options['password']
        self.stdout.write('Will create password: '+password)
        if not password:
            self.stdout.write(self.style.ERROR('password argument not found.'))

        User = get_user_model()
        if not User.objects.filter(username=options['username']).exists():
            self.stdout.write(f"User {options['username']} not present, creating it ...")
            user = User.objects.create_superuser(username=options['username'])
            user.set_password(password)
            user.save()
            self.stdout.write(f"user {options['username']} created!")
        else:
            user = User.objects.get(username=username)
            self.stdout.write(str(user))
            self.stdout.write(f"Got user {options['username']}")

        token_key = options['token']
        if token_key:
            token, created = Token.objects.get_or_create(user=user, key=token_key)
            self.stdout.write(self.style.SUCCESS(f'Token created for user: {username}'))
            self.stdout.write(self.style.SUCCESS(f'Token key: {token.key}'))
        else:
            self.stdout.write(self.style.ERROR('Token argument not found.'))



