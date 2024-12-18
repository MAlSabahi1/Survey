from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.urls import reverse
from .models import *
from .forms import *
from django.http import Http404, HttpResponse, HttpResponseForbidden, JsonResponse
from django.db.models import Q
from django.forms.models import model_to_dict
from django.views.decorators.csrf import csrf_exempt
from .utils import encode_id, decode_id
from django.views.decorators.cache import cache_control
import json
from django.db.models import Count, F, Q
from django.db.models.functions import TruncMonth
from django.contrib.contenttypes.models import ContentType




@login_required
@permission_required('survey.add_entitys', raise_exception=True)
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


@login_required
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

@login_required
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
@permission_required('survey.delete_surveys', raise_exception=True)
def delete_survey(request, survey_id, entity_id):
    # فك تشفير entity_id
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





@login_required
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

@login_required
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
@permission_required('survey.add_question', raise_exception=True)
def add_question(request):
    if request.method == 'POST':
        question_form = QuestionForm(request.POST)

        if question_form.is_valid():
            question = question_form.save(commit=False)

            # تحقق من وجود نص السؤال ونوعه
            if not question.text or not question.question_type:
                return JsonResponse({'success': False, 'message': 'يرجى التأكد من إدخال نص السؤال واختيار نوع السؤال.'})

            # حفظ السؤال
            question.save()

            # حفظ الاختيارات فقط إذا كان نوع السؤال "اختيار متعدد" أو "راديو"
            if question.question_type in ['multiple_choice', 'radio']:
                choices = request.POST.getlist('choices[]')
                for choice_text in choices:
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
@permission_required('survey.view_question', raise_exception=True)
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
        return render(request, 'survey/questions_list.html', {
            'questions': questions,
            })



# التعديل

@login_required
@permission_required('survey.change_question', raise_exception=True)
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
@permission_required('survey.delete_question', raise_exception=True)
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

@login_required
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


@login_required
def get_choices(request, question_id):
    question = get_object_or_404(Question, id=question_id, question_type__in=["multiple_choice", "radio"])
    choices = Choice.objects.filter(question=question)

    return JsonResponse({
        'choices': [{'id': choice.id, 'text': choice.text} for choice in choices]
    })


@login_required
@permission_required('survey.change_surveys', raise_exception=True)
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



@login_required
@permission_required('survey.view_entitys', raise_exception=True)
def entity_list(request):
    entities = Entitys.objects.all()
    # parents = Entitys.objects.filter(parent) 
    parents = Entitys.objects.filter(parent__isnull=True) # اختيار الكيانات التي يمكن أن تكون "أب"
    return render(request, 'survey/entities_list.html', {'entities': entities, 'parents': parents})


@login_required
@permission_required('survey.change_entitys', raise_exception=True)
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


@login_required
@permission_required('survey.delete_entitys', raise_exception=True)
@csrf_exempt
def delete_entity(request, entity_id):
    if request.method == "POST":
        entity = get_object_or_404(Entitys, id=entity_id)
        entity.delete()
        return JsonResponse({'success': True, 'message': 'تم حذف الكيان بنجاح!'})
    return JsonResponse({'success': False, 'message': 'طلب غير صالح'})  



@login_required
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


@login_required
def home(request):
    user = request.user

    # جميع الكيانات التي يمتلك المستخدم صلاحيات عليها
    permissions = Entitys.objects.filter(user_permissions__user=user)

    # الآباء الذين يمتلك المستخدم صلاحية مباشرة عليهم
    parent_entities = permissions.filter(parent=None)

    # الأطفال الذين يمتلك المستخدم صلاحية عليهم
    child_permissions = permissions.filter(parent__isnull=False)

    # الآباء الذين لديهم أطفال يمتلك المستخدم صلاحية عليهم
    parents_with_children_permissions = Entitys.objects.filter(
        id__in=child_permissions.values_list('parent_id', flat=True)
    )

    # دمج جميع الآباء في قائمة واحدة (الآباء بصلاحيات مباشرة + الآباء الذين لديهم أطفال بصلاحيات)
    all_parents = parent_entities.union(parents_with_children_permissions)

    # إضافة encoded_id
    for entity in permissions:
        entity.encoded_id = encode_id(entity.id)

    for entity in child_permissions:
        entity.encoded_id = encode_id(entity.id)

    context = {
        'parent_entities': all_parents,  # جميع الآباء الذين يجب أن تظهر الكروت الخاصة بهم
        'child_permissions': child_permissions,  # الأطفال مع صلاحيات
        'permissions': permissions,
    }

    return render(request, 'home.html', context)




def dashboard(request):
    # الإحصائيات الأساسية
    total_entities = Entitys.objects.count()
    total_surveys = Surveys.objects.count()
    total_questions = Question.objects.count()
    total_answers = Answer.objects.count()



    # إحصائيات المستخدمين
    users = User.objects.all()
    users_labels = [user.username for user in users]
    users_data = [1 for _ in users]  # نستخدم 1 كقيمة ثابتة لكل مستخدم لتمثيل كل واحد في الرسم البياني


    # إحصائيات عدد الاستبيانات التي أنشأها كل مستخدم
    surveys_by_user = (
        Surveys.objects.values('user__username')  # استخدمنا user__username للوصول إلى اسم المستخدم
        .annotate(count=Count('id'))  # عدد الاستبيانات التي أنشأها كل مستخدم
        .order_by('-count')
    )

    surveys_by_user_labels = [item['user__username'] for item in surveys_by_user]
    surveys_by_user_data = [item['count'] for item in surveys_by_user]


    # إحصائيات الاستبيانات حسب الفئات
    surveys_by_category = (
        Surveys.objects.values('category')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    # تحويل الفئات إلى الأسماء العربية
    CATEGORIES_DICT = {
        'staff': 'الكادر',
        'infrastructure': 'البنية التحتية',
        'systems': 'الأنظمة',
    }
    
    surveys_by_category_labels = [CATEGORIES_DICT.get(item['category'], item['category']) for item in surveys_by_category]
    surveys_by_category_data = [item['count'] for item in surveys_by_category]

    # إحصائيات الأسئلة حسب النوع
    questions_by_type = (
        Question.objects.values('question_type')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    # تحويل الأنواع إلى الأسماء العربية
    QUESTION_TYPES_DICT = {
        'text': 'نص',
        'yes_no': 'نعم/لا',
        'multiple_choice': 'اختيارات متعددة',
        'radio': 'اختيار واحد',
    }

    questions_by_type_labels = [QUESTION_TYPES_DICT.get(item['question_type'], item['question_type']) for item in questions_by_type]
    questions_by_type_data = [item['count'] for item in questions_by_type]

    # نسبة الإجابات المكتملة لكل استبيان
    surveys_with_completion_rate = []
    surveys = Surveys.objects.all()
    for survey in surveys:
        total_answerss = Answer.objects.filter(survey=survey).count()
        completion_rate = (
            (total_answerss / total_questions * 100) if total_questions > 0 else 0
        )
        surveys_with_completion_rate.append({
            'name': survey.name,
            'completion_rate': round(completion_rate, 2),
        })
    completion_rate_labels = [survey['name'] for survey in surveys_with_completion_rate]
    completion_rate_data = [survey['completion_rate'] for survey in surveys_with_completion_rate]

    # الكيانات المرتبطة بأكبر عدد من الاستبيانات
    entities_with_surveys = (
        Entitys.objects.annotate(survey_count=Count('surveys'))
        .order_by('-survey_count')[:5]
    )
    entities_with_surveys_labels = [entity.name for entity in entities_with_surveys]
    entities_with_surveys_data = [entity.survey_count for entity in entities_with_surveys]

    # عدد الاستبيانات التي تم إنشاؤها لكل شهر
    surveys_by_month = (
        Surveys.objects.annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    surveys_by_month_labels = [item['month'].strftime('%B') for item in surveys_by_month]
    surveys_by_month_data = [item['count'] for item in surveys_by_month]

    # أكثر الكيانات مشاركة بالإجابات
    top_entities_by_answers = (
        Entitys.objects.annotate(answer_count=Count('entity'))
        .order_by('-answer_count')[:5]
    )
    top_entities_labels = [entity.name for entity in top_entities_by_answers]
    top_entities_data = [entity.answer_count for entity in top_entities_by_answers]

    # إرسال البيانات إلى القالب
    context = {
        'total_entities': total_entities,
        'total_surveys': total_surveys,
        'total_questions': total_questions,
        'total_answers': total_answers,
        'surveys_by_category_labels': json.dumps(surveys_by_category_labels),
        'surveys_by_category_data': json.dumps(surveys_by_category_data),
        'questions_by_type_labels': json.dumps(questions_by_type_labels),
        'questions_by_type_data': json.dumps(questions_by_type_data),
        'completion_rate_labels': json.dumps(completion_rate_labels),
        'completion_rate_data': json.dumps(completion_rate_data),
        'entities_with_surveys_labels': json.dumps(entities_with_surveys_labels),
        'entities_with_surveys_data': json.dumps(entities_with_surveys_data),
        'surveys_by_month_labels': json.dumps(surveys_by_month_labels),
        'surveys_by_month_data': json.dumps(surveys_by_month_data),
        'top_entities_labels': json.dumps(top_entities_labels),
        'top_entities_data': json.dumps(top_entities_data),
        'surveys_by_user_labels': json.dumps(surveys_by_user_labels),
        'surveys_by_user_data': json.dumps(surveys_by_user_data),
        'users_labels': json.dumps(users_labels),
        'users_data': json.dumps(users_data),
        'total_users': len(users),
    }

    return render(request, 'survey/dashboard.html', context)


# # في ملف views.py
# from django.shortcuts import render, get_object_or_404
# from .models import Answer, Question  # تأكد من أن الـ models متاحة

# def print_answer_report(request, question_id, answer_value):
#     # جلب السؤال بناءً على الـ question_id
#     question = get_object_or_404(Question, id=question_id)

#     # جلب الإجابات التي تطابق الـ question_id و answer_value
#     answers = Answer.objects.filter(question=question, answer_text=answer_value)

#     # تمرير البيانات إلى القالب
#     context = {
#         'question': question,
#         'answers': answers,
#         'report_date': '2024-12-14',  # يمكنك استخدام التاريخ الفعلي أو توليده حسب الحاجة
#         'logo1_url': '/path/to/logo1.png',
#         'logo2_url': '/path/to/logo2.png',
#     }

#     return render(request, 'survey/report_print.html', context)
