from app import app
from extensions import celery
import tasks
from celery.schedules import crontab

# Ensure tasks have access to the database by wrapping them in the Flask app context
class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)

celery.Task = ContextTask


# CELERY BEAT SCHEDULE (CRON JOBS)

celery.conf.beat_schedule = {
    'send-daily-reminders-at-10am': {
        'task': 'tasks.daily_deadline_reminder',
        'schedule': crontab(hour=10, minute=0), # Runs daily at 10:00 AM
    },
    'send-monthly-report-on-1st': {
        'task': 'tasks.monthly_activity_report',
        'schedule': crontab(day_of_month='1', hour=8, minute=0), # Runs 1st day of every month at 8:00 AM
    }
}

# Timezone set karna zaroori hai India ke liye
celery.conf.timezone = 'Asia/Kolkata'