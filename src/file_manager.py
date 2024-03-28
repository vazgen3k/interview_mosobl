import os
from datetime import datetime
from urllib.parse import unquote
from zipfile import ZipFile

import httpx
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from starlette.responses import FileResponse


class Manager:
    def __init__(self, config):
        """
        Базовый класс менеджера, инициализирующий конфигурацию.
        :param config: Словарь конфигурации приложения.
        """
        self.config = config


class FileManager(Manager):
    """
    Получение файла по UUID и его сохранение.
        
    Выполняет HTTP GET запрос к внешнему API для получения файла по UUID,
    сохраняет файл во временной директории и возвращает информацию о файле.
        
    :param uuid: UUID файла для загрузки.
    :return: JSONResponse с информацией о файле.
    """
    async def fetch_file_by_uuid(self, uuid: str):
        file_url = f"{self.config['files_info']['api_url']}?keys={uuid}"
        async with httpx.AsyncClient() as client:
            response = await client.get(
                file_url,
                auth=httpx.BasicAuth(
                    self.config["auth_info"]["basic"]["username"],
                    self.config["auth_info"]["basic"]["password"],
                ),
            )
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid UUID4"
                )

            filename = self._extract_filename(
                response.headers.get("Content-Disposition")
            )
            file_path = self._generate_file_path(filename)

            self._save_file(file_path, response.content)

            return JSONResponse(
                content={"status": "success", "filename": filename}, status_code=200
            )

    def _extract_filename(self, content_disposition: str):
        filename = content_disposition.split("filename=")[1]
        return str(unquote(filename)).replace('"', "")

    def _generate_file_path(self, filename: str):
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        unique_filename = f"{timestamp}_{filename}"
        return os.path.join(self.config["files_info"]["temp_dir"], unique_filename)

    def _save_file(self, file_path: str, content: bytes):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as file:
            file.write(content)


class FileZipper(Manager):

    async def zip_files(self, temp_dir, zip_filename="temp_files.zip"):
        zip_path = os.path.join(temp_dir, zip_filename)
        with ZipFile(zip_path, "w") as zipf:
            for root, dir, files in os.walk(temp_dir):
                for file in files:
                    if file != zip_filename:
                        zipf.write(os.path.join(root, file), arcname=file)

        return zip_path


class FileSendler:
    @staticmethod
    async def send_zip_file(zip_path, zip_filename="temp_files.zip"):
        return FileResponse(
            path=zip_path, filename=zip_filename, media_type="application/zip"
        )
