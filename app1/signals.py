from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Punch, WFOCount
from django.core.cache import cache
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from .models import ResignationForm, ExperienceCertificate
import pdfkit
import os
from django.conf import settings

@receiver(post_save, sender=Punch)
def create_profile(sender, instance, created, **kwargs):
        if created:
            punchcache = f'all_user_punch{instance.date.year}{instance.date.month}'
            print(punchcache)
            cache.delete(punchcache)

@receiver(post_delete, sender=Punch)
def after_punch_deleted(sender, instance, **kwargs):
    punchcache = f'all_user_punch{instance.date.year}{instance.date.month}'
    print(punchcache)
    cache.delete(punchcache)


@receiver(post_save, sender=WFOCount)
def create_wfosignal(sender, instance, created, **kwargs):
    if created and instance.wfo_date:
        punchcache = f"wfo_count_by_user_month_wise{instance.wfo_date.year}{instance.wfo_date.month}"
        print(punchcache)
        cache.delete(punchcache)


@receiver(post_delete, sender=WFOCount)
def after_wfosignal(sender, instance, **kwargs):
    if instance.wfo_date:
        punchcache = f"wfo_count_by_user_month_wise{instance.wfo_date.year}{instance.wfo_date.month}"
        print(punchcache)
        cache.delete(punchcache)


@receiver(post_save, sender=WFOCount)
def update_wfosignal(sender, instance, created, **kwargs):
    if created and instance.wfo_date:
        punchcache = f"wfo_count_by_user_month_wise{instance.wfo_date.year}{instance.wfo_date.month}"
        print(punchcache)
        cache.delete(punchcache)


# Experience certificate Template
@receiver(post_save, sender=ResignationForm)
def generate_experience_certificate(sender, instance, **kwargs):
    try:
        # Trigger only when resignation is approved
        if instance.status != 'Approved':
            return

        user = instance.user

        # Prevent duplicate generation
        if ExperienceCertificate.objects.filter(user=user, resignation=instance).exists():
            return

        # Prepare full context
        context = {
            'name': f"{user.username}",
            'employee_id': user.empid,
            'department': user.department.name if user.department else '',
            'datejoin': user.datejoin.strftime('%d %B %Y') if hasattr(user, 'datejoin') and user.datejoin and hasattr(user.datejoin, 'strftime') else (user.datejoin if user.datejoin else ''),
            'resignation_date': instance.resignation_date.strftime('%d %B %Y'),
            'last_working_day': instance.last_workingday.strftime('%d %B %Y'),
            'issue_date': timezone.now().strftime('%d %B %Y'),
            'signature_url': "https://hrms.cydeztechnologies.com/static/login/images/signature.png",
            'logo_url': "https://hrms.cydeztechnologies.com/static/login/images/logo.png",
            'seal_url': "https://hrms.cydeztechnologies.com/static/login/images/seal.png"
        }

        # Render HTML from template
        html_content = render_to_string('index/experience_template.html', context)

        # File paths
        filename = f"{user.username}_experience_certificate.pdf"
        folder_path = os.path.join(settings.MEDIA_ROOT, 'experience_certificates')
        output_path = os.path.join(folder_path, filename)
        os.makedirs(folder_path, exist_ok=True)

        # PDFKit options
        options = {
            'enable-local-file-access': None
        }

        # Generate the PDF
        pdfkit.from_string(html_content, output_path, configuration=settings.PDFKIT_CONFIG, options=options)

        # Save certificate to database
        cert = ExperienceCertificate.objects.create(
            user=user,
            resignation=instance,
            certificate_file=f'experience_certificates/{filename}'
        )

        # Send via email
        email = EmailMessage(
            subject={filename},
                body=f"""
        Dear HR Team,

        Please find attached the official Experience Certificate for the employee below:

        Name       : {user.username}  
        Employee ID: {user.empid}  
        Email      : {user.email}

        This certificate has been auto-generated as part of the approved resignation workflow.

        Regards,  
        Automated HRMS System  
        Cydez Technologies
        """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=["operations@cydeztechnologies.com"]  # HR recipient
        )
        email.attach_file(output_path)
        email.send()

    except Exception as e:
        print("🔥 ERROR WHILE GENERATING CERTIFICATE:", str(e))