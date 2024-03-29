from celery import Celery
from celery.schedules import crontab

from configuration import config

# Инициализация Celery приложения
celery_app = Celery(
    "tasks",
    broker=f"redis://{config['celery_info']['host']}:{config['celery_info']['port']}",
    backend=f"redis://{config['celery_info']['host']}:{config['celery_info']['port']}",
    include=["src.tasks.task"],
)

# Настройка расписания для периодических задач
celery_app.conf.beat_schedule = {
    # Определение задачи для ежечасной очистки временной папки
    "clean-temp-folder-every-hour": {
        "task": "src.tasks.task.clear_temp_folder",
        "schedule": crontab(minute=0),
    },
}
