from itsdangerous import URLSafeSerializer
from django.conf import settings


def encode_id(entity_id):
    serializer = URLSafeSerializer(settings.SECRET_KEY)
    return serializer.dumps(entity_id)  # تشفير المعرف

def decode_id(encoded_id):
    serializer = URLSafeSerializer(settings.SECRET_KEY)
    try:
        return serializer.loads(encoded_id)  # فك التشفير
    except Exception:
        return None
    



