# models.py
from django.db import models

class Class(models.Model):
    class_id = models.AutoField(primary_key=True)
    class_name = models.CharField(max_length=50, unique=True)  # Added unique constraint
    
    def __str__(self):
        return self.class_name

class Student(models.Model):
    student_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=50)
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='students')
    
    class Meta:
        # Ensure roll number is unique within each class
        unique_together = ('roll_number', 'class_id')
    
    def __str__(self):
        return f"{self.name} - {self.roll_number} ({self.class_id.class_name})"

class Subject(models.Model):
    subject_id = models.AutoField(primary_key=True)
    subject_name = models.CharField(max_length=100)
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='subjects', default=1)
  # Added class relationship
    
    class Meta:
        # Ensure subject name is unique within each class
        unique_together = ('subject_name', 'class_id')
    
    def __str__(self):
        return f"{self.subject_name} ({self.class_id.class_name})"

class Script(models.Model):
    script_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='scripts')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='scripts')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # Ensure one script per student per subject
        unique_together = ('student', 'subject')
    
    def __str__(self):
        return f"Script: {self.student.name} - {self.subject.subject_name}"
    
    def clean(self):
        # Custom validation to ensure student and subject belong to same class
        from django.core.exceptions import ValidationError
        if self.student.class_id != self.subject.class_id:
            raise ValidationError("Student and subject must belong to the same class.")

class OCRData(models.Model):
    ocr_id = models.AutoField(primary_key=True)
    script = models.ForeignKey(Script, on_delete=models.CASCADE, related_name='ocr_data')
    page_number = models.IntegerField()
    ocr_json = models.JSONField()
    structured_json = models.JSONField()
    key_json = models.JSONField()
    context = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # Ensure unique page per script
        unique_together = ('script', 'page_number')
    
    def __str__(self):
        return f"OCR Data: {self.script} - Page {self.page_number}"