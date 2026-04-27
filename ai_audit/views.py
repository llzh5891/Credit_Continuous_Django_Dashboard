from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import TestLogic, Exception, Feedback
from .api import get_api_instance
from .utils import get_entity_by_id, get_entity_data, get_next_version


def dashboard(request):
    """
    AI 审计仪表盘
    """
    tests = TestLogic.objects.order_by('-created_at')
    exceptions = Exception.objects.filter(status='detected').order_by('-created_at')[:10]
    
    context = {
        'tests': tests,
        'exceptions': exceptions
    }
    
    return render(request, 'ai_audit/dashboard.html', context)


def test_detail(request, test_id):
    """
    测试详情
    """
    test = get_object_or_404(TestLogic, test_id=test_id)
    exceptions = test.exceptions.all().order_by('-created_at')
    
    context = {
        'test': test,
        'exceptions': exceptions
    }
    
    return render(request, 'ai_audit/test_detail.html', context)


def exception_detail(request, exception_id):
    """
    异常详情
    """
    exception = get_object_or_404(Exception, exception_id=exception_id)
    entity = get_entity_by_id(exception.entity_type, exception.entity_id)
    entity_data = get_entity_data(entity)
    
    context = {
        'exception': exception,
        'entity': entity,
        'entity_data': entity_data
    }
    
    return render(request, 'ai_audit/exception_detail.html', context)

@csrf_exempt
def update_exception_status(request):
    """
    更新异常状态
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        exception_id = data.get('exception_id')
        status = data.get('status')
        
        try:
            exception = Exception.objects.get(exception_id=exception_id)
            exception.status = status
            exception.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def submit_feedback(request):
    """
    提交反馈
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        exception_id = data.get('exception_id')
        feedback_content = data.get('feedback_content')
        user_id = data.get('user_id', 'anonymous')
        
        try:
            exception = Exception.objects.get(exception_id=exception_id)
            
            # 创建反馈
            feedback = Feedback.objects.create(
                test=exception.test,
                exception=exception,
                user_id=user_id,
                feedback_content=feedback_content,
                feedback_type='false_positive'
            )
            
            # 更新异常状态
            exception.status = 'false_positive'
            exception.save()
            
            # 生成新版本测试逻辑
            api = get_api_instance()
            new_logic = api.update_test_logic(
                exception.test.test_logic,
                feedback_content
            )
            
            if new_logic:
                # 创建新版本测试
                next_version = get_next_version(exception.test.test_id)
                TestLogic.objects.create(
                    test_id=exception.test.test_id,
                    test_version=next_version,
                    test_name=exception.test.test_name,
                    test_description=exception.test.test_description,
                    column_to_use=exception.test.column_to_use,
                    test_logic=new_logic.get('content', ''),
                    ai_rationale=new_logic.get('rationale', ''),
                    model_version=exception.test.model_version
                )
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def generate_tests(request):
    """
    生成测试逻辑
    """
    # 这里可以添加生成测试的逻辑
    # 例如：从数据库获取数据，调用API生成测试
    
    return redirect('ai_audit:dashboard')
