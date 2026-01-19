from django.shortcuts import render, get_object_or_404
from .models import Program, Course, Topic, Semester # Added Semester import
from .utils_ml import fuzzy_search_topics
from django.db.models import Q, F # Added Q and F for robust filtering (Optional, but good practice)
from datetime import datetime # Added datetime import

def homepage(request):
    programs = Program.objects.all().order_by('name')
    semesters = None
    courses = None
    results = None
    message = None

    program_id = request.GET.get('program')
    semester = request.GET.get('semester')
    course_id = request.GET.get('course')

    if program_id:
        # --- CRITICAL FIX 1 (Filtering Semesters by Program) ---
        # The filter path is Course -> Semester -> Program
        semesters = Course.objects.filter(
            semester__program__id=program_id 
        ).values_list('semester__number', flat=True).distinct().order_by('semester__number')

    if program_id and semester:
        # --- CRITICAL FIX 2 (Filtering Courses by Semester and Program) ---
        courses = Course.objects.filter(
            semester__program__id=program_id, 
            semester__number=semester
        ).order_by('name')

    if request.method == 'POST' and course_id:
        topic_input = request.POST.get('topic_input', '').strip()
        if topic_input:
            course = get_object_or_404(Course, id=course_id)
            topics = Topic.objects.filter(course=course)
            matches = fuzzy_search_topics(topic_input, topics)
            if matches:
                results = []
                for topic, score in matches:
                    prereqs = topic.prerequisites.all()
                    prereq_names = [p.name for p in prereqs] if prereqs.exists() else ["No prerequisites required."]
                    results.append({
                        'topic': topic.name,
                        'score': round(score * 100, 2),
                        'prerequisites': prereq_names,
                        'why': topic.why if topic.why else "No explanation provided."
                    })
                # Session and message logic (Untouched)
                message = f"Found {len(results)} matching topic(s) for '{topic_input}'."
                # Store recent search in session
                recent_searches = request.session.get('recent_searches', [])
                recent_searches.insert(0, {
                    'topic_input': topic_input,
                    'course_name': course.name,
                    'results_count': len(results),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                request.session['recent_searches'] = recent_searches[:5] 
            else:
                message = f"No matching topics found for '{topic_input}'."
        else:
            message = "Please enter a topic to search."

    selected_course_name = None
    if course_id:
        try:
            selected_course_name = Course.objects.get(id=course_id).name
        except Course.DoesNotExist:
            selected_course_name = None

    context = {
        'programs': programs,
        'semesters': semesters,
        'courses': courses,
        'results': results,
        'message': message,
        'selected_program': program_id,
        'selected_semester': semester,
        'selected_course': course_id,
        'selected_course_name': selected_course_name,
        'topic_input': request.POST.get('topic_input', '') if request.method == 'POST' else '',
        'recent_searches': request.session.get('recent_searches', []),
    }
    return render(request, 'advisor/blackbox.html', context)