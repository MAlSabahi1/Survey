from django import template
from survey.utils import encode_id
register = template.Library()

@register.filter
def get_answer_text(answers, question_id):
    for answer in answers:
        if answer.question.id == question_id:
            return answer.answer_text
    return ""


@register.filter
def get_selected_choices(answers, question_id):
    """
    Retrieves the list of selected choice IDs for a specific question ID from the list of answers.
    """
    selected_choices = []
    for answer in answers:
        if answer.question.id == question_id and answer.choice_selected:
            selected_choices.append(answer.choice_selected.id)
    return selected_choices

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, "")

@register.filter
def dict_key(value, key):
    return value.get(key) if isinstance(value, dict) else None


@register.filter
def encode_id_filter(value):
    return encode_id(value)



@register.filter
def dictitems(value):
    """
    فلتر مخصص لإرجاع العناصر داخل القاموس (key-value pairs).
    """
    if isinstance(value, dict):
        return value.items()
    return None
