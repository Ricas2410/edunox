from django.core.management.base import BaseCommand
from services.models import Service, ServiceCategory


class Command(BaseCommand):
    help = 'Create default services that match navbar links'

    def handle(self, *args, **options):
        # Create or get service categories
        university_category, _ = ServiceCategory.objects.get_or_create(
            name='University Applications',
            defaults={
                'description': 'University application services',
                'order': 1,
                'is_active': True
            }
        )
        
        digital_category, _ = ServiceCategory.objects.get_or_create(
            name='Digital Training',
            defaults={
                'description': 'Digital skills and computer training',
                'order': 2,
                'is_active': True
            }
        )
        
        consultancy_category, _ = ServiceCategory.objects.get_or_create(
            name='Consultancy',
            defaults={
                'description': 'Educational consultancy services',
                'order': 3,
                'is_active': True
            }
        )

        # Default services data
        default_services = [
            {
                'category': university_category,
                'name': 'UoPeople Application',
                'short_description': 'Complete application assistance for University of the People',
                'description': '''Get comprehensive support for your University of the People application process. 
                
Our service includes:
- Application form completion assistance
- Document preparation and review
- Personal statement writing guidance
- Application submission support
- Follow-up assistance

University of the People is a tuition-free, accredited online university that offers undergraduate and graduate degree programs in Business Administration, Computer Science, Health Science, and Education.''',
                'pricing_type': 'FIXED',
                'price': 150.00,
                'duration': '2-3 weeks',
                'icon': 'fas fa-university',
                'features': '''Complete application form assistance
Document preparation and verification
Personal statement review and editing
Application submission guidance
Follow-up support until admission decision
Access to UoPeople preparation materials''',
                'requirements': '''Valid high school diploma or equivalent
English proficiency
Access to computer and internet
Commitment to complete the application process''',
                'external_url': '',
                'is_featured': True,
                'order': 1
            },
            {
                'category': university_category,
                'name': 'Ghana Universities Application',
                'short_description': 'Application support for Ghanaian universities and institutions',
                'description': '''Professional assistance for applications to Ghanaian universities and tertiary institutions.

Our comprehensive service covers:
- University selection guidance
- Application form completion
- Document preparation and authentication
- Personal statement and essay writing
- Interview preparation (where applicable)
- Scholarship application assistance

We support applications to all major Ghanaian universities including University of Ghana, KNUST, UCC, UDS, and many others.''',
                'pricing_type': 'FIXED',
                'price': 120.00,
                'duration': '3-4 weeks',
                'icon': 'fas fa-school',
                'features': '''University selection counseling
Complete application assistance
Document preparation and verification
Personal statement writing support
Interview preparation sessions
Scholarship application guidance
Follow-up until admission decision''',
                'requirements': '''WASSCE or equivalent qualification
Valid identification documents
Academic transcripts
Commitment to the application process''',
                'external_url': '',
                'is_featured': True,
                'order': 2
            },
            {
                'category': digital_category,
                'name': 'Basic Computer Skills',
                'short_description': 'Essential computer skills training for beginners',
                'description': '''Comprehensive basic computer skills training designed for beginners and those looking to improve their digital literacy.

Course covers:
- Computer fundamentals and terminology
- Operating system navigation (Windows/Mac)
- File management and organization
- Internet browsing and email
- Microsoft Office basics (Word, Excel, PowerPoint)
- Online safety and security
- Digital communication tools

Perfect for students, professionals, and anyone looking to build confidence with technology.''',
                'pricing_type': 'FIXED',
                'price': 80.00,
                'duration': '2 weeks',
                'icon': 'fas fa-desktop',
                'features': '''Computer fundamentals training
Operating system navigation
File management skills
Internet and email usage
Microsoft Office basics
Online safety education
Hands-on practice sessions
Certificate of completion''',
                'requirements': '''No prior computer experience required
Access to a computer for practice
Willingness to learn
Basic literacy skills''',
                'external_url': '',
                'is_featured': False,
                'order': 1
            },
            {
                'category': digital_category,
                'name': 'Online Learning Skills',
                'short_description': 'Master the skills needed for successful online education',
                'description': '''Develop essential skills for successful online learning and digital education platforms.

Training includes:
- Online learning platform navigation
- Digital study techniques and time management
- Virtual classroom participation
- Online collaboration tools
- Digital note-taking and organization
- Video conferencing etiquette
- Self-directed learning strategies
- Technical troubleshooting basics

Ideal for students preparing for online courses, distance learning, or remote education programs.''',
                'pricing_type': 'FIXED',
                'price': 100.00,
                'duration': '1-2 weeks',
                'icon': 'fas fa-video',
                'features': '''Online platform navigation training
Digital study techniques
Virtual classroom skills
Collaboration tools mastery
Time management for online learning
Technical troubleshooting
Self-directed learning strategies
Certificate of completion''',
                'requirements': '''Basic computer skills
Internet access
Email account
Motivation for online learning''',
                'external_url': '',
                'is_featured': False,
                'order': 2
            },
            {
                'category': consultancy_category,
                'name': 'Educational Counseling',
                'short_description': 'Professional guidance for your educational journey',
                'description': '''Personalized educational counseling to help you make informed decisions about your academic and career path.

Our counseling services include:
- Academic pathway planning
- Career guidance and exploration
- University and program selection
- Scholarship and funding opportunities
- Study abroad planning
- Skills assessment and development planning
- Goal setting and achievement strategies
- Ongoing support and mentorship

Work with experienced educational consultants who understand the Ghanaian and international education landscape.''',
                'pricing_type': 'FIXED',
                'price': 200.00,
                'duration': 'Ongoing',
                'icon': 'fas fa-user-tie',
                'features': '''One-on-one counseling sessions
Academic pathway planning
Career exploration and guidance
University selection assistance
Scholarship opportunity identification
Study abroad planning
Skills assessment
Goal setting and tracking
Ongoing mentorship support''',
                'requirements': '''Academic transcripts or records
Clear educational or career goals
Commitment to the counseling process
Regular session attendance''',
                'external_url': '',
                'is_featured': True,
                'order': 1
            }
        ]

        created_count = 0
        updated_count = 0

        for service_data in default_services:
            service, created = Service.objects.get_or_create(
                name=service_data['name'],
                category=service_data['category'],
                defaults=service_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created service: {service.name}')
                )
            else:
                # Update existing service with new data
                for key, value in service_data.items():
                    if key != 'name' and key != 'category':  # Don't update name and category
                        setattr(service, key, value)
                service.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated service: {service.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nCompleted! Created {created_count} new services, updated {updated_count} existing services.'
            )
        )
