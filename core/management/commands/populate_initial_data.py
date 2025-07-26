from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import SiteConfiguration, FAQ
from services.models import ServiceCategory, Service
from resources.models import ResourceCategory, Resource


class Command(BaseCommand):
    help = 'Populate initial data for EduBridge Ghana'

    def handle(self, *args, **options):
        self.stdout.write('Populating initial data...')
        
        # Create site configuration
        self.create_site_config()
        
        # Create FAQs
        self.create_faqs()
        
        # Create service categories and services
        self.create_services()
        
        # Create resource categories
        self.create_resource_categories()
        
        # Create admin user if not exists
        self.create_admin_user()
        
        self.stdout.write(self.style.SUCCESS('Successfully populated initial data!'))

    def create_site_config(self):
        config, created = SiteConfiguration.objects.get_or_create(
            defaults={
                'site_name': 'EduBridge Ghana',
                'site_description': 'Your gateway to affordable higher education and digital empowerment.',
                'contact_email': 'info@edubridge.com',
                'contact_phone': '+233 XX XXX XXXX',
                'address': 'Accra, Ghana',
                'is_active': True
            }
        )
        if created:
            self.stdout.write('Created site configuration')

    def create_faqs(self):
        faqs_data = [
            {
                'question': 'What is Edunox GH?',
                'answer': 'Edunox GH is a grassroots initiative committed to empowering students across Ghana with access to tuition-free universities, traditional higher institutions, and personalized educational consulting.',
                'order': 1
            },
            {
                'question': 'Is University of the People really free?',
                'answer': 'Yes, University of the People is tuition-free. Our fee is for support and outreach services, not for education itself.',
                'order': 2
            },
            {
                'question': 'What documents do I need to register?',
                'answer': 'You need to upload your ID (National ID or Passport) and your exam results (WASSCE, BECE, or equivalent academic transcripts).',
                'order': 3
            },
            {
                'question': 'How much do your services cost?',
                'answer': 'While reading information on our website is free, a modest service fee is charged to cover internet data bundles, travel to remote areas, personalized application assistance, and training sessions.',
                'order': 4
            },
            {
                'question': 'Do you help with scholarship applications?',
                'answer': 'Yes, we assist with applying for available scholarships to reduce or eliminate exam/application fees.',
                'order': 5
            },
            {
                'question': 'What if I\'m not computer literate?',
                'answer': 'No problem! We offer a Personal Application Service where we collect your particulars and apply on your behalf. We also provide digital literacy training.',
                'order': 6
            }
        ]
        
        for faq_data in faqs_data:
            faq, created = FAQ.objects.get_or_create(
                question=faq_data['question'],
                defaults=faq_data
            )
            if created:
                self.stdout.write(f'Created FAQ: {faq.question}')

    def create_services(self):
        # Create service categories
        categories_data = [
            {
                'name': 'University Applications',
                'description': 'Help with university application processes',
                'icon': 'fas fa-graduation-cap',
                'order': 1
            },
            {
                'name': 'Digital Training',
                'description': 'Digital literacy and online learning skills',
                'icon': 'fas fa-laptop',
                'order': 2
            },
            {
                'name': 'Consultancy',
                'description': 'Educational guidance and career counseling',
                'icon': 'fas fa-comments',
                'order': 3
            }
        ]
        
        for cat_data in categories_data:
            category, created = ServiceCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'Created service category: {category.name}')

        # Create services
        services_data = [
            {
                'category_name': 'University Applications',
                'name': 'University of the People Application',
                'short_description': 'Complete application support for UoPeople admission',
                'description': 'We provide comprehensive support for your University of the People application, including document preparation, application form completion, and submission guidance.',
                'price': 50.00,
                'duration': '1-2 weeks',
                'icon': 'fas fa-university',
                'features': 'Application form completion\nDocument preparation\nSubmission guidance\nFollow-up support',
                'is_featured': True
            },
            {
                'category_name': 'University Applications',
                'name': 'Ghana University Application',
                'short_description': 'Application support for public and private universities in Ghana',
                'description': 'Get help applying to public and private universities in Ghana with our comprehensive application support service.',
                'price': 75.00,
                'duration': '2-3 weeks',
                'icon': 'fas fa-school',
                'features': 'University selection guidance\nApplication assistance\nDocument verification\nInterview preparation',
                'is_featured': True
            },
            {
                'category_name': 'Digital Training',
                'name': 'Basic Computer Skills',
                'short_description': 'Learn essential computer skills for online learning',
                'description': 'Master basic computer skills including email, internet browsing, and file management essential for online education.',
                'price': 30.00,
                'duration': '1 week',
                'icon': 'fas fa-desktop',
                'features': 'Email setup and management\nInternet browsing\nFile management\nBasic software usage'
            },
            {
                'category_name': 'Digital Training',
                'name': 'Online Learning Skills',
                'short_description': 'Learn how to study effectively online',
                'description': 'Develop skills for effective online learning including virtual classroom participation and time management.',
                'price': 40.00,
                'duration': '1-2 weeks',
                'icon': 'fas fa-video',
                'features': 'Virtual classroom navigation\nOnline study techniques\nTime management\nDigital note-taking'
            },
            {
                'category_name': 'Consultancy',
                'name': 'Educational Counseling',
                'short_description': 'Personalized guidance for your educational journey',
                'description': 'Receive personalized guidance to help you choose the best program, school, or career path that fits your dreams and goals.',
                'price': 25.00,
                'duration': '1 hour session',
                'icon': 'fas fa-user-tie',
                'features': 'Career assessment\nProgram recommendations\nGoal setting\nAction plan development',
                'is_featured': True
            }
        ]
        
        for service_data in services_data:
            category = ServiceCategory.objects.get(name=service_data['category_name'])
            service, created = Service.objects.get_or_create(
                name=service_data['name'],
                defaults={
                    'category': category,
                    'short_description': service_data['short_description'],
                    'description': service_data['description'],
                    'price': service_data['price'],
                    'duration': service_data['duration'],
                    'icon': service_data['icon'],
                    'features': service_data['features'],
                    'is_featured': service_data.get('is_featured', False)
                }
            )
            if created:
                self.stdout.write(f'Created service: {service.name}')

    def create_resource_categories(self):
        categories_data = [
            {
                'name': 'University Guides',
                'description': 'Comprehensive guides for university applications',
                'icon': 'fas fa-book',
                'color': '#3B82F6',
                'order': 1
            },
            {
                'name': 'Scholarship Information',
                'description': 'Information about available scholarships',
                'icon': 'fas fa-award',
                'color': '#10B981',
                'order': 2
            },
            {
                'name': 'Digital Literacy',
                'description': 'Resources for improving digital skills',
                'icon': 'fas fa-laptop',
                'color': '#8B5CF6',
                'order': 3
            },
            {
                'name': 'Career Guidance',
                'description': 'Career planning and development resources',
                'icon': 'fas fa-briefcase',
                'color': '#F59E0B',
                'order': 4
            }
        ]
        
        for cat_data in categories_data:
            category, created = ResourceCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'Created resource category: {category.name}')

    def create_admin_user(self):
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@edubridge.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(f'Created admin user: {admin_user.username}')
        else:
            self.stdout.write('Admin user already exists')
