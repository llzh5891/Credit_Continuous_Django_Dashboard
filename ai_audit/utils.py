from django.db.models import Model
from credit_app.models import Customer, CreditApplication, Facility
from agreements.models import AgreementPDF


def get_entity_by_id(entity_type, entity_id):
    """
    根据实体类型和ID获取实体
    """
    entity_map = {
        'Customer': Customer,
        'CreditApplication': CreditApplication,
        'Facility': Facility,
        'AgreementPDF': AgreementPDF
    }
    
    model = entity_map.get(entity_type)
    if not model:
        return None
    
    try:
        # 尝试通过不同字段查找
        if entity_type == 'Customer':
            return model.objects.filter(customer_id=entity_id).first()
        elif entity_type == 'CreditApplication':
            return model.objects.filter(relationship_id=entity_id).first()
        elif entity_type == 'Facility':
            return model.objects.filter(facility_id=entity_id).first()
        elif entity_type == 'AgreementPDF':
            return model.objects.filter(id=entity_id).first()
    except Exception:
        return None
    
    return None


def get_entity_data(entity):
    """
    获取实体数据
    """
    if not entity:
        return {}
    
    data = {}
    for field in entity._meta.fields:
        try:
            value = getattr(entity, field.name)
            if isinstance(value, Model):
                data[field.name] = str(value)
            else:
                data[field.name] = value
        except:
            pass
    
    return data


def generate_test_id():
    """
    生成测试ID
    """
    import uuid
    return uuid.uuid4()


def get_next_version(test_id):
    """
    获取下一个版本号
    """
    from .models import TestLogic
    max_version = TestLogic.objects.filter(test_id=test_id).aggregate(
        max_version=models.Max('test_version')
    )['max_version']
    return (max_version or 0) + 1
