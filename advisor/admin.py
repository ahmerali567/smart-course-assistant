from django.contrib import admin
from .models import Program, Semester, Course, Topic

# --- Program Admin ---
@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# --- Semester Admin ---
@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('number', 'program')
    list_filter = ('program',)

# --- Course Admin ---
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'semester', 'get_program_name')
    search_fields = ('name', 'semester__program__name')
    list_filter = ('semester__program', 'semester__number') 

    @admin.display(description='Program')
    def get_program_name(self, obj):
        return obj.semester.program.name

# --- Topic Admin ---
@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    # 'name' field is used as per your models.py
    list_display = ('name', 'course', 'get_semester_name', 'get_program_name') 
    search_fields = ('name', 'course__name')
    list_filter = ('course__semester__program', 'course__semester') 
    
    # Fields for Admin Form
    fields = ('course', 'name', 'why', 'prerequisites', 'prerequisites_raw')
    filter_horizontal = ('prerequisites',)

    @admin.display(description='Semester')
    def get_semester_name(self, obj):
        return f"S{obj.course.semester.number}"

    @admin.display(description='Program')
    def get_program_name(self, obj):
        return obj.course.semester.program.name