# AI 审计应用 (ai_audit)

## 功能说明

AI 审计应用是一个基于 Django 的模块，用于集成 AI 模型自动生成信贷审计测试，帮助识别潜在的风险和异常。

### 核心功能

1. **AI 测试生成**：通过 GPT-5 API 分析现有数据，自动生成审计测试逻辑
2. **异常检测**：基于测试逻辑检测数据中的异常
3. **异常处理**：提供异常状态管理和处理流程
4. **用户反馈**：收集用户对异常的反馈，特别是误报（False Positive）
5. **测试逻辑优化**：根据用户反馈自动更新测试逻辑，生成新的版本

## 技术架构

### 数据模型

- **TestLogic**：存储 AI 生成的测试逻辑
- **Exception**：存储测试产生的异常
- **Feedback**：存储用户反馈

### 目录结构

```
ai_audit/
├── templates/ai_audit/      # 前端模板
├── __init__.py              # 应用初始化
├── apps.py                  # 应用配置
├── models.py                # 数据模型
├── views.py                 # 视图逻辑
├── urls.py                  # URL 配置
├── api.py                   # API 调用
├── utils.py                 # 工具函数
└── README.md                # 说明文档
```

## 安装步骤

### 1. 复制应用

将 `ai_audit` 目录复制到公司项目的 `version1.2-dev` 目录中。

### 2. 更新配置

#### settings.py

在 `credit_continuous_dashboard/settings.py` 中添加以下配置：

```python
# 添加到 INSTALLED_APPS
INSTALLED_APPS = [
    # 现有应用
    'credit_app',
    'agreements',
    # 新应用
    'ai_audit',
]

# GPT-5 API 配置
GPT5_API_URL = 'https://api.example.com/gpt5'  # 替换为实际API地址
GPT5_API_TOKEN = 'YOUR_API_TOKEN_HERE'  # 替换为实际Token
```

#### urls.py

在根 `urls.py` 中添加以下配置：

```python
from django.urls import path, include

urlpatterns = [
    # 现有URL
    path('credit/', include('credit_app.urls')),
    path('agreements/', include('agreements.urls')),
    # 新URL
    path('ai-audit/', include('ai_audit.urls')),
]
```

### 3. 数据库迁移

在公司电脑的 venv1.2 环境中运行：

```bash
# 激活虚拟环境
venv1.2\Scripts\activate

# 运行迁移
python manage.py makemigrations ai_audit
python manage.py migrate ai_audit
```

### 4. 安装依赖

在公司电脑的 venv1.2 环境中安装所需依赖：

```bash
# 激活虚拟环境
venv1.2\Scripts\activate

# 安装核心依赖
pip install requests python-dotenv

# 可选依赖（根据需要）
pip install djangorestframework
```

## 使用方法

### 1. 启动应用

```bash
# 激活虚拟环境
venv1.2\Scripts\activate

# 启动开发服务器
python manage.py runserver
```

### 2. 访问应用

在浏览器中访问：`http://localhost:8000/ai-audit/`

### 3. 主要功能

- **仪表盘**：查看所有测试和未处理异常
- **测试详情**：查看测试逻辑和相关异常
- **异常详情**：处理异常，提交反馈
- **生成测试**：触发 AI 生成新的测试逻辑

## 工作流程

1. **生成测试**：点击 "生成新测试" 按钮，AI 会分析现有数据并生成测试逻辑
2. **查看异常**：测试运行后，查看检测到的异常
3. **处理异常**：
   - Recognized：确认异常有效
   - Investigate：跳转到原始数据进行调查
   - False Positive：标记为误报并提交反馈
4. **优化测试**：AI 根据反馈自动更新测试逻辑，生成新版本

## 注意事项

1. **API 配置**：
   - 请确保在 `settings.py` 中正确配置 GPT-5 API 地址和 Token
   - 建议使用环境变量存储敏感信息

2. **安全性**：
   - 不要在代码中硬编码 API Token
   - 确保只有授权用户可以访问 AI 审计功能

3. **性能**：
   - API 调用可能会有延迟，建议实现异步处理
   - 对于大量数据，考虑分批处理

4. **维护**：
   - 定期检查 AI 生成的测试逻辑
   - 监控 API 调用频率和费用

## 后续优化

1. **向量数据库集成**：添加 Pinecone 或 FAISS 以提高相似性搜索效率
2. **用户认证**：集成公司现有的用户认证系统
3. **自动化**：实现定期自动生成测试的功能
4. **报表功能**：添加测试覆盖率和异常统计报表

## 故障排除

### 常见问题

1. **API 调用失败**：
   - 检查 API URL 和 Token 是否正确
   - 确保网络连接正常

2. **数据库迁移失败**：
   - 检查模型定义是否正确
   - 确保依赖的模型存在

3. **页面加载错误**：
   - 检查模板文件是否存在
   - 确保 URL 配置正确

### 日志查看

```bash
# 查看 Django 日志
python manage.py runserver --verbosity 2
```

## 联系信息

如有问题或建议，请联系开发团队。
