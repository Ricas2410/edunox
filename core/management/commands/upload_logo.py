"""
Management command to upload logo to ImageKit and update site configuration
"""
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from core.models import SiteConfiguration
import requests
import os


class Command(BaseCommand):
    help = 'Upload a logo to ImageKit and update site configuration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--logo-path',
            type=str,
            help='Path to the logo file to upload',
        )
        parser.add_argument(
            '--logo-url',
            type=str,
            help='URL of the logo to download and upload',
        )

    def handle(self, *args, **options):
        logo_path = options.get('logo_path')
        logo_url = options.get('logo_url')

        if not logo_path and not logo_url:
            self.stdout.write(
                self.style.ERROR('Please provide either --logo-path or --logo-url')
            )
            return

        try:
            # Get or create site configuration
            config = SiteConfiguration.get_config()

            if logo_path:
                # Upload from local file
                if not os.path.exists(logo_path):
                    self.stdout.write(
                        self.style.ERROR(f'File not found: {logo_path}')
                    )
                    return

                with open(logo_path, 'rb') as f:
                    file_content = f.read()
                    filename = os.path.basename(logo_path)

            elif logo_url:
                # Download from URL
                response = requests.get(logo_url)
                response.raise_for_status()
                file_content = response.content
                filename = 'logo.png'

            # Create Django file object
            django_file = ContentFile(file_content, name=filename)

            # Save to site configuration (this will upload to ImageKit)
            config.logo = django_file
            config.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully uploaded logo to ImageKit: {config.logo.url}'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error uploading logo: {str(e)}')
            )
