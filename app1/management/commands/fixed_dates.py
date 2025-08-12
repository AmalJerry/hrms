from django.core.management.base import BaseCommand
from datetime import timedelta
from app1.models import AssignSalaryStructure

class Command(BaseCommand):
    help = 'Correct AssignSalaryStructure entries that appear in May due to USE_TZ toggle but were intended for June'

    def handle(self, *args, **options):
        ist_offset = timedelta(hours=5, minutes=30)
        may_entries = AssignSalaryStructure.objects.filter(effective_date__month=5)

        fixed_count = 0

        for entry in may_entries:
            original = entry.effective_date
            shifted_time = entry.effective_date + ist_offset
            if shifted_time.month == 6:
                entry.effective_date = shifted_time
                entry.save()
                fixed_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"✅ Corrected {fixed_count} AssignSalaryStructure entries misaligned due to USE_TZ=True."
        ))