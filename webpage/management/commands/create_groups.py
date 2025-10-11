from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from webpage.models import Event

class Command(BaseCommand):
    help = 'Creates a Manager group and assigns permissions'

    def handle(self, *args, **options):
        manager_group, created = Group.objects.get_or_create(name='Manager')
        if created:
            self.stdout.write(self.style.SUCCESS('Successfully created Manager group'))

        content_type = ContentType.objects.get_for_model(Event)
        view_event_permission = Permission.objects.get(
            codename='view_event',
            content_type=content_type,
        )

        manager_group.permissions.add(view_event_permission)
        self.stdout.write(self.style.SUCCESS('Successfully assigned view_event permission to Manager group'))
