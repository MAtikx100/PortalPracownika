from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from webpage.models import Event

class Command(BaseCommand):
    help = 'Creates Administrator, Manager, and Regular User groups and assigns permissions'

    def handle(self, *args, **options):
        # Create groups
        admin_group, _ = Group.objects.get_or_create(name='Administrator')
        manager_group, _ = Group.objects.get_or_create(name='Manager')
        Group.objects.get_or_create(name='Regular User')
        self.stdout.write(self.style.SUCCESS('Successfully created user groups'))

        # Define permissions
        try:
            user_content_type = ContentType.objects.get_for_model(User)
            event_content_type = ContentType.objects.get_for_model(Event)

            add_user_perm = Permission.objects.get(codename='add_user', content_type=user_content_type)
            view_event_perm = Permission.objects.get(codename='view_event', content_type=event_content_type)

            # Assign permissions to Administrator
            admin_group.permissions.add(add_user_perm)

            # Assign permissions to Manager
            manager_group.permissions.add(add_user_perm, view_event_perm)

            self.stdout.write(self.style.SUCCESS('Successfully assigned permissions to groups'))

        except (ContentType.DoesNotExist, Permission.DoesNotExist) as e:
            self.stdout.write(self.style.WARNING(f'Could not assign permissions: {e}'))
