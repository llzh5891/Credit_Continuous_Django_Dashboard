import uuid
from django.db import models
from django.utils import timezone
from credit_app.models import Customer, CreditApplication, Facility
from agreements.models import AgreementPDF


class TestLogic(models.Model):
    """
    AI 生成的测试逻辑模型
    """
    # 主键
    test_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    # 测试版本
    test_version = models.IntegerField(
        default=1,
        verbose_name='测试版本'
    )
    
    # 测试信息
    test_name = models.CharField(
        max_length=200,
        verbose_name='测试名称'
    )
    
    test_description = models.TextField(
        verbose_name='测试描述',
        null=True,
        blank=True
    )
    
    # 使用的列
    column_to_use = models.CharField(
        max_length=100,
        verbose_name='使用的列'
    )
    
    # 测试逻辑
    test_logic = models.TextField(
        verbose_name='测试逻辑'
    )
    
    # AI 理由
    ai_rationale = models.TextField(
        verbose_name='AI 理由',
        null=True,
        blank=True
    )
    
    # 发布日期
    test_logic_publish_date = models.DateTimeField(
        default=timezone.now,
        verbose_name='发布日期'
    )
    
    # 状态
    STATUS_CHOICES = [
        ('active', '活跃'),
        ('inactive', '非活跃'),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='状态'
    )
    
    # 模型版本
    model_version = models.CharField(
        max_length=50,
        verbose_name='模型版本',
        null=True,
        blank=True
    )
    
    # 元数据
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )
    
    class Meta:
        db_table = 'ai_audit_test_logic'
        verbose_name = '测试逻辑'
        verbose_name_plural = '测试逻辑'
        unique_together = ('test_id', 'test_version')
    
    def __str__(self):
        return f"{self.test_name} (v{self.test_version})"


class Exception(models.Model):
    """
    测试产生的异常模型
    """
    # 主键
    exception_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    # 关联测试
    test = models.ForeignKey(
        TestLogic,
        on_delete=models.CASCADE,
        related_name='exceptions',
        verbose_name='测试'
    )
    
    # 实体类型
    ENTITY_TYPE_CHOICES = [
        ('Customer', '客户'),
        ('CreditApplication', '信贷申请'),
        ('Facility', '授信额度'),
        ('AgreementPDF', '协议PDF'),
    ]
    
    entity_type = models.CharField(
        max_length=50,
        choices=ENTITY_TYPE_CHOICES,
        verbose_name='实体类型'
    )
    
    # 实体ID
    entity_id = models.CharField(
        max_length=100,
        verbose_name='实体ID'
    )
    
    # 异常详情
    exception_details = models.TextField(
        verbose_name='异常详情'
    )
    
    # 状态
    STATUS_CHOICES = [
        ('detected', '已检测'),
        ('reviewed', '已审核'),
        ('investigated', '已调查'),
        ('resolved', '已解决'),
        ('false_positive', '误报'),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='detected',
        verbose_name='状态'
    )
    
    # 元数据
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )
    
    class Meta:
        db_table = 'ai_audit_exception'
        verbose_name = '异常'
        verbose_name_plural = '异常'
    
    def __str__(self):
        return f"异常: {self.entity_type} - {self.entity_id}"


class Feedback(models.Model):
    """
    用户反馈模型
    """
    # 主键
    id = models.AutoField(
        primary_key=True
    )
    
    # 关联测试
    test = models.ForeignKey(
        TestLogic,
        on_delete=models.CASCADE,
        related_name='feedbacks',
        verbose_name='测试'
    )
    
    # 关联异常
    exception = models.ForeignKey(
        Exception,
        on_delete=models.CASCADE,
        related_name='feedbacks',
        verbose_name='异常'
    )
    
    # 用户信息
    user_id = models.CharField(
        max_length=100,
        verbose_name='用户ID'
    )
    
    # 反馈内容
    feedback_content = models.TextField(
        verbose_name='反馈内容'
    )
    
    # 反馈类型
    FEEDBACK_TYPE_CHOICES = [
        ('false_positive', '误报'),
        ('suggestion', '建议'),
        ('bug', '错误'),
    ]
    
    feedback_type = models.CharField(
        max_length=20,
        choices=FEEDBACK_TYPE_CHOICES,
        default='false_positive',
        verbose_name='反馈类型'
    )
    
    # 处理状态
    PROCESS_STATUS_CHOICES = [
        ('pending', '待处理'),
        ('processed', '已处理'),
    ]
    
    process_status = models.CharField(
        max_length=20,
        choices=PROCESS_STATUS_CHOICES,
        default='pending',
        verbose_name='处理状态'
    )
    
    # 反馈日期
    feedback_date = models.DateTimeField(
        default=timezone.now,
        verbose_name='反馈日期'
    )
    
    # 元数据
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )
    
    class Meta:
        db_table = 'ai_audit_feedback'
        verbose_name = '反馈'
        verbose_name_plural = '反馈'
    
    def __str__(self):
        return f"反馈: {self.user_id} - {self.feedback_type}"
