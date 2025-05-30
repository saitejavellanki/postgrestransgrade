# views.py - Updated version with KeyOCR and Script modifications
from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from .models import Class, Student, Subject, Script, OCRData, KeyOCR

@method_decorator(csrf_exempt, name='dispatch')
class ClassView(View):
    def get(self, request):
        data = list(Class.objects.values())
        return JsonResponse(data, safe=False)

    def post(self, request):
        try:
            data = json.loads(request.body)
            new_class = Class.objects.create(class_name=data['class_name'])
            return JsonResponse({'message': 'Class created', 'class_id': new_class.class_id})
        except IntegrityError:
            return JsonResponse({'error': 'Class name already exists'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class StudentView(View):
    def get(self, request):
        # Get class_id from query parameters if provided
        class_id = request.GET.get('class_id')
        
        if class_id:
            # Return students for specific class
            try:
                class_obj = Class.objects.get(class_id=class_id)
                students = Student.objects.filter(class_id=class_obj)
                data = []
                for student in students:
                    data.append({
                        'student_id': student.student_id,
                        'name': student.name,
                        'roll_number': student.roll_number,
                        'class_id': student.class_id.class_id,
                        'class_name': student.class_id.class_name
                    })
                return JsonResponse(data, safe=False)
            except Class.DoesNotExist:
                return JsonResponse({'error': 'Invalid class_id'}, status=400)
        else:
            # Return all students with class information
            students = Student.objects.select_related('class_id').all()
            data = []
            for student in students:
                data.append({
                    'student_id': student.student_id,
                    'name': student.name,
                    'roll_number': student.roll_number,
                    'class_id': student.class_id.class_id,
                    'class_name': student.class_id.class_name
                })
            return JsonResponse(data, safe=False)

    def post(self, request):
        try:
            data = json.loads(request.body)
            
            # Get the actual Class object from DB
            class_obj = Class.objects.get(class_id=data['class_id'])
            student = Student.objects.create(
                name=data['name'],
                roll_number=data['roll_number'],
                class_id=class_obj
            )

            return JsonResponse({'message': 'Student created', 'student_id': student.student_id})
        
        except Class.DoesNotExist:
            return JsonResponse({'error': 'Invalid class_id'}, status=400)
        except IntegrityError:
            return JsonResponse({'error': 'Student with this roll number already exists in this class'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class SubjectView(View):
    def get(self, request):
        # Get class_id from query parameters if provided
        class_id = request.GET.get('class_id')
        
        if class_id:
            # Return subjects for specific class
            try:
                class_obj = Class.objects.get(class_id=class_id)
                subjects = Subject.objects.filter(class_id=class_obj)
                data = []
                for subject in subjects:
                    # Check if key OCR exists for this subject
                    has_key_ocr = hasattr(subject, 'key_ocr') and subject.key_ocr is not None
                    data.append({
                        'subject_id': subject.subject_id,
                        'subject_name': subject.subject_name,
                        'class_id': subject.class_id.class_id,
                        'class_name': subject.class_id.class_name,
                        'has_key_ocr': has_key_ocr
                    })
                return JsonResponse(data, safe=False)
            except Class.DoesNotExist:
                return JsonResponse({'error': 'Invalid class_id'}, status=400)
        else:
            # Return all subjects with class information
            subjects = Subject.objects.select_related('class_id').all()
            data = []
            for subject in subjects:
                # Check if key OCR exists for this subject
                has_key_ocr = hasattr(subject, 'key_ocr') and subject.key_ocr is not None
                data.append({
                    'subject_id': subject.subject_id,
                    'subject_name': subject.subject_name,
                    'class_id': subject.class_id.class_id,
                    'class_name': subject.class_id.class_name,
                    'has_key_ocr': has_key_ocr
                })
            return JsonResponse(data, safe=False)

    def post(self, request):
        try:
            data = json.loads(request.body)
            subject_name = data['subject_name'].strip()
            class_id = data['class_id']
            
            # Validate that class exists
            try:
                class_obj = Class.objects.get(class_id=class_id)
            except Class.DoesNotExist:
                return JsonResponse({'error': 'Invalid class_id'}, status=400)
            
            # Check if subject already exists for this specific class
            if Subject.objects.filter(
                subject_name__iexact=subject_name, 
                class_id=class_obj
            ).exists():
                return JsonResponse({
                    'error': f'Subject "{subject_name}" already exists for class "{class_obj.class_name}"'
                }, status=400)
            
            # Create subject for this class
            subject = Subject.objects.create(
                subject_name=subject_name,
                class_id=class_obj
            )
            
            return JsonResponse({
                'message': 'Subject created successfully',
                'subject_id': subject.subject_id,
                'class_name': class_obj.class_name
            })
            
        except KeyError as e:
            return JsonResponse({'error': f'Missing required field: {str(e)}'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class KeyOCRView(View):
    def get(self, request):
        # Get subject_id from query parameters if provided
        subject_id = request.GET.get('subject_id')
        
        if subject_id:
            try:
                key_ocr = KeyOCR.objects.select_related('subject', 'subject__class_id').get(subject_id=subject_id)
                data = {
                    'key_ocr_id': key_ocr.key_ocr_id,
                    'subject_id': key_ocr.subject.subject_id,
                    'subject_name': key_ocr.subject.subject_name,
                    'class_id': key_ocr.subject.class_id.class_id,
                    'class_name': key_ocr.subject.class_id.class_name,
                    'key_json': key_ocr.key_json,
                    'context': key_ocr.context,
                    'created_at': key_ocr.created_at,
                    'updated_at': key_ocr.updated_at
                }
                return JsonResponse(data)
            except KeyOCR.DoesNotExist:
                return JsonResponse({'error': 'Key OCR not found for this subject'}, status=404)
        else:
            # Return all key OCRs
            key_ocrs = KeyOCR.objects.select_related('subject', 'subject__class_id').all()
            data = []
            for key_ocr in key_ocrs:
                data.append({
                    'key_ocr_id': key_ocr.key_ocr_id,
                    'subject_id': key_ocr.subject.subject_id,
                    'subject_name': key_ocr.subject.subject_name,
                    'class_id': key_ocr.subject.class_id.class_id,
                    'class_name': key_ocr.subject.class_id.class_name,
                    'key_json': key_ocr.key_json,
                    'context': key_ocr.context,
                    'created_at': key_ocr.created_at,
                    'updated_at': key_ocr.updated_at
                })
            return JsonResponse(data, safe=False)

    def post(self, request):
        try:
            data = json.loads(request.body)
            
            # Validate that subject exists
            try:
                subject = Subject.objects.get(subject_id=data['subject_id'])
            except Subject.DoesNotExist:
                return JsonResponse({'error': 'Invalid subject_id'}, status=400)
            
            # Check if key OCR already exists for this subject
            if KeyOCR.objects.filter(subject=subject).exists():
                return JsonResponse({
                    'error': f'Key OCR already exists for subject "{subject.subject_name}"'
                }, status=400)
            
            # Create key OCR - make context optional
            key_ocr = KeyOCR.objects.create(
                subject=subject,
                key_json=data['key_json'],
                context=data.get('context', '')  # Use empty string as default if context not provided
            )
            
            return JsonResponse({
                'message': 'Key OCR created successfully',
                'key_ocr_id': key_ocr.key_ocr_id,
                'subject_name': subject.subject_name,
                'class_name': subject.class_id.class_name
            })
            
        except KeyError as e:
            return JsonResponse({'error': f'Missing required field: {str(e)}'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def put(self, request):
        try:
            data = json.loads(request.body)
            
            # Get key OCR by subject_id or key_ocr_id
            if 'subject_id' in data:
                try:
                    key_ocr = KeyOCR.objects.get(subject_id=data['subject_id'])
                except KeyOCR.DoesNotExist:
                    return JsonResponse({'error': 'Key OCR not found for this subject'}, status=404)
            elif 'key_ocr_id' in data:
                try:
                    key_ocr = KeyOCR.objects.get(key_ocr_id=data['key_ocr_id'])
                except KeyOCR.DoesNotExist:
                    return JsonResponse({'error': 'Key OCR not found'}, status=404)
            else:
                return JsonResponse({'error': 'Either subject_id or key_ocr_id is required'}, status=400)
            
            # Only update fields that are provided and not empty
            if 'key_json' in data and data['key_json']:  # Only update if key_json is provided and not empty
                key_ocr.key_json = data['key_json']
            
            if 'context' in data:  # Update context if provided (even if empty string)
                key_ocr.context = data['context']
            
            key_ocr.save()
            
            return JsonResponse({
                'message': 'Key OCR updated successfully',
                'key_ocr_id': key_ocr.key_ocr_id
            })
            
        except KeyError as e:
            return JsonResponse({'error': f'Missing required field: {str(e)}'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ScriptView(View):
    def get(self, request):
        # Get query parameters for filtering
        student_id = request.GET.get('student_id')
        subject_id = request.GET.get('subject_id')
        class_id = request.GET.get('class_id')
        
        scripts = Script.objects.select_related('student', 'subject', 'class_id')
        
        # Apply filters if provided
        if student_id:
            scripts = scripts.filter(student=student_id)
        if subject_id:
            scripts = scripts.filter(subject=subject_id)
        if class_id:
            scripts = scripts.filter(class_id=class_id)
        
        data = []
        for script in scripts:
            data.append({
                'script_id': script.script_id,
                'student_id': script.student.student_id,
                'student_name': script.student.name,
                'subject_id': script.subject.subject_id,
                'subject_name': script.subject.subject_name,
                'class_id': script.class_id.class_id,
                'class_name': script.class_id.class_name,
                'uploaded_at': script.uploaded_at
            })
        return JsonResponse(data, safe=False)

    def post(self, request):
        try:
            data = json.loads(request.body)
            
            # Validate that student and subject exist
            try:
                student = Student.objects.get(student_id=data['student_id'])
                subject = Subject.objects.get(subject_id=data['subject_id'])
            except Student.DoesNotExist:
                return JsonResponse({'error': 'Invalid student_id'}, status=400)
            except Subject.DoesNotExist:
                return JsonResponse({'error': 'Invalid subject_id'}, status=400)
            
            # Validate that student and subject belong to same class
            if student.class_id != subject.class_id:
                return JsonResponse({
                    'error': 'Student and subject must belong to the same class'
                }, status=400)
            
            # Check if script already exists
            existing_script = Script.objects.filter(
                student=student,
                subject=subject
            ).first()
            
            if existing_script:
                return JsonResponse({
                    'error': f'Script already exists for student {student.name} and subject {subject.subject_name}',
                    'script_id': existing_script.script_id
                }, status=400)
            
            # Create new script - class_id will be auto-populated from student's class
            script = Script.objects.create(
                student=student,
                subject=subject,
                class_id=student.class_id  # Explicitly set class_id
            )
            return JsonResponse({
                'message': 'Script created',
                'script_id': script.script_id,
                'class_id': script.class_id.class_id,
                'class_name': script.class_id.class_name
            })
            
        except KeyError as e:
            return JsonResponse({'error': f'Missing required field: {str(e)}'}, status=400)
        except IntegrityError as e:
            return JsonResponse({'error': f'Script already exists for this student and subject'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class OCRDataView(View):
    def get(self, request):
        # Get query parameters for filtering
        script_id = request.GET.get('script_id')
        
        if script_id:
            # Return OCR data for specific script
            try:
                script = Script.objects.get(script_id=script_id)
                ocr_data = OCRData.objects.filter(script=script).order_by('page_number')
                data = []
                for ocr in ocr_data:
                    data.append({
                        'ocr_id': ocr.ocr_id,
                        'script_id': ocr.script.script_id,
                        'page_number': ocr.page_number,
                        'ocr_json': ocr.ocr_json,
                        'structured_json': ocr.structured_json,
                        'context': ocr.context,
                        'created_at': ocr.created_at
                    })
                return JsonResponse(data, safe=False)
            except Script.DoesNotExist:
                return JsonResponse({'error': 'Invalid script_id'}, status=400)
        else:
            # Return all OCR data
            ocr_data = OCRData.objects.select_related('script').all()
            data = []
            for ocr in ocr_data:
                data.append({
                    'ocr_id': ocr.ocr_id,
                    'script_id': ocr.script.script_id,
                    'page_number': ocr.page_number,
                    'ocr_json': ocr.ocr_json,
                    'structured_json': ocr.structured_json,
                    'context': ocr.context,
                    'created_at': ocr.created_at
                })
            return JsonResponse(data, safe=False)

    def post(self, request):
        try:
            data = json.loads(request.body)
            
            # Validate that script exists
            try:
                script = Script.objects.get(script_id=data['script_id'])
            except Script.DoesNotExist:
                return JsonResponse({'error': 'Invalid script_id'}, status=400)
            
            # Create OCR data
            ocr = OCRData.objects.create(
                script=script,
                page_number=data['page_number'],
                ocr_json=data['ocr_json'],
                structured_json=data['structured_json'],
                context=data['context']
            )
            return JsonResponse({
                'message': 'OCR Data created',
                'ocr_id': ocr.ocr_id,
                'script_id': script.script_id
            })
            
        except KeyError as e:
            return JsonResponse({'error': f'Missing required field: {str(e)}'}, status=400)
        except IntegrityError:
            return JsonResponse({'error': 'OCR data already exists for this script and page number'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)