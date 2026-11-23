from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from accounts.models import StudentProfile, CompanyProfile, FacultyProfile
from skills.models import SkillCategory, Skill, StudentSkill, SkillResource, StudentProject, StudentCertification
from internships.models import InternshipPosting, PostingRequiredSkill, Application, PlacementRecord
from notifications.models import Notification

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds database with realistic skills, users, postings, and smart automation test records'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting database seed...'))

        # 1. Create Skill Categories & Skills with Aliases
        categories_data = {
            'Programming Languages': [
                ('Python', 'High-level programming language', 'python, py, python3'),
                ('Java', 'Object-oriented programming language', 'java, j2ee, core java'),
                ('C++', 'High performance compiled language', 'c++, cpp'),
                ('JavaScript', 'Dynamic web scripting language', 'javascript, js, es6, ecmascript'),
                ('TypeScript', 'Typed superset of JavaScript', 'typescript, ts'),
                ('C#', 'Microsoft enterprise language', 'c#, csharp, .net'),
            ],
            'Web Backend Development': [
                ('Django', 'High-level Python web framework', 'django, drf, django rest framework'),
                ('Flask', 'Lightweight Python micro-framework', 'flask'),
                ('Node.js', 'Asynchronous event-driven JavaScript runtime', 'node, nodejs, express, expressjs'),
                ('REST API', 'RESTful API design and implementation', 'rest, restful, rest api, web apis'),
                ('Spring Boot', 'Enterprise Java microservice framework', 'spring boot, spring framework, spring'),
                ('FastAPI', 'High performance Python API framework', 'fastapi'),
            ],
            'Web Frontend Development': [
                ('HTML5', 'Markup standard for web development', 'html, html5'),
                ('CSS3', 'Style sheet language for modern web', 'css, css3, flexbox, grid'),
                ('React', 'Component-based frontend UI library', 'react, reactjs, react.js'),
                ('Bootstrap', 'Responsive frontend component framework', 'bootstrap, bootstrap5'),
                ('Tailwind CSS', 'Utility-first modern CSS framework', 'tailwind, tailwindcss'),
                ('Vue.js', 'Progressive JavaScript framework', 'vue, vuejs, vue.js'),
            ],
            'Databases & Data Storage': [
                ('SQL', 'Structured Query Language for relational DBs', 'sql, relational database'),
                ('PostgreSQL', 'Advanced open-source relational database', 'postgres, postgresql'),
                ('MySQL', 'Popular open-source relational DBMS', 'mysql'),
                ('MongoDB', 'NoSQL document database', 'mongodb, mongo, nosql'),
                ('Redis', 'In-memory key-value data store & cache', 'redis, in-memory caching'),
            ],
            'AI, Machine Learning & Data Science': [
                ('Machine Learning', 'Predictive modeling and algorithms', 'machine learning, ml, algorithms'),
                ('Deep Learning', 'Neural networks and deep models', 'deep learning, dl, neural networks'),
                ('Pandas', 'Data manipulation and analysis library', 'pandas, dataframe'),
                ('NumPy', 'Scientific computing package', 'numpy'),
                ('Scikit-Learn', 'Machine learning toolkit in Python', 'scikit-learn, sklearn'),
                ('Natural Language Processing', 'Text processing and LLMs', 'nlp, natural language processing, text analysis'),
            ],
            'Cloud, DevOps & Tools': [
                ('Git', 'Distributed version control system', 'git, github, gitlab'),
                ('Docker', 'Containerization platform', 'docker, containerization, containers'),
                ('AWS', 'Amazon Web Services cloud computing', 'aws, amazon web services, ec2, s3'),
                ('Linux', 'Open source operating system CLI', 'linux, bash, unix, shell scripting'),
                ('CI/CD', 'Continuous integration and deployment pipelines', 'ci/cd, github actions, jenkins'),
            ]
        }

        skill_objs = {}
        for cat_name, skills_list in categories_data.items():
            cat, _ = SkillCategory.objects.get_or_create(name=cat_name)
            for s_name, s_desc, s_aliases in skills_list:
                skill, _ = Skill.objects.get_or_create(
                    name=s_name,
                    defaults={'category': cat, 'description': s_desc, 'aliases': s_aliases}
                )
                skill_objs[s_name] = skill

        self.stdout.write(self.style.SUCCESS(f'Created {len(skill_objs)} skills across categories.'))

        # 2. Add Learning Resources for Skills (for Smart Development Suggestions)
        learning_resources = [
            ('Django', 'Official Django Documentation & Tutorial', 'https://docs.djangoproject.com/en/stable/intro/tutorial01/', 'DOCUMENTATION', 'Comprehensive step-by-step introduction to Django models, views, and templates.'),
            ('Django', 'Django for Beginners (FreeCodeCamp)', 'https://www.youtube.com/watch?v=F5mRW0jo-U4', 'COURSE', 'Hands-on video course building 3 production Django web applications.'),
            ('Django', 'Build a Multi-Tenant SaaS Portal', 'https://github.com/topics/django-projects', 'PROJECT_IDEA', 'Create an academic collaboration platform with custom auth and dashboard analytics.'),
            ('REST API', 'RESTful API Design Best Practices', 'https://restfulapi.net/', 'DOCUMENTATION', 'Architectural constraints, HTTP status codes, and URI design conventions.'),
            ('React', 'Official React 19 Quick Start Guide', 'https://react.dev/learn', 'DOCUMENTATION', 'Learn interactive state, hooks, and modern component composition.'),
            ('React', 'Full Stack React & Django Integration Guide', 'https://www.youtube.com/results?search_query=react+django+rest+framework', 'COURSE', 'Complete project guide connecting Django REST backend with React single-page app.'),
            ('Machine Learning', 'Kaggle Machine Learning Track (Free)', 'https://www.kaggle.com/learn/intro-to-machine-learning', 'COURSE', 'Practical interactive track covering Decision Trees, Random Forests, and cross-validation.'),
            ('Docker', 'Docker 101 - Containerizing Python Web Apps', 'https://docs.docker.com/get-started/', 'DOCUMENTATION', 'Writing Dockerfiles, building multi-stage images, and docker-compose orchestration.'),
            ('SQL', 'SQL Bolt - Interactive SQL Lessons', 'https://sqlbolt.com/', 'COURSE', 'Interactive browser exercises to master JOINs, aggregates, and subqueries.')
        ]

        for s_name, title, url, r_type, desc in learning_resources:
            if s_name in skill_objs:
                SkillResource.objects.get_or_create(
                    skill=skill_objs[s_name],
                    title=title,
                    defaults={'resource_url': url, 'resource_type': r_type, 'description': desc}
                )

        # 3. Create Demo Users
        # A) Faculty / Admin
        faculty_user, _ = User.objects.get_or_create(
            username='faculty_admin',
            defaults={
                'email': 'faculty@college.edu',
                'first_name': 'Dr. Ramesh',
                'last_name': 'Sharma',
                'role': 'FACULTY',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        faculty_user.set_password('admin123')
        faculty_user.save()
        FacultyProfile.objects.get_or_create(
            user=faculty_user,
            defaults={
                'department': 'Computer Science & Engineering',
                'designation': 'Head of Placements & Professor',
                'employee_id': 'FAC-CSE-104'
            }
        )

        # B) Company 1: Nexas Technologies
        c1_user, _ = User.objects.get_or_create(
            username='nexas_tech',
            defaults={
                'email': 'recruiting@nexastech.com',
                'first_name': 'Sarah',
                'last_name': 'Jenkins',
                'role': 'COMPANY',
            }
        )
        c1_user.set_password('company123')
        c1_user.save()
        c1_profile, _ = CompanyProfile.objects.get_or_create(
            user=c1_user,
            defaults={
                'company_name': 'Nexas Technologies',
                'industry_type': 'Cloud & Enterprise Software',
                'website': 'https://nexastech.example.com',
                'location': 'Bangalore, India (Hybrid)',
                'description': 'Building next-generation distributed enterprise platforms and intelligent cloud services.',
                'contact_email': 'careers@nexastech.com',
                'is_verified': True
            }
        )

        # C) Company 2: DataStride AI
        c2_user, _ = User.objects.get_or_create(
            username='datastride_ai',
            defaults={
                'email': 'talent@datastride.io',
                'first_name': 'Vikram',
                'last_name': 'Mehta',
                'role': 'COMPANY',
            }
        )
        c2_user.set_password('company123')
        c2_user.save()
        c2_profile, _ = CompanyProfile.objects.get_or_create(
            user=c2_user,
            defaults={
                'company_name': 'DataStride AI',
                'industry_type': 'Artificial Intelligence & Analytics',
                'website': 'https://datastride.example.com',
                'location': 'Hyderabad, India (Remote Available)',
                'description': 'Pioneering generative AI and data analytics intelligence solutions for global enterprises.',
                'contact_email': 'hiring@datastride.io',
                'is_verified': True
            }
        )

        # D) Students
        # Student 1: Rahul (Python Backend focus)
        s1_user, _ = User.objects.get_or_create(
            username='rahul_cse',
            defaults={
                'email': 'rahul.verma@student.edu',
                'first_name': 'Rahul',
                'last_name': 'Verma',
                'role': 'STUDENT',
            }
        )
        s1_user.set_password('student123')
        s1_user.save()
        s1_profile, _ = StudentProfile.objects.get_or_create(
            user=s1_user,
            defaults={
                'registration_no': '2023CSE045',
                'branch': 'Computer Science & Engineering',
                'cgpa': Decimal('8.40'),
                'graduation_year': 2026,
                'bio': 'Passionate backend developer with strong foundations in Python, Django, and database modeling. Seeking challenging summer internships.',
                'phone': '+91 98765 43210',
                'github_url': 'https://github.com/rahul-verma-dev',
                'linkedin_url': 'https://linkedin.com/in/rahul-verma-cse'
            }
        )

        # Add skills for Rahul
        s1_skills = [
            ('Python', 'ADVANCED'),
            ('SQL', 'INTERMEDIATE'),
            ('HTML5', 'ADVANCED'),
            ('CSS3', 'INTERMEDIATE'),
            ('Git', 'INTERMEDIATE'),
            ('REST API', 'BEGINNER')
            # Notice: Missing Django! Perfect for showing Skill Gap Analysis demo
        ]
        for s_name, prof in s1_skills:
            if s_name in skill_objs:
                StudentSkill.objects.get_or_create(
                    student=s1_profile,
                    skill=skill_objs[s_name],
                    defaults={'proficiency': prof, 'verified': True}
                )

        StudentProject.objects.get_or_create(
            student=s1_profile,
            title='E-Commerce API & Inventory System',
            defaults={
                'description': 'Designed and implemented relational database schemas and automated checkout REST endpoints with SQL and Python.',
                'technologies_used': 'Python, SQL, HTML5, Git',
                'github_link': 'https://github.com/rahul-verma-dev/ecommerce-api'
            }
        )

        # Student 2: Priya (Frontend & Full Stack focus)
        s2_user, _ = User.objects.get_or_create(
            username='priya_it',
            defaults={
                'email': 'priya.sharma@student.edu',
                'first_name': 'Priya',
                'last_name': 'Sharma',
                'role': 'STUDENT',
            }
        )
        s2_user.set_password('student123')
        s2_user.save()
        s2_profile, _ = StudentProfile.objects.get_or_create(
            user=s2_user,
            defaults={
                'registration_no': '2023IT021',
                'branch': 'Information Technology',
                'cgpa': Decimal('9.10'),
                'graduation_year': 2026,
                'bio': 'Frontend specialist experienced in React, modern JavaScript, and UI/UX design. Open to full-stack and frontend roles.',
                'phone': '+91 98765 88990',
                'github_url': 'https://github.com/priya-sharma-it',
                'linkedin_url': 'https://linkedin.com/in/priya-sharma'
            }
        )

        s2_skills = [
            ('JavaScript', 'ADVANCED'),
            ('React', 'ADVANCED'),
            ('HTML5', 'ADVANCED'),
            ('CSS3', 'ADVANCED'),
            ('Git', 'ADVANCED'),
            ('Node.js', 'INTERMEDIATE'),
            ('Bootstrap', 'ADVANCED')
        ]
        for s_name, prof in s2_skills:
            if s_name in skill_objs:
                StudentSkill.objects.get_or_create(
                    student=s2_profile,
                    skill=skill_objs[s_name],
                    defaults={'proficiency': prof, 'verified': True}
                )

        # Student 3: Arjun (AI & Data Science focus)
        s3_user, _ = User.objects.get_or_create(
            username='arjun_ai',
            defaults={
                'email': 'arjun.nair@student.edu',
                'first_name': 'Arjun',
                'last_name': 'Nair',
                'role': 'STUDENT',
            }
        )
        s3_user.set_password('student123')
        s3_user.save()
        s3_profile, _ = StudentProfile.objects.get_or_create(
            user=s3_user,
            defaults={
                'registration_no': '2023AI014',
                'branch': 'Artificial Intelligence & Data Science',
                'cgpa': Decimal('7.80'),
                'graduation_year': 2026,
                'bio': 'Machine Learning enthusiast with strong mathematical fundamentals, data wrangling skills, and model training experience.',
                'phone': '+91 91234 56789',
                'github_url': 'https://github.com/arjun-nair-ai',
                'linkedin_url': 'https://linkedin.com/in/arjun-nair'
            }
        )

        s3_skills = [
            ('Python', 'ADVANCED'),
            ('Machine Learning', 'ADVANCED'),
            ('Pandas', 'ADVANCED'),
            ('NumPy', 'ADVANCED'),
            ('Scikit-Learn', 'INTERMEDIATE'),
            ('SQL', 'INTERMEDIATE')
        ]
        for s_name, prof in s3_skills:
            if s_name in skill_objs:
                StudentSkill.objects.get_or_create(
                    student=s3_profile,
                    skill=skill_objs[s_name],
                    defaults={'proficiency': prof, 'verified': True}
                )

        # 4. Create Postings
        # Posting 1: Python/Django Developer Intern (Nexas Technologies)
        p1, _ = InternshipPosting.objects.get_or_create(
            company=c1_profile,
            title='Backend Python & Django Engineering Intern',
            defaults={
                'posting_type': 'INTERNSHIP',
                'description': 'We are looking for an energetic Backend Developer Intern to help build and scale our multi-tenant cloud microservices. You will work closely with senior architects to develop robust REST APIs and optimize database queries.',
                'responsibilities': 'Develop clean, well-tested Python/Django backend code.\nDesign RESTful APIs for web and mobile clients.\nWrite optimized SQL queries and manage migrations.\nParticipate in code reviews and agile sprints.',
                'location': 'Bangalore (Hybrid)',
                'stipend_or_salary': '₹30,000 / month',
                'min_cgpa': Decimal('7.00'),
                'allowed_branches': 'Computer Science & Engineering, Information Technology, Artificial Intelligence & Data Science',
                'open_positions': 4,
                'deadline': (timezone.now() + timedelta(days=30)).date(),
                'is_active': True
            }
        )
        p1_reqs = [
            ('Python', 'INTERMEDIATE', True),
            ('Django', 'INTERMEDIATE', True),
            ('SQL', 'INTERMEDIATE', True),
            ('REST API', 'INTERMEDIATE', True),
            ('Git', 'BEGINNER', False)
        ]
        for s_name, min_lvl, mand in p1_reqs:
            if s_name in skill_objs:
                PostingRequiredSkill.objects.get_or_create(
                    posting=p1,
                    skill=skill_objs[s_name],
                    defaults={'minimum_proficiency': min_lvl, 'is_mandatory': mand}
                )

        # Posting 2: Frontend React Engineer (Nexas Technologies)
        p2, _ = InternshipPosting.objects.get_or_create(
            company=c1_profile,
            title='Frontend React Developer Intern',
            defaults={
                'posting_type': 'INTERNSHIP',
                'description': 'Join our frontend team to build high-performance, accessible, and delightful interactive user interfaces for thousands of enterprise users.',
                'responsibilities': 'Build modular React UI components using modern hooks.\nCollaborate with UX designers to translate Figma mockups into code.\nEnsure responsiveness across mobile, tablet, and desktop viewports.',
                'location': 'Remote / Bangalore',
                'stipend_or_salary': '₹28,000 / month',
                'min_cgpa': Decimal('6.50'),
                'allowed_branches': 'Computer Science & Engineering, Information Technology, Electronics & Communication Engineering',
                'open_positions': 2,
                'deadline': (timezone.now() + timedelta(days=25)).date(),
                'is_active': True
            }
        )
        p2_reqs = [
            ('JavaScript', 'ADVANCED', True),
            ('React', 'INTERMEDIATE', True),
            ('HTML5', 'ADVANCED', True),
            ('CSS3', 'INTERMEDIATE', True),
            ('Git', 'INTERMEDIATE', False)
        ]
        for s_name, min_lvl, mand in p2_reqs:
            if s_name in skill_objs:
                PostingRequiredSkill.objects.get_or_create(
                    posting=p2,
                    skill=skill_objs[s_name],
                    defaults={'minimum_proficiency': min_lvl, 'is_mandatory': mand}
                )

        # Posting 3: Machine Learning & Data Science Intern (DataStride AI)
        p3, _ = InternshipPosting.objects.get_or_create(
            company=c2_profile,
            title='Machine Learning & Data Intelligence Intern',
            defaults={
                'posting_type': 'INTERNSHIP',
                'description': 'DataStride is seeking an ML Intern to assist in building predictive analytics engines, NLP pipelines, and data preprocessing workflows.',
                'responsibilities': 'Perform exploratory data analysis and feature engineering on large tabular datasets.\nTrain and benchmark scikit-learn models.\nDocument model performance metrics and build evaluation pipelines.',
                'location': 'Hyderabad (Hybrid)',
                'stipend_or_salary': '₹35,000 / month',
                'min_cgpa': Decimal('7.50'),
                'allowed_branches': 'Computer Science & Engineering, Artificial Intelligence & Data Science, Information Technology',
                'open_positions': 3,
                'deadline': (timezone.now() + timedelta(days=20)).date(),
                'is_active': True
            }
        )
        p3_reqs = [
            ('Python', 'ADVANCED', True),
            ('Machine Learning', 'INTERMEDIATE', True),
            ('Pandas', 'ADVANCED', True),
            ('Scikit-Learn', 'INTERMEDIATE', True),
            ('SQL', 'BEGINNER', False)
        ]
        for s_name, min_lvl, mand in p3_reqs:
            if s_name in skill_objs:
                PostingRequiredSkill.objects.get_or_create(
                    posting=p3,
                    skill=skill_objs[s_name],
                    defaults={'minimum_proficiency': min_lvl, 'is_mandatory': mand}
                )

        # 5. Create Applications
        # Priya applied to Frontend React Intern -> High match, Shortlisted
        app1, _ = Application.objects.get_or_create(
            posting=p2,
            student=s2_profile,
            defaults={
                'match_percentage_at_apply': Decimal('95.00'),
                'status': 'INTERVIEW_SCHEDULED',
                'interview_date': timezone.now() + timedelta(days=3, hours=4),
                'interview_mode': 'ONLINE',
                'interview_link_or_venue': 'https://meet.google.com/nex-dev-int',
                'company_feedback': 'Impressive portfolio of React components. Technical round scheduled.'
            }
        )
        Notification.objects.get_or_create(
            recipient=s2_user,
            title='Interview Scheduled: Frontend React Intern',
            defaults={
                'message': 'Nexas Technologies has scheduled your technical interview for Friday via Google Meet.',
                'notification_type': 'INTERVIEW_SCHEDULED',
                'link': '/internships/my-applications/'
            }
        )

        # Arjun applied to ML Intern -> High match, Shortlisted
        app2, _ = Application.objects.get_or_create(
            posting=p3,
            student=s3_profile,
            defaults={
                'match_percentage_at_apply': Decimal('92.50'),
                'status': 'SHORTLISTED',
                'company_feedback': 'Strong math and scikit-learn foundations.'
            }
        )

        # Rahul applied to Python Backend Intern -> Partial match (Gap: Django missing)
        app3, _ = Application.objects.get_or_create(
            posting=p1,
            student=s1_profile,
            defaults={
                'match_percentage_at_apply': Decimal('65.00'),
                'status': 'UNDER_REVIEW',
                'company_feedback': 'Good Python & SQL experience. Reviewing project repository.'
            }
        )

        # 6. Sample Placement Record
        PlacementRecord.objects.get_or_create(
            student=s2_profile,
            company=c1_profile,
            job_role='Associate Software Development Engineer (Frontend)',
            defaults={
                'package_lpa': Decimal('12.50'),
                'acceptance_status': 'ACCEPTED'
            }
        )

        # 7. Campus Notices
        from analytics.models import CampusNotice
        notices_data = [
            ('Campus Placement Drive: Nexas Technologies & DataStride AI',
             'Nexas Technologies and DataStride AI have published summer internship and full-time hiring drives. Eligible candidates with >= 6.5 CGPA can apply through the portal.',
             'PLACEMENT'),
            ('Semester Examination Schedule Released',
             'The final end-semester theoretical and laboratory examination schedules for all engineering branches have been published on the university portal.',
             'ACADEMIC'),
            ('Faculty Development Programme (FDP) Registration',
             'Department of Computer Science is conducting a 3-day workshop on Generative AI and Microservices. Interested faculty and student coordinators may enroll.',
             'WORKSHOP'),
        ]
        for n_title, n_content, n_type in notices_data:
            CampusNotice.objects.get_or_create(
                title=n_title,
                defaults={'posted_by': faculty_user, 'content': n_content, 'notice_type': n_type}
            )

        self.stdout.write(self.style.SUCCESS('Successfully seeded database with users, skills, postings, and applications!'))
        self.stdout.write(self.style.SUCCESS('Demo Credentials:'))
        self.stdout.write(self.style.WARNING('  Faculty/Admin: faculty_admin / admin123'))
        self.stdout.write(self.style.WARNING('  Company 1:     nexas_tech / company123'))
        self.stdout.write(self.style.WARNING('  Company 2:     datastride_ai / company123'))
        self.stdout.write(self.style.WARNING('  Student 1:     rahul_cse / student123 (Backend / Skill Gap demo)'))
        self.stdout.write(self.style.WARNING('  Student 2:     priya_it / student123 (Frontend / Placed demo)'))
        self.stdout.write(self.style.WARNING('  Student 3:     arjun_ai / student123 (AI/Data Science demo)'))
