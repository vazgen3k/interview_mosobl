import os
import shutil

from src.tasks.celery_config import celery_app

# Определение задачи Celery для очистки временной папки
@celery_app.task
def clear_temp_folder():
    """
    Очистка временной папки.
    
    Перебирает все файлы и подпапки в папке './temp' и удаляет их. В случае возникновения
    исключений при удалении, выводит сообщение с указанием причины.
    """
    folder = "./temp"
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")
