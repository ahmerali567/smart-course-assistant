import os
from django.core.management.base import BaseCommand
from django.conf import settings
from advisor.models import Program, Semester, Course, Topic
from django.db import transaction

def clean_name(name):
    name = name.strip()
    name = name.removesuffix('.')
    name = name.removesuffix(',')
    if name.endswith('(conceptual)'):
        name = name[:-12].strip()
    return name.strip()

class Command(BaseCommand):
    help = 'Loads curriculum data from file with robust prerequisite linking.'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str)

    def handle(self, *args, **options):
        file_path = options['file_path']

        if not os.path.exists(file_path):
            file_path = os.path.join(settings.BASE_DIR, file_path)
            if not os.path.exists(file_path):
                self.stdout.write(self.style.ERROR("File not found"))
                return

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [l for l in f.readlines()[1:] if l.strip()]

        self.stdout.write(self.style.SUCCESS("--- Starting Curriculum Import ---"))

        cleaned_data_for_pass2 = []

        with transaction.atomic():

            # ---------- PASS 1 ----------
            self.stdout.write("--- PASS 1: Creating Topics ---")

            for line in lines:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) != 6:
                    self.stdout.write(self.style.WARNING(f"Skipping bad line: {line}"))
                    continue

                program_name, semester_str, course_name, topic_name, prereqs_str, why = parts

                try:
                    semester_num = int(semester_str)
                except ValueError:
                    continue

                program, _ = Program.objects.get_or_create(
                    name=clean_name(program_name)
                )
                semester, _ = Semester.objects.get_or_create(
                    program=program,
                    number=semester_num
                )
                course, _ = Course.objects.get_or_create(
                    semester=semester,
                    name=clean_name(course_name)
                )

                topic, _ = Topic.objects.get_or_create(
                    course=course,
                    name=clean_name(topic_name)
                )

                topic.prerequisites_raw = prereqs_str
                topic.why = why
                topic.save()

                cleaned_data_for_pass2.append({
                    "topic": topic,
                    "prereqs": prereqs_str
                })

            self.stdout.write(self.style.SUCCESS(
                f"Created {Topic.objects.count()} topics"
            ))

            # ---------- PASS 2 ----------
            self.stdout.write("--- PASS 2: Linking Prerequisites ---")

            all_topics_map = {
                f"{t.course.id}:{clean_name(t.name).lower()}": t
                for t in Topic.objects.all()
            }

            link_count = 0

            for item in cleaned_data_for_pass2:
                topic = item["topic"]
                prereqs = item["prereqs"]

                topic.prerequisites.clear()

                for p in prereqs.split(','):
                    p_clean = clean_name(p)
                    if not p_clean:
                        continue

                    key = f"{topic.course.id}:{p_clean.lower()}"
                    prereq_topic = all_topics_map.get(key)

                    if prereq_topic and prereq_topic != topic:
                        topic.prerequisites.add(prereq_topic)
                        link_count += 1
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Prereq NOT FOUND: "{p_clean}" for "{topic.name}"'
                            )
                        )

        self.stdout.write(self.style.SUCCESS(
            f"Import complete ✔ | {link_count} prerequisite links created"
        ))
