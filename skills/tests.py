from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from accounts.models import StudentProfile, CompanyProfile
from skills.models import SkillCategory, Skill, StudentSkill, SkillResource
from internships.models import InternshipPosting, PostingRequiredSkill
from skills.automation import (
    calculate_skill_gap,
    check_placement_eligibility,
    extract_skills_from_text
)

User = get_user_model()

class SmartAutomationEngineTestCase(TestCase):
    def setUp(self):
        # Category & Skills
        self.cat_web = SkillCategory.objects.create(name='Web Development')
        self.cat_prog = SkillCategory.objects.create(name='Programming')

        self.skill_python = Skill.objects.create(name='Python', category=self.cat_prog, aliases='py, python3')
        self.skill_django = Skill.objects.create(name='Django', category=self.cat_web, aliases='django, drf')
        self.skill_sql = Skill.objects.create(name='SQL', category=self.cat_web, aliases='sql, mysql')
        self.skill_docker = Skill.objects.create(name='Docker', category=self.cat_web, aliases='docker, containerization')

        # Resource for Django
        SkillResource.objects.create(
            skill=self.skill_django,
            title='Django Official Docs',
            resource_url='https://docs.djangoproject.com'
        )

        # Users
        self.student_user = User.objects.create_user(username='test_student', role='STUDENT')
        self.student_profile = StudentProfile.objects.create(
            user=self.student_user,
            branch='Computer Science & Engineering',
            cgpa=Decimal('8.50')
        )

        self.company_user = User.objects.create_user(username='test_company', role='COMPANY')
        self.company_profile = CompanyProfile.objects.create(user=self.company_user, company_name='Acme Corp')

        # Student has Python (Advanced) and SQL (Intermediate) - missing Django
        StudentSkill.objects.create(student=self.student_profile, skill=self.skill_python, proficiency='ADVANCED')
        StudentSkill.objects.create(student=self.student_profile, skill=self.skill_sql, proficiency='INTERMEDIATE')

        # Posting requires Python, Django, SQL
        self.posting = InternshipPosting.objects.create(
            company=self.company_profile,
            title='Full Stack Django Developer',
            min_cgpa=Decimal('7.00'),
            allowed_branches='Computer Science & Engineering, Information Technology',
            deadline='2026-12-31'
        )
        PostingRequiredSkill.objects.create(posting=self.posting, skill=self.skill_python, minimum_proficiency='INTERMEDIATE')
        PostingRequiredSkill.objects.create(posting=self.posting, skill=self.skill_django, minimum_proficiency='INTERMEDIATE')
        PostingRequiredSkill.objects.create(posting=self.posting, skill=self.skill_sql, minimum_proficiency='INTERMEDIATE')

    def test_skill_gap_analysis(self):
        gap = calculate_skill_gap(self.student_profile, self.posting)
        # 3 required skills: Python (Intermediate=2 pts), Django (Intermediate=2 pts), SQL (Intermediate=2 pts) = Total 6 pts
        # Student has Python (Advanced=3, >= 2 -> 2 pts earned) and SQL (Intermediate=2 -> 2 pts earned) = 4 pts earned
        # Match % = (4 / 6) * 100 = 66.7%
        self.assertEqual(gap['total_required'], 3)
        self.assertEqual(gap['matched_count'], 2)
        self.assertEqual(gap['missing_count'], 1)
        self.assertAlmostEqual(gap['match_percentage'], 66.7, places=1)

        # Verify missing skill is Django and has learning resource attached
        missing_names = [m['skill'].name for m in gap['missing_skills']]
        self.assertIn('Django', missing_names)
        self.assertTrue(gap['missing_skills'][0]['resources'].exists())

    def test_placement_eligibility_checker(self):
        gap = calculate_skill_gap(self.student_profile, self.posting)
        elig = check_placement_eligibility(self.student_profile, self.posting, gap['match_percentage'])

        # CGPA 8.5 >= 7.0 (passed), Branch CSE in allowed (passed), Match 66.7% >= 50% (passed)
        self.assertEqual(elig['status'], 'ELIGIBLE')
        self.assertEqual(elig['status_display'], 'Eligible')
        self.assertTrue(elig['can_apply'])

        # Test skills improvement required status_display
        elig_low_skill = check_placement_eligibility(self.student_profile, self.posting, Decimal('40.0'))
        self.assertEqual(elig_low_skill['status'], 'SKILLS_IMPROVEMENT_REQUIRED')
        self.assertEqual(elig_low_skill['status_display'], 'Skills Improvement Required')

        # Test ineligible CGPA
        self.student_profile.cgpa = Decimal('6.00')
        self.student_profile.save()
        elig_low_cgpa = check_placement_eligibility(self.student_profile, self.posting, gap['match_percentage'])
        self.assertEqual(elig_low_cgpa['status'], 'NOT_ELIGIBLE')
        self.assertEqual(elig_low_cgpa['status_display'], 'Not Eligible')
        self.assertFalse(elig_low_cgpa['cgpa_eligible'])

    def test_proficiency_level_gap_detection(self):
        # Give student Django as Beginner (posting requires Intermediate)
        StudentSkill.objects.create(student=self.student_profile, skill=self.skill_django, proficiency='BEGINNER')
        gap = calculate_skill_gap(self.student_profile, self.posting)
        # All 3 skills are in profile, but Django is below required level
        self.assertEqual(gap['missing_count'], 0)
        self.assertEqual(gap['proficiency_gap_count'], 1)
        self.assertGreater(gap['match_percentage'], 70.0)

    def test_resume_skill_extraction(self):
        sample_resume_text = """
        John Doe - Software Engineer
        Proficient in Python programming and web APIs with Django.
        Experienced with relational databases like SQL, and container deployment using Docker.
        """
        detected = extract_skills_from_text(sample_resume_text)
        detected_names = [s.name for s in detected]

        self.assertIn('Python', detected_names)
        self.assertIn('Django', detected_names)
        self.assertIn('SQL', detected_names)
        self.assertIn('Docker', detected_names)
