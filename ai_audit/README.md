# AI Audit Application (ai_audit)

## Overview

The AI Audit application is a Django-based module that integrates AI models to automatically generate credit audit tests, helping to identify potential risks and exceptions.

### Core Features

1. **AI Test Generation**: Automatically generates audit test logic by analyzing existing data through GPT-5 API
2. **Exception Detection**: Detects exceptions in data based on test logic
3. **Exception Handling**: Provides exception status management and processing workflow
4. **User Feedback**: Collects user feedback on exceptions, especially false positives
5. **Test Logic Optimization**: Automatically updates test logic based on user feedback, generating new versions

## Technical Architecture

### Data Models

- **TestLogic**: Stores AI-generated test logic
- **Exception**: Stores test-generated exceptions
- **Feedback**: Stores user feedback

### Directory Structure

```
ai_audit/
├── templates/ai_audit/      # Frontend templates
├── __init__.py              # Application initialization
├── apps.py                  # Application configuration
├── models.py                # Data models
├── views.py                 # View logic
├── urls.py                  # URL configuration
├── api.py                   # API calls
├── utils.py                 # Utility functions
└── README.md                # Documentation
```

## Installation Steps

### 1. Copy the Application

Copy the `ai_audit` directory to the `version1.2-dev` directory of the company project.

### 2. Update Configuration

#### settings.py

Add the following configuration to `credit_continuous_dashboard/settings.py`:

```python
# Add to INSTALLED_APPS
INSTALLED_APPS = [
    # Existing apps
    'credit_app',
    'agreements',
    # New app
    'ai_audit',
]

# GPT-5 API configuration
GPT5_API_URL = 'https://api.example.com/gpt5'  # Replace with actual API address
GPT5_API_TOKEN = 'YOUR_API_TOKEN_HERE'  # Replace with actual Token
```

#### urls.py

Add the following configuration to the root `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    # Existing URLs
    path('credit/', include('credit_app.urls')),
    path('agreements/', include('agreements.urls')),
    # New URL
    path('ai-audit/', include('ai_audit.urls')),
]
```

### 3. Database Migration

Run in the venv1.2 environment on the company computer:

```bash
# Activate virtual environment
venv1.2\Scripts\activate

# Run migrations
python manage.py makemigrations ai_audit
python manage.py migrate ai_audit
```

### 4. Install Dependencies

Install required dependencies in the venv1.2 environment on the company computer:

```bash
# Activate virtual environment
venv1.2\Scripts\activate

# Install core dependencies
pip install requests python-dotenv

# Optional dependencies (as needed)
pip install djangorestframework
```

## Usage

### 1. Start the Application

```bash
# Activate virtual environment
venv1.2\Scripts\activate

# Start development server
python manage.py runserver
```

### 2. Access the Application

Access in browser: `http://localhost:8000/ai-audit/`

### 3. Main Features

- **Dashboard**: View all tests and unprocessed exceptions
- **Test Details**: View test logic and related exceptions
- **Exception Details**: Process exceptions and submit feedback
- **Generate Tests**: Trigger AI to generate new test logic

## Workflow

1. **Generate Tests**: Click the "Generate New Tests" button, AI will analyze existing data and generate test logic
2. **View Exceptions**: After tests run, view detected exceptions
3. **Process Exceptions**:
   - Recognized: Confirm the exception is valid
   - Investigate: Redirect to raw data for investigation
   - False Positive: Mark as false positive and submit feedback
4. **Optimize Tests**: AI automatically updates test logic based on feedback, generating new versions

## Notes

1. **API Configuration**:
   - Ensure GPT-5 API address and Token are correctly configured in `settings.py`
   - Recommend using environment variables to store sensitive information

2. **Security**:
   - Do not hardcode API Token in code
   - Ensure only authorized users can access AI audit functionality

3. **Performance**:
   - API calls may have latency, recommend implementing asynchronous processing
   - For large data volumes, consider batch processing

4. **Maintenance**:
   - Regularly review AI-generated test logic
   - Monitor API call frequency and costs

## Future Optimizations

1. **Vector Database Integration**: Add Pinecone or FAISS to improve similarity search efficiency
2. **User Authentication**: Integrate with company's existing user authentication system
3. **Automation**: Implement scheduled automatic test generation
4. **Reporting**: Add test coverage and exception statistics reports

## Troubleshooting

### Common Issues

1. **API Call Failure**:
   - Check if API URL and Token are correct
   - Ensure network connection is normal

2. **Database Migration Failure**:
   - Check if model definitions are correct
   - Ensure dependent models exist

3. **Page Loading Error**:
   - Check if template files exist
   - Ensure URL configuration is correct

### Log Viewing

```bash
# View Django logs
python manage.py runserver --verbosity 2
```

## Contact Information

For questions or suggestions, please contact the development team.
