from django.core.management.base import BaseCommand
from datetime import timedelta
from django.utils.timezone import is_aware
from app1.models import Adhoc

class Command(BaseCommand):
    help = 'Correct Adhoc entries that appear in May due to USE_TZ toggle but were intended for June'

    def handle(self, *args, **options):
        ist_offset = timedelta(hours=5, minutes=30)
        may_entries = Adhoc.objects.filter(createddate__month=5)

        fixed_count = 0

        for entry in may_entries:
            original = entry.createddate

            shifted_time = entry.createddate + ist_offset
            if shifted_time.month == 6:
                entry.createddate = shifted_time
                entry.save()
                fixed_count += 1


        self.stdout.write(self.style.SUCCESS(
            f"✅ Corrected {fixed_count} Adhoc entries misaligned due to USE_TZ=True."
        ))