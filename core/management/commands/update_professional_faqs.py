from django.core.management.base import BaseCommand
from core.models import FAQ


class Command(BaseCommand):
    help = 'Update FAQs with professional content that clarifies independence from universities'

    def handle(self, *args, **options):
        self.stdout.write('Updating FAQs with professional content...')
        
        # Clear existing FAQs
        FAQ.objects.all().delete()
        self.stdout.write('Cleared existing FAQs')
        
        # Create comprehensive professional FAQs
        self.create_professional_faqs()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully updated FAQs with professional content')
        )

    def create_professional_faqs(self):
        faqs_data = [
            # About Edunox GH
            {
                'question': 'What is Edunox GH?',
                'answer': 'Edunox GH is an independent educational consultancy service based in Ghana. We are NOT affiliated with any university, including University of the People. We are a grassroots initiative that helps students across Ghana—especially in underserved and rural communities—access higher education opportunities through personalized guidance and support services.',
                'order': 1
            },
            {
                'question': 'Are you affiliated with University of the People or any other university?',
                'answer': 'No, we are completely independent. Edunox GH is not affiliated with, endorsed by, or connected to University of the People, any Ghanaian university, or any other educational institution. We are an independent consultancy service that helps students navigate the application process to various universities.',
                'order': 2
            },
            {
                'question': 'What exactly do you do?',
                'answer': 'We provide educational consultancy services including: university application assistance, scholarship guidance, digital literacy training, document preparation support, and educational counseling. We help you understand your options and guide you through application processes, but we do not provide education or issue degrees.',
                'order': 3
            },
            
            # Fees and Services
            {
                'question': 'Why do you charge fees if universities like UoPeople are free?',
                'answer': 'University of the People is indeed tuition-free, but our fees are for our consultancy services, NOT for education. Our modest service fees cover: internet data bundles for research and applications, travel costs to reach students in remote areas, personalized application assistance, training materials and sessions, and administrative support. We are transparent that our fees are for support services, not tuition.',
                'order': 4
            },
            {
                'question': 'What services are included in your fees?',
                'answer': 'Our service fees cover: personalized consultation sessions, assistance with university applications, scholarship application guidance, digital literacy training, document preparation and review, application status tracking, and ongoing support throughout the process. We also provide travel to remote areas and cover internet costs for students who need assistance.',
                'order': 5
            },
            {
                'question': 'Can I apply to universities myself without your services?',
                'answer': 'Absolutely! You can apply directly to any university, including University of the People, without using our services. All university websites have free information and application portals. Our services are optional and designed for those who need guidance, lack digital literacy, or prefer professional assistance with the application process.',
                'order': 6
            },
            
            # University Applications
            {
                'question': 'Which universities do you help students apply to?',
                'answer': 'We assist with applications to various institutions including: University of the People (tuition-free online university), public universities in Ghana, private universities in Ghana, and select international institutions. We help you choose the best fit based on your goals, qualifications, and financial situation.',
                'order': 7
            },
            {
                'question': 'Is University of the People really completely free?',
                'answer': 'Yes, University of the People is tuition-free. However, students pay small assessment fees (around $5,460 total for a bachelor\'s degree, paid per course). There are also application fees and potential costs for proctored exams. Many students qualify for fee waivers and scholarships. We help you understand all costs and apply for financial assistance.',
                'order': 8
            },
            {
                'question': 'What documents do I need for university applications?',
                'answer': 'Common requirements include: valid ID (National ID or Passport), academic transcripts (WASSCE, BECE, or equivalent), English proficiency proof (if required), personal statement or essay, and sometimes recommendation letters. Requirements vary by university and program. We help you understand specific requirements and prepare all necessary documents.',
                'order': 9
            },
            
            # Digital Literacy and Support
            {
                'question': 'What if I\'m not computer literate?',
                'answer': 'No problem! We offer comprehensive support for students with limited digital skills: basic computer skills training, assistance with creating email accounts and online profiles, guided application completion, ongoing technical support, and even personal application services where we handle the technical aspects for you while you provide the information.',
                'order': 10
            },
            {
                'question': 'Do you provide digital literacy training?',
                'answer': 'Yes! We offer training in: basic computer operations, internet navigation and email usage, online learning platforms, video conferencing for virtual classes, document creation and submission, and general digital skills needed for online education. This training is especially valuable for students planning to study online.',
                'order': 11
            },
            
            # Scholarships and Financial Aid
            {
                'question': 'Do you help with scholarships and financial aid?',
                'answer': 'Yes, we assist with: identifying available scholarships and grants, completing scholarship applications, writing compelling personal statements, gathering required documentation, and applying for fee waivers. We help you find financial assistance to reduce or eliminate application and assessment fees.',
                'order': 12
            },
            {
                'question': 'Can you guarantee scholarship approval or university admission?',
                'answer': 'No, we cannot guarantee admission or scholarship approval. These decisions are made entirely by the universities and scholarship providers. We can only provide guidance, help you prepare strong applications, and ensure you meet all requirements. Success depends on your qualifications and the institution\'s selection criteria.',
                'order': 13
            },
            
            # Process and Timeline
            {
                'question': 'How long does the application process take?',
                'answer': 'Timeline varies by university: University of the People applications typically take 2-4 weeks for processing, Ghanaian public universities may take 1-3 months, and international universities can take 2-6 months. We help you plan ahead and meet all deadlines. Early preparation is key to success.',
                'order': 14
            },
            {
                'question': 'What happens after I submit my application?',
                'answer': 'After submission, we help you: track application status, respond to any university requests for additional information, prepare for interviews if required, understand admission decisions, and plan next steps whether accepted or not. We provide ongoing support throughout the entire process.',
                'order': 15
            },
            
            # Transparency and Trust
            {
                'question': 'How do I know you\'re legitimate?',
                'answer': 'We maintain full transparency: we clearly state we are not affiliated with any university, we provide detailed information about our services and fees upfront, we have verifiable contact information and physical presence in Ghana, and we encourage you to verify all information independently. You can also contact universities directly to confirm application requirements.',
                'order': 16
            },
            {
                'question': 'What if I\'m not satisfied with your services?',
                'answer': 'We strive for complete satisfaction. If you\'re not happy with our services, please contact us immediately. We will work to address your concerns and, where appropriate, provide additional support or partial refunds. Our goal is to help you succeed in your educational journey.',
                'order': 17
            },
            
            # Getting Started
            {
                'question': 'How do I get started with your services?',
                'answer': 'Getting started is easy: register on our website with your basic information, upload required documents (ID and academic records), browse our available services and choose what you need, book a consultation to discuss your goals, and begin your educational journey with our guidance and support.',
                'order': 18
            },
            {
                'question': 'Do you serve students outside of Ghana?',
                'answer': 'While we are based in Ghana and primarily serve Ghanaian students, we can provide remote consultancy services to students in other countries. However, our in-person services, travel support, and local expertise are specifically designed for students within Ghana.',
                'order': 19
            },
            
            # Important Disclaimers
            {
                'question': 'What should I know before using your services?',
                'answer': 'Important points to remember: we are an independent consultancy, not a university; we cannot guarantee admission or scholarships; all final decisions are made by universities; you can apply directly to universities without our help; our fees are for consultancy services, not education; and you should always verify information with universities directly. We are here to guide and support, not to replace your own research and decision-making.',
                'order': 20
            }
        ]
        
        for faq_data in faqs_data:
            faq = FAQ.objects.create(**faq_data)
            self.stdout.write(f'Created FAQ: {faq.question}')
