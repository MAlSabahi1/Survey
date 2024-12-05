from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from .models import *
from .forms import *
import pandas as pd
from django.http import Http404, HttpResponse, JsonResponse
import csv
from collections import Counter
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.forms.models import model_to_dict
from django.views.decorators.csrf import csrf_exempt
from .utils import encode_id, decode_id


@login_required
@user_passes_test(lambda u: u.is_staff)
def create_entitys(request):
    if request.method == 'POST':
        form = EntitysForm(request.POST)
        if form.is_valid():
            entity = form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    else:
        form = EntitysForm()
    
    entities = Entitys.objects.filter(parent__isnull=True)  # جلب الكيانات الرئيسية فقط
    return render(request, 'survey/create_entitys.html', {'form': form, 'entities': entities})



def show_categories(request, pk):
    # فك تشفير pk
    entity_id = decode_id(pk)
    if entity_id is None:
        raise Http404("Invalid IDrrrr")
    
    entity = get_object_or_404(Entitys, pk=entity_id)
    staff_surveys = Surveys.objects.filter(category='staff', entities=entity)
    infrastructure_surveys = Surveys.objects.filter(category='infrastructure', entities=entity)
    systems_surveys = Surveys.objects.filter(category='systems', entities=entity)
    
    return render(request, 'survey/categories.html', {
        'entity': entity,
        'entity_encoded_id': encode_id(entity.id),  # تشفير الـ id للروابط
        'staff_surveys': staff_surveys,
        'infrastructure_surveys': infrastructure_surveys,
        'systems_surveys': systems_surveys,
    })


def show_questions_by_category(request, category, pk):
    # فك تشفير pk
    entity_id = decode_id(pk)
    # print(entity_id)
    if entity_id is None:
        raise Http404("Invalid or missing ID")  # إذا كان pk غير صالح
    
    # جلب الأسئلة بناءً على الفئة
    questions = Question.objects.filter(category=category, is_active=True)
    entity = get_object_or_404(Entitys, pk=entity_id)

    return render(request, 'survey/questions_by_category.html', {
        'entity_id':pk,
        'questions': questions,
        'category': category,
        'entity': entity,
    })

@login_required
def submit_survey(request, category, pk):
    # print(pk)
    entity_id = decode_id(pk)
    # print(entity_id,'kkkkkkkkkkkkkkkkkkkkkkkkkkk')
    if entity_id is None:
        raise Http404("Invalid IDiiii")
    # print(f"Category: {category}, PK: {pk}, Decoded ID: {entity_id}","gggggggggggggggggggggggggggggggggggggggggg")
    
    if request.method == 'POST':
        survey_name = request.POST.get('survey_name')

        # جلب الكيان المحدد بناءً على المعرّف
        entity = get_object_or_404(Entitys, pk=entity_id)

        # إنشاء استبيان جديد للمستخدم الحالي
        survey = Surveys.objects.create(category=category, user=request.user, name=survey_name)

        # ربط الاستبيان بالكيان المحدد
        survey.entities.add(entity)

        # معالجة الإجابات القادمة من الطلب
        for key, value in request.POST.items():
            if key.startswith('question_'):
                question_id = key.split('_')[1]
                question = get_object_or_404(Question, id=question_id)

                # قراءة الملاحظات الخاصة بالسؤال
                note_key = f"note_{question_id}"
                note = request.POST.get(note_key, "").strip()

                if question.question_type in ['text', 'yes_no']:
                    # الإجابة النصية أو نعم/لا يتم حفظها مباشرة
                    Answer.objects.create(
                        survey=survey, 
                        question=question, 
                        answer_text=value, 
                        note=note,  # حفظ الملاحظة
                        entity=entity
                    )
                elif question.question_type in ['multiple_choice', 'radio']:
                    # حفظ كل خيار كمجموعة إجابة منفصلة
                    for choice_id in request.POST.getlist(key):
                        choice = Choice.objects.get(id=choice_id)
                        Answer.objects.create(
                            survey=survey, 
                            question=question, 
                            choice_selected=choice, 
                            note=note,  # حفظ الملاحظة
                            entity=entity
                        )

        # إعادة التوجيه إلى صفحة التصنيفات مع الكيان المحدد
        return redirect('categories', pk)

    return HttpResponse("Invalid request", status=400)



@login_required
def delete_survey(request, survey_id, entity_id):
    # فك تشفير entity_id
    print(entity_id)
    decoded_entity_id = decode_id(entity_id)
    if decoded_entity_id is None:
        raise Http404("Invalid ID")
    
    # جلب الاستبيان بناءً على المعرّف
    survey = get_object_or_404(Surveys, id=survey_id, entities__id=decoded_entity_id)

    # حذف الاستبيان
    survey.delete()

    # إظهار رسالة نجاح
    messages.success(request, "تم حذف الاستبيان بنجاح.")

    # إعادة التوجيه إلى صفحة عرض التصنيفات
    return redirect('categories', entity_id)


def show_survey(request, survey_id):
    survey = get_object_or_404(Surveys, id=survey_id)
    answers = Answer.objects.filter(survey=survey)

    # تجميع الإجابات حسب السؤال
    questions_with_answers = {}
    for answer in answers:
        if answer.question not in questions_with_answers:
            questions_with_answers[answer.question] = []
        if answer.answer_text:
            questions_with_answers[answer.question].append(answer.answer_text)
        elif answer.choice_selected:
            questions_with_answers[answer.question].append(answer.choice_selected.text)

    return render(request, 'survey/view_survey.html', {
        'survey': survey,
        'questions_with_answers': questions_with_answers
    })



def is_admin(user):
    return user.is_authenticated and user.is_staff


def filter_questions(keywords=None, question_types=None):
    query = Q()

    if keywords:
        keyword_query = Q()
        for keyword in keywords:
            keyword_query |= Q(text__icontains=keyword)
        query &= keyword_query
    
    if question_types:
        query &= Q(question_type__in=question_types)

    return Question.objects.filter(query)




@login_required
@user_passes_test(is_admin)
def add_question(request):
    if request.method == 'POST':
        question_form = QuestionForm(request.POST)

        if question_form.is_valid():
            question = question_form.save(commit=False)
            # تأكد من حذف أو تعديل السطر التالي حسب ما إذا كنت تحتاج تعيين استبيان محدد للسؤال
            question.save()
            
            # حفظ الاختيارات إذا كان نوع السؤال "اختيار متعدد" أو "راديو"
            if question.question_type in ['multiple_choice', 'radio']:
                choices = request.POST.getlist('choices[]')
                for choice_text in choices:
                    if choice_text.strip():
                        Choice.objects.create(question=question, text=choice_text)
            
            # إرسال رد JSON مع رسالة النجاح
            return JsonResponse({'success': True, 'message': 'تم إضافة السؤال بنجاح!'})
        else:
            # إرسال رد JSON مع رسالة الخطأ
            return JsonResponse({'success': False, 'message': 'حدث خطأ أثناء إضافة السؤال. يرجى التحقق من البيانات وإعادة المحاولة.'})

    else:
        question_form = QuestionForm()

    return render(request, 'survey/add_question.html', {
        'question_form': question_form,
    })


@login_required
@user_passes_test(is_admin)
def questions_list(request):
    if request.method == 'GET':
        # الحصول على التصنيف إذا تم تحديده
        category = request.GET.get('category', None)
        if category:
            questions = Question.objects.filter(category=category)
        else:
            questions = Question.objects.all()
        
        # إذا كان الطلب AJAX، إرجاع JSON
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            questions_data = [
                {
                    'id': question.id,
                    'text': question.text,
                    'question_type': question.get_question_type_display(),
                    'category': question.get_category_display(),
                    'is_active': question.is_active  # تضمين حالة النشاط هنا

                } for question in questions
            ]
            return JsonResponse({'success': True, 'questions': questions_data})

        # إذا كان طلب عادي (غير AJAX)، عرض الصفحة
        return render(request, 'survey/questions_list.html', {'questions': questions})



# التعديل

@login_required
@user_passes_test(is_admin)
def update_question(request, question_id):
    if request.method == 'POST':
        question = get_object_or_404(Question, id=question_id)
        form = QuestionForm(request.POST, instance=question)

        if form.is_valid():
            # حفظ السؤال المحدث
            updated_question = form.save()

            # إذا كان نوع السؤال يدعم الخيارات، قم بتحديث الخيارات
            if updated_question.question_type in ['multiple_choice', 'radio']:
                updated_question.choices.all().delete()
                choices = request.POST.getlist('choices[]')
                for choice_text in choices:
                    if choice_text.strip():
                        Choice.objects.create(question=updated_question, text=choice_text)

            return JsonResponse({'success': True, 'message': 'تم تعديل السؤال بنجاح!'})
        else:
            return JsonResponse({'success': False, 'message': 'حدث خطأ أثناء تعديل السؤال.', 'errors': form.errors})

    # إذا كان الطلب GET (عرض السؤال وبياناته)
    question = get_object_or_404(Question, id=question_id)
    question_data = model_to_dict(question)
    question_data['choices'] = list(question.choices.values_list('text', flat=True))
    return JsonResponse({'success': True, 'question': question_data})




# الحذف 

@login_required
@user_passes_test(is_admin)
def delete_question(request, question_id):
    if request.method == 'POST':
        try:
            question = Question.objects.get(id=question_id)
            question.delete()
            return JsonResponse({'success': True, 'message': 'تم حذف السؤال بنجاح!'})
        except Question.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'السؤال غير موجود.'})
    return JsonResponse({'success': False, 'message': 'طلب غير صالح.'})

def question_report(request):
    if request.method == "GET":
        questions = Question.objects.all()
        return render(request, 'survey/question_report.html', {'questions': questions})
    
    if request.method == "POST":  # AJAX طلب
        question_id = request.POST.get('question_id')
        question = get_object_or_404(Question, id=question_id)
        answers = Answer.objects.filter(question=question).select_related('entity', 'choice_selected')

        # تجهيز البيانات لإرسالها كـ JSON
        data = {
            'question': question.text,
            'answers': [
                {
                    'answer': answer.choice_selected.text if answer.choice_selected else answer.answer_text or "لا توجد إجابة",
                    'entity': answer.entity.name,
                    'survey':answer.survey.name,
                    'note': answer.note or "-"
                }
                for answer in answers
            ]
        }
        return JsonResponse(data)


def answer_report(request):
    if request.method == "GET":
        # جلب الأسئلة من الأنواع المحددة فقط
        questions = Question.objects.filter(question_type__in=["yes_no", "multiple_choice", "radio"])
        return render(request, 'survey/answer_report.html', {'questions': questions})
    
    if request.method == "POST":  # عند اختيار إجابة معينة
        question_id = request.POST.get('question_id')
        answer_value = request.POST.get('answer_value')
        
        question = get_object_or_404(Question, id=question_id)

        # تصفية الإجابات بناءً على السؤال والإجابة
        if question.question_type == "yes_no":
            answers = Answer.objects.filter(question=question, answer_text=answer_value).select_related('entity')
        else:  # multiple_choice أو radio
            answers = Answer.objects.filter(question=question, choice_selected__text=answer_value).select_related('entity')

        # تجهيز البيانات لإرسالها
        data = {
            'entities': [
                {
                    'name': answer.entity.name,
                    'survey':answer.survey.name,
                    'note': answer.note or "-"
                }
                for answer in answers
            ]
        }
        return JsonResponse(data)

def get_choices(request, question_id):
    question = get_object_or_404(Question, id=question_id, question_type__in=["multiple_choice", "radio"])
    choices = Choice.objects.filter(question=question)

    return JsonResponse({
        'choices': [{'id': choice.id, 'text': choice.text} for choice in choices]
    })



def edit_survey(request, survey_id):
    # الحصول على الاستبيان
    survey = get_object_or_404(Surveys, id=survey_id)
    # جلب الإجابات المتعلقة بالاستبيان
    answers = Answer.objects.filter(survey=survey).select_related('question', 'choice_selected')
    
    notes = {answer.question.id: answer.note for answer in answers}  # جمع الملاحظات حسب السؤال

    # جلب الأسئلة النشطة التي تخص نفس الفئة الخاصة بالاستبيان
    questions = Question.objects.filter(category=survey.category, is_active=True)
    # الكيان الأول المرتبط بالاستبيان
    entity = survey.entities.first() 

    # عند إرسال النموذج (POST request)
    if request.method == 'POST':
        survey.name = request.POST.get('survey_title')
        survey.save()
        for question in questions:
            question_key = f"question_{question.id}"
            note_key = f"note_{question.id}"  # مفتاح الملاحظة

            # إذا كان السؤال من نوع نص
            if question.question_type == 'text':
                answer_text = request.POST.get(question_key, "")
                note_text = request.POST.get(note_key, "")  # جلب الملاحظة
                Answer.objects.update_or_create(
                    survey=survey,
                    question=question,
                    defaults={"answer_text": answer_text, "note": note_text},
                    entity=entity
                )

            # إذا كان السؤال من نوع نعم/لا
            elif question.question_type == 'yes_no':
                answer_text = request.POST.get(question_key, None)
                note_text = request.POST.get(note_key, "")  # جلب الملاحظة
                if answer_text:
                    Answer.objects.update_or_create(
                        survey=survey,
                        question=question,
                        defaults={"answer_text": answer_text, "note": note_text},
                        entity=entity
                    )

            # إذا كان السؤال متعدد الخيارات أو مجموعة خيارات
            elif question.question_type in ['multiple_choice', 'radio']:
                selected_choices = request.POST.getlist(question_key)
                Answer.objects.filter(survey=survey, question=question).delete()  # حذف الإجابات القديمة
                for choice_id in selected_choices:
                    choice = Choice.objects.get(id=choice_id)
                    note_text = request.POST.get(note_key, "")  # جلب الملاحظة
                    Answer.objects.create(
                        survey=survey,
                        question=question,
                        choice_selected=choice,
                        entity=entity,
                        note=note_text  # إضافة الملاحظة
                    )

        encoded_entity_id = encode_id(entity.id)

        # إعادة توجيه المستخدم بعد الحفظ
        return redirect('categories', pk=encoded_entity_id)

    return render(request, 'survey/edit_survey.html', {
        'survey': survey,
        'questions': questions,
        'answers': answers,
        'notes': notes,  
    })




def entity_list(request):
    entities = Entitys.objects.all()
    # parents = Entitys.objects.filter(parent) 
    parents = Entitys.objects.filter(parent__isnull=True) # اختيار الكيانات التي يمكن أن تكون "أب"
    return render(request, 'survey/entities_list.html', {'entities': entities, 'parents': parents})

@csrf_exempt
def update_entity(request, entity_id):
    if request.method == "POST":
        entity = get_object_or_404(Entitys, id=entity_id)

        # تحديث الحقول
        entity.name = request.POST.get('name', entity.name)
        entity.description = request.POST.get('description', entity.description)
        
        # تحديث parent (قد يكون None إذا لم يُحدد)
        parent_id = request.POST.get('parent')
        if parent_id:
            parent_entity = get_object_or_404(Entitys, id=parent_id)
            entity.parent = parent_entity
        else:
            entity.parent = None

        entity.save()
        return JsonResponse({'success': True, 'message': 'تم تحديث الكيان بنجاح!'})
    return JsonResponse({'success': False, 'message': 'طلب غير صالح'})


@csrf_exempt
def delete_entity(request, entity_id):
    if request.method == "POST":
        entity = get_object_or_404(Entitys, id=entity_id)
        entity.delete()
        return JsonResponse({'success': True, 'message': 'تم حذف الكيان بنجاح!'})
    return JsonResponse({'success': False, 'message': 'طلب غير صالح'})  














# =---------------------------------------------------------------------------------------------


@login_required
@user_passes_test(is_admin)
def get_questions(request):
    return render(request, 'survey/question_category.html')


@login_required
@user_passes_test(lambda u: u.is_staff)
def survey_list(request):
    surveys = Surveys.objects.all()
    return render(request, 'survey/survey_list.html', {'surveys': surveys})

def thank_you(request):
    return render(request, 'survey/thank_you.html')

@login_required
@user_passes_test(is_admin)
def view_survey_answers(request, survey_id):
    survey = get_object_or_404(Surveys, id=survey_id)
    entity_responses = SurveyEntityResponse.objects.filter(survey=survey)
    entity_answers = {}

    for response in entity_responses:
        entity_id = response.entity.id
        if entity_id not in entity_answers:
            entity_answers[entity_id] = {
                'entity': response.entity,
                'answers': response.answers,
                'sectors': {}
            }
        if response.sector:
            entity_answers[entity_id]['sectors'][response.sector.id] = {
                'sector': response.sector,
                'answers': response.answers
            }

    if request.method == 'POST':
        # Save the answers
        for entity_id, entity_data in entity_answers.items():
            entity_answers_data = {}
            for question in survey.questions.all():
                answer_key = f"entity_{entity_id}_question_{question.id}"
                text_answer = request.POST.get(answer_key, "")
                entity_answers_data[question.text] = {'text_answer': text_answer}
            SurveyEntityResponse.objects.update_or_create(
                survey=survey,
                entity=entity_data['entity'],
                sector=None,
                user=request.user,
                defaults={'answers': entity_answers_data}
            )

        # For sectors
        for entity_id, entity_data in entity_answers.items():
            for sector_id, sector_data in entity_data['sectors'].items():
                sector_answers_data = {}
                for question in survey.questions.all():
                    answer_key = f"sector_{sector_id}_question_{question.id}"
                    text_answer = request.POST.get(answer_key, "")
                    sector_answers_data[question.text] = {'text_answer': text_answer}
                SurveyEntityResponse.objects.update_or_create(
                    survey=survey,
                    entity=entity_data['entity'],
                    sector=sector_data['sector'],
                    user=request.user,
                    defaults={'answers': sector_answers_data}
                )

        messages.success(request, "Answers updated successfully.")
        return redirect('view_survey_answers', survey_id=survey.id)

    return render(request, 'survey/view_survey_answers.html', {
        'survey': survey,
        'entity_answers': entity_answers,
    })
@login_required
@user_passes_test(is_admin)
def choose_survey_for_answers(request):
    surveys = Surveys.objects.all()
    return render(request, 'survey/choose_survey_for_answers.html', {'surveys': surveys})



# @login_required
# @user_passes_test(is_admin)
# def survey_report(request, survey_id):
#     survey = get_object_or_404(Surveys, id=survey_id)
#     answers_data = survey.json_answers  # Get the JSON answers data

#     # Convert JSON answers to DataFrame for analysis
#     df = pd.DataFrame([answers_data])

#     # Generate basic summary statistics
#     report_data = {}
#     for question, responses in answers_data.items():
#         if 'choices' in responses:  # Multiple choice question
#             choices_df = pd.Series(responses['choices']).value_counts()
#             report_data[question] = choices_df.to_dict()
#         elif 'yes_no_answer' in responses:  # Yes/No question
#             report_data[question] = {
#                 'Yes': (responses['yes_no_answer'] == 'yes'),
#                 'No': (responses['yes_no_answer'] == 'no')
#             }
#         else:  # Text responses
#             report_data[question] = responses['text_answer']

#     # Pass data to the template
#     return render(request, 'survey/survey_report.html', {
#         'survey': survey,
#         'report_data': report_data
#     })

@login_required
@user_passes_test(is_admin)
def choose_survey_for_report(request):
    surveys = Surveys.objects.all()
    return render(request, 'survey/choose_survey_for_report.html', {'surveys': surveys})


# @login_required
# @user_passes_test(lambda u: u.is_staff)
# def delete_survey(request, survey_id):
#     survey = get_object_or_404(Surveys, id=survey_id)
#     survey.delete()
#     return redirect('survey_list')

@login_required
@user_passes_test(lambda u: u.is_staff)
def survey_report(request, survey_id=None):
    # Fetch all surveys to populate the dropdown
    surveys = Surveys.objects.all()

    # If a survey_id is provided, fetch that specific survey
    selected_survey = None
    if survey_id:
        selected_survey = get_object_or_404(Surveys, id=survey_id)

    return render(request, 'survey/survey_report.html', {
        'surveys': surveys,
        'selected_survey': selected_survey,
    })



# Utility function to check admin status
def is_admin(user):
    return user.is_authenticated and user.is_staff

# 1. Surveys Summary Report
@login_required
@user_passes_test(is_admin)
def survey_summary_report(request, survey_id):
    survey = get_object_or_404(Surveys, id=survey_id)
    response_data = survey.json_answers
    total_responses = len(response_data)
    question_types = Question.objects.filter(survey=survey).values('question_type').count()

    return render(request, 'survey/summary_report.html', {
        'survey': survey,
        'total_responses': total_responses,
        'question_types': question_types,
    })

# 2. Question-Level Analysis
@login_required
@user_passes_test(is_admin)
def question_analysis_report(request, survey_id):
    survey = get_object_or_404(Surveys, id=survey_id)
    questions = survey.questions.all()
    
    # Assuming survey.json_answers is structured correctly as a dictionary with questions as keys
    answers_by_question = {
        question.text: survey.json_answers.get(question.text, "لا توجد إجابات") 
        for question in questions
    }

    return render(request, 'survey/question_analysis_report.html', {
        'survey': survey,
        'questions': questions,
        'answers_by_question': answers_by_question,
    })

# 3. Demographic Breakdown
@login_required
@user_passes_test(is_admin)
def demographic_report(request, survey_id):
    survey = get_object_or_404(Surveys, id=survey_id)
    response_data = pd.DataFrame(survey.json_answers)
    age_breakdown = response_data['age'].value_counts().to_dict() if 'age' in response_data.columns else {}

    return render(request, 'survey/demographic_report.html', {
        'survey': survey,
        'age_breakdown': age_breakdown,
    })

# 4. Trends Over Time
@login_required
@user_passes_test(is_admin)
def time_trend_report(request, survey_id):
    survey = get_object_or_404(Surveys, id=survey_id)
    response_data = pd.DataFrame(survey.json_answers)
    
    if 'response_date' in response_data.columns:
        response_data['response_date'] = pd.to_datetime(response_data['response_date'])
        trend_over_time = response_data.groupby(response_data['response_date'].dt.date).size().to_dict()
    else:
        trend_over_time = {}

    return render(request, 'survey/time_trend_report.html', {
        'survey': survey,
        'trend_over_time': trend_over_time,
    })

# 5. Completion Analysis

@login_required
@user_passes_test(is_admin)
def completion_analysis(request, survey_id):
    survey = get_object_or_404(Surveys, id=survey_id)
    
    # Access the JSON data for this survey's answers
    response_data = survey.json_answers

    # Define total_responses as the number of answered questions (non-empty responses)
    total_responses = sum(1 for answer in response_data.values() if any(answer.values()))

    # Assume a response is complete if all required questions have non-empty answers
    questions = survey.questions.all()
    completed_responses = 1 if all(response_data.get(q.text) for q in questions) else 0

    # Calculate completion rate
    completion_rate = (completed_responses / len(questions)) * 100 if questions else 0

    return render(request, 'survey/completion_analysis.html', {
        'survey': survey,
        'total_responses': total_responses,  # This now represents answered questions
        'completion_rate': completion_rate,
    })


# 6. Satisfaction and Feedback Analysis
@login_required
@user_passes_test(is_admin)
def satisfaction_report(request, survey_id):
    survey = get_object_or_404(Surveys, id=survey_id)
    response_data = survey.json_answers
    satisfaction_scores = [resp['satisfaction'] for resp in response_data if 'satisfaction' in resp]
    avg_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores) if satisfaction_scores else 0

    return render(request, 'survey/satisfaction_report.html', {
        'survey': survey,
        'avg_satisfaction': avg_satisfaction,
    })

# 7. Export Responses as CSV
@login_required
@user_passes_test(lambda u: u.is_staff)
def export_survey_data(request, survey_id):
    survey = get_object_or_404(Surveys, id=survey_id)
    response_data = survey.json_answers

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{survey.title}_responses.csv"'
    writer = csv.writer(response)

    # Check if json_answers is a dictionary with question-answer pairs
    if isinstance(response_data, dict):
        # Write header
        writer.writerow(['Question', 'Answer'])

        # Write question-answer pairs
        for question, answer in response_data.items():
            if isinstance(answer, dict):
                # Handle different answer types within the dictionary
                if 'choices' in answer:
                    writer.writerow([question, ', '.join(answer['choices'])])
                elif 'text_answer' in answer:
                    writer.writerow([question, answer['text_answer']])
                elif 'yes_no_answer' in answer:
                    writer.writerow([question, answer['yes_no_answer']])
            else:
                writer.writerow([question, answer])
    else:
        # Handle cases where response_data is not in the expected format
        writer.writerow(['Error'])
        writer.writerow(['Unexpected data format in json_answers'])

    return response


@login_required
@user_passes_test(lambda u: u.is_staff)
def dynamic_report(request):
    surveys = Surveys.objects.all()
    keyword = None
    report_data = []  # Store question-by-question analysis here

    # Process the filter form
    if request.method == "GET":
        form = ReportFilterForm(request.GET)
        if form.is_valid():
            keyword = form.cleaned_data['keyword'].lower()

    # Iterate through surveys to analyze answers
    for survey in surveys:
        for question, answer_data in survey.json_answers.items():
            # Filter questions based on the keyword
            if keyword and keyword not in question.lower():
                continue

            question_analysis = {
                'question_text': question,
                'question_type': None,
                'yes_count': 0,
                'no_count': 0,
                'most_common_choices': [],
                'choices_usage': {},
                'text_responses': []
            }

            # Determine the type of question and process responses
            for question_obj in survey.questions.filter(text=question):
                question_analysis['question_type'] = question_obj.question_type

                if question_obj.question_type == 'yes_no':
                    if answer_data.get("yes_no_answer") == "yes":
                        question_analysis['yes_count'] += 1
                    elif answer_data.get("yes_no_answer") == "no":
                        question_analysis['no_count'] += 1

                elif question_obj.question_type == 'multiple_choice' and 'choices' in answer_data:
                    choices_counter = Counter(answer_data['choices'])
                    question_analysis['choices_usage'] = dict(choices_counter)  # Ensure choices_usage is always a dictionary
                    question_analysis['most_common_choices'] = choices_counter.most_common()

                elif question_obj.question_type == 'text' and 'text_answer' in answer_data:
                    question_analysis['text_responses'].append(answer_data['text_answer'])

            report_data.append(question_analysis)

    context = {
        'form': form,
        'surveys': surveys,
        'keyword': keyword,
        'report_data': report_data,
    }

    return render(request, 'survey/dynamic_report.html', context)



@login_required
def survey_summary(request, survey_id):
    survey = get_object_or_404(Surveys, id=survey_id)
    survey_response, created = SurveyResponse.objects.get_or_create(survey=survey, user=request.user)

    if request.method == 'POST':
        summary_form = SurveySummaryForm(request.POST, instance=survey_response)
        
        question_forms = [
            QuestionNoteForm(request.POST, prefix=str(q.id), instance=QuestionResponse.objects.get_or_create(response=survey_response, question=q)[0])
            for q in survey.questions.all()
        ]

        if summary_form.is_valid() and all(form.is_valid() for form in question_forms):
            summary_form.save()
            for form in question_forms:
                form.save()
            return redirect('survey_list')  # Redirect to a survey list or confirmation page

    else:
        summary_form = SurveySummaryForm(instance=survey_response)
        question_forms = [
            QuestionNoteForm(prefix=str(q.id), instance=QuestionResponse.objects.get_or_create(response=survey_response, question=q)[0])
            for q in survey.questions.all()
        ]

    context = {
        'survey': survey,
        'summary_form': summary_form,
        'question_forms': question_forms,
    }
    return render(request, 'survey/survey_summary.html', context)


# @login_required
# @user_passes_test(lambda u: u.is_staff)
# def create_entity(request):
#     if request.method == 'POST':
#         form = EntityForm(request.POST)
#         if form.is_valid():
#             entity = form.save()
#             # استجابة JSON عند النجاح
#             return JsonResponse({'success': True})
#         else:
#             # استجابة JSON عند وجود خطأ في النموذج
#             return JsonResponse({'success': False, 'errors': form.errors}, status=400)

#     else:
#         form = EntityForm()
#     return render(request, 'entity/create_entity.html', {'form': form})


# @login_required
# def entity_list(request):
#     entities = Entity.objects.all()  # Retrieve all entities
#     return render(request, 'entity/entity_list.html', {'entities': entities})  # Render a template for displaying entities




@login_required
@user_passes_test(lambda u: u.is_staff)
def create_sector(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # استلام البيانات من الطلب
        sector_name = request.POST.get('sector_name')
        entity_id = request.POST.get('entity_id')
        print(sector_name)
        print(entity_id)
        # التحقق من وجود الكيان
        try:
            entity = Entitys.objects.get(id=entity_id)
        except Entitys.DoesNotExist:
            return JsonResponse({'error': 'Entity not found'}, status=404)
        
        # إنشاء قطاع جديد
        sector = Entitys.objects.create(name=sector_name, parent=entity)
        
        # إرجاع الاستجابة بعد إنشاء القطاع بنجاح
        return JsonResponse({'success': True, 'sector_name': sector.name})
    
    # إذا لم يكن الطلب من نوع POST أو غير AJAX
    return JsonResponse({'error': 'Invalid request'}, status=400)





def get_sectors(request):
    entity_id = request.GET.get('entity_id')
    sectors = Sector.objects.filter(entity_id=entity_id).values('id', 'name')
    return JsonResponse({'sectors': list(sectors)})


@login_required
def home(request):
    user = request.user

    # Get child entities (where parent is not None) with permissions for the user
    child_permissions = Entitys.objects.filter(parent__isnull=False, user_permissions__user=user)

    # Get unique parent entities of the child entities
    parent_entities = Entitys.objects.filter(id__in=child_permissions.values_list('parent_id', flat=True))



    # Add encoded_id for each entity for secure URL encoding
    for entity in parent_entities:
        entity.encoded_id = encode_id(entity.id)  # Ensure the encode_id function is working correctly


    for entity in child_permissions:
        entity.encoded_id = encode_id(entity.id)

    context = {
        'parent_entities': parent_entities,  # Parents of children with permissions
        'child_permissions': child_permissions,  # Child entities with permissions
    }

    return render(request, 'home.html', context)

# @login_required
# def home(request):
#     user = request.user

#     # Get the entities where the parent is None (top-level entities)
#     entities_permissions = Entitys.objects.filter(parent=None, user_permissions__user=user)
#     # Get the child entities (where parent is not None)
#     child_permissions = Entitys.objects.filter(parent__isnull=False, user_permissions__user=user)

#     # Add encoded_id for each entity for secure URL encoding
#     for entity in entities_permissions:
#         entity.encoded_id = encode_id(entity.id)  # Ensure this function is working correctly

#     for entity in child_permissions:
#         entity.encoded_id = encode_id(entity.id)  # Ensure this function is working correctly

#     context = {
#         'entities': entities_permissions,  # Top-level entities (parents)
#         'child_permissions': child_permissions,  # Child entities (sectors)
#     }

#     return render(request, 'home.html', context)






@login_required
@user_passes_test(lambda u: u.is_staff)
def update_survey_answers(request, survey_id):
    survey = get_object_or_404(Surveys, id=survey_id)

    if request.method == 'POST':
        answers_data = request.POST.getlist('answers')
        notes_data = request.POST.getlist('notes')

        for response in SurveyEntityResponse.objects.filter(survey=survey):
            entity_answers = answers_data.get(str(response.entity.id), {})
            response.answers.update(entity_answers)
            response.save()

        messages.success(request, "تم تحديث الإجابات بنجاح.")
        return redirect('view_survey_answers', survey_id=survey_id)

    return redirect('view_survey_answers', survey_id=survey_id)

    
