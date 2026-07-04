from django.core.management.base import BaseCommand

from sayt.models import Person


class Command(BaseCommand):
    help = 'Seed 3 groups with 15 students each'

    def handle(self, *args, **options):
        created = 0
        for g in range(1, 4):
            group_name = f'guruh{g}'
            for i in range(1, 16):
                login = f'talaba{g}_{i}'
                surname = f'Talaba{g}_{i}'
                if not Person.objects.filter(login=login).exists():
                    Person.objects.create(
                        surname=surname,
                        login=login,
                        role=Person.ROLE_STUDENT,
                        group=group_name,
                    )
                    created += 1

        self.stdout.write(self.style.SUCCESS(f'Created {created} students.'))
        for g in range(1, 4):
            group_name = f'guruh{g}'
            cnt = Person.objects.filter(role=Person.ROLE_STUDENT, group=group_name).count()
            self.stdout.write(f'{group_name}: {cnt}')
