from django.db import models

# --- NEW MODEL: Program (Minimal changes applied) ---
class Program(models.Model):
    name = models.CharField(max_length=200, unique=True) # Added unique=True for better indexing

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

# --- NEW MODEL: Semester (ADDED) ---
# This model links the Program to the Semester Number, matching the CSV structure.
class Semester(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    number = models.IntegerField()
    
    class Meta:
        unique_together = ('program', 'number')
        ordering = ['program', 'number']

    def __str__(self):
        return f"{self.program.name} - S{self.number}"
# -------------------------------------

# --- CHANGES IN Course Model ---
class Course(models.Model):
    # CHANGED: Program FK removed. Now links directly to the Semester object.
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='courses') 
    name = models.CharField(max_length=200)
    
    # REMOVED: program field removed, semester field changed to FK to Semester model.
    
    class Meta:
        ordering = ['semester__program__name', 'semester__number', 'name']
        unique_together = ('semester', 'name') # Added unique constraint
    
    def __str__(self):
        return f"{self.name} (Semester {self.semester.number})"


# --- CHANGES IN Topic Model ---
class Topic(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='topics')
    name = models.CharField(max_length=200) # Topic name
    
    # ADDED: Raw string field for CSV import (CRITICAL)
    prerequisites_raw = models.TextField(blank=True, null=True, verbose_name="Raw Prereqs (CSV)")
    
    # Existing ManyToMany field for actual linking
    prerequisites = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='required_for')
    why = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
        unique_together = ('course', 'name') # Added unique constraint

    def __str__(self):
        return self.name