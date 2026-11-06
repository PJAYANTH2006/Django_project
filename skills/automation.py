import re
from decimal import Decimal
from django.db.models import Q
from skills.models import Skill, StudentSkill, SkillResource
from internships.models import InternshipPosting, PostingRequiredSkill


def calculate_skill_gap(student_profile, posting):
    """
    Automated Skill Gap Analysis Engine:
    Compares student's verified and declared skills with the posting's required skills.
    Calculates weighted match percentage, identifies matched vs missing skills,
    and attaches curated learning resources for missing skills.
    """
    required_skills = posting.required_skills.select_related('skill').all()
    if not required_skills.exists():
        return {
            'match_percentage': 100.0,
            'matched_skills': [],
            'missing_skills': [],
            'proficiency_gap_count': 0,
            'total_required': 0,
            'summary': 'No specific skill requirements listed.'
        }

    # Fetch student's skills mapped to dict: {skill_id: (proficiency, weight)}
    student_skills_qs = StudentSkill.objects.filter(student=student_profile).select_related('skill')
    student_skills_map = {
        ss.skill_id: {
            'skill': ss.skill,
            'proficiency': ss.proficiency,
            'display_prof': ss.get_proficiency_display(),
            'weight': ss.weight
        }
        for ss in student_skills_qs
    }

    total_possible_score = 0.0
    earned_score = 0.0
    matched_skills = []
    missing_skills = []
    proficiency_gap_count = 0

    for req in required_skills:
        req_weight = req.weight  # 1 for Beginner, 2 for Intermediate, 3 for Advanced
        total_possible_score += req_weight

        if req.skill_id in student_skills_map:
            s_data = student_skills_map[req.skill_id]
            student_weight = s_data['weight']

            if student_weight >= req_weight:
                # Full credit
                earned_score += req_weight
                level_status = 'MET'
            else:
                # Partial credit: student knows the skill, but at lower proficiency
                earned_score += (req_weight * 0.6)
                level_status = 'BELOW_REQUIRED'
                proficiency_gap_count += 1

            matched_skills.append({
                'skill': req.skill,
                'required_proficiency': req.minimum_proficiency,
                'required_display': req.get_minimum_proficiency_display(),
                'student_proficiency': s_data['proficiency'],
                'student_display': s_data['display_prof'],
                'level_status': level_status,
                'is_mandatory': req.is_mandatory
            })
        else:
            # Missing skill completely
            resources = SkillResource.objects.filter(skill=req.skill)
            missing_skills.append({
                'skill': req.skill,
                'required_proficiency': req.minimum_proficiency,
                'required_display': req.get_minimum_proficiency_display(),
                'is_mandatory': req.is_mandatory,
                'resources': resources
            })

    if total_possible_score > 0:
        match_percentage = round((earned_score / total_possible_score) * 100.0, 1)
    else:
        match_percentage = 100.0

    return {
        'match_percentage': match_percentage,
        'matched_skills': matched_skills,
        'missing_skills': missing_skills,
        'proficiency_gap_count': proficiency_gap_count,
        'total_required': required_skills.count(),
        'missing_count': len(missing_skills),
        'matched_count': len(matched_skills),
    }


def check_placement_eligibility(student_profile, posting, match_percentage):
    """
    Automated Placement Eligibility Checker:
    Multi-factor evaluation checking:
    1. CGPA criteria
    2. Academic Branch criteria
    3. Technical Skill readiness threshold (>= 50%)
    """
    reasons = []

    # 1. CGPA Check
    cgpa_eligible = student_profile.cgpa >= posting.min_cgpa
    if not cgpa_eligible:
        reasons.append(f"Requires minimum CGPA of {posting.min_cgpa} (Current: {student_profile.cgpa})")

    # 2. Branch Check
    allowed_branches = [b.lower() for b in posting.get_allowed_branches_list()]
    student_branch = student_profile.branch.lower().strip()
    branch_eligible = any(student_branch in b or b in student_branch for b in allowed_branches)
    if not branch_eligible:
        reasons.append(f"Branch '{student_profile.branch}' is not in allowed branches list")

    # 3. Skill match threshold
    skill_ready = match_percentage >= 50.0

    if cgpa_eligible and branch_eligible and skill_ready:
        status = 'ELIGIBLE'
        badge_class = 'bg-success'
        summary = 'Eligible to Apply: You meet all academic, branch, and skill criteria.'
    elif cgpa_eligible and branch_eligible and not skill_ready:
        status = 'SKILLS_IMPROVEMENT_REQUIRED'
        badge_class = 'bg-warning text-dark'
        summary = f'Skills Improvement Required: You meet academic criteria, but your skill match ({match_percentage}%) is below the recommended 50% readiness threshold.'
    else:
        status = 'NOT_ELIGIBLE'
        badge_class = 'bg-danger'
        summary = f"Not Eligible: {'; '.join(reasons)}"

    return {
        'status': status,
        'badge_class': badge_class,
        'summary': summary,
        'cgpa_eligible': cgpa_eligible,
        'branch_eligible': branch_eligible,
        'skill_ready': skill_ready,
        'reasons': reasons,
        'can_apply': cgpa_eligible and branch_eligible  # Can submit, but flagged accordingly
    }


def get_recommended_postings_for_student(student_profile, limit=10):
    """
    Smart Internship Recommendation Engine:
    Ranks all active postings for this student based on skill match % and eligibility.
    """
    active_postings = InternshipPosting.objects.filter(is_active=True).select_related('company')
    recommendations = []

    for posting in active_postings:
        gap_info = calculate_skill_gap(student_profile, posting)
        elig_info = check_placement_eligibility(student_profile, posting, gap_info['match_percentage'])

        recommendations.append({
            'posting': posting,
            'match_percentage': gap_info['match_percentage'],
            'gap_info': gap_info,
            'eligibility': elig_info,
        })

    # Sort primarily by match percentage descending, secondarily by can_apply
    recommendations.sort(key=lambda x: (x['eligibility']['can_apply'], x['match_percentage']), reverse=True)
    return recommendations[:limit]


def extract_skills_from_text(raw_text):
    """
    Rule-based skill extraction from resume text using regex and alias taxonomy.
    """
    if not raw_text:
        return []

    text_lower = " " + raw_text.lower() + " "
    detected_skills = []

    all_skills = Skill.objects.select_related('category').all()
    for skill in all_skills:
        # Build search patterns: skill name + all aliases
        patterns = [skill.name.lower()]
        if skill.aliases:
            aliases = [a.strip().lower() for a in skill.aliases.split(',') if a.strip()]
            patterns.extend(aliases)

        found = False
        for p in patterns:
            # Escape regex characters (e.g. C++, C#)
            escaped = re.escape(p)
            # Match with word boundaries or space/punctuation
            if re.search(r'(?<![a-zA-Z0-9])' + escaped + r'(?![a-zA-Z0-9])', text_lower):
                found = True
                break

        if found:
            detected_skills.append(skill)

    return detected_skills


def extract_text_from_pdf_file(uploaded_file):
    """
    Extracts text from uploaded PDF or plain text file.
    """
    text = ""
    try:
        import pypdf
        reader = pypdf.PdfReader(uploaded_file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        # Fallback for plain text or if pypdf has a read error
        try:
            uploaded_file.seek(0)
            text = uploaded_file.read().decode('utf-8', errors='ignore')
        except Exception:
            text = ""

    return text
