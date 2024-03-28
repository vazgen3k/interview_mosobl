from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from configuration import config
from src.file_manager import FileManager, FileSendler, FileZipper

router = APIRouter(prefix="/interview", tags=["interview"])


@router.get("/get_file/{uuid}")
async def get_file(
    uuid: UUID, creditionals: HTTPBasicCredentials = Depends(HTTPBasic())
):
    """
    Получение файла по UUID.
    
    Аутентифицирует пользователя с помощью HTTP Basic Auth и, если аутентификация прошла успешно,
    использует FileManager для получения файла по UUID.
    
    :param uuid: UUID файла для загрузки.
    :param credentials: Учетные данные пользователя, полученные через HTTP Basic Auth.
    :return: JSONResponse с информацией о файле или HTTPException в случае ошибки.
    """
    if (
        creditionals.username != config["auth_info"]["basic"]["username"]
        or creditionals.username != config["auth_info"]["basic"]["password"]
    ):

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    file_manager = FileManager(config)
    result = await file_manager.fetch_file_by_uuid(uuid)
    return result


@router.get("/download_zip")
async def download_zip(
    request: Request, creditionals: HTTPBasicCredentials = Depends(HTTPBasic())
):
    """
    Скачивание архива с файлами.
    
    Аутентифицирует пользователя и проверяет наличие куки "mojo". Если проверки пройдены,
    использует FileZipper для создания архива с файлами и FileSender для его отправки.
    
    :param request: Объект запроса FastAPI для доступа к кукам.
    :param credentials: Учетные данные пользователя, полученные через HTTP Basic Auth.
    :return: FileResponse с архивом или HTTPException в случае ошибки.
    """
    cookies = request.cookies

    if (
        creditionals.username != config["auth_info"]["zip_auth"]["username"]
        or creditionals.password != config["auth_info"]["zip_auth"]["password"]
        or cookies.get("mojo") != config["auth_info"]["zip_cookies"]["value"]
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )

    try:

        file_zipper = FileZipper(config)
        zip_path = await file_zipper.zip_files(
            temp_dir=config["files_info"]["temp_dir"]
        )
        responce = await FileSendler.send_zip_file(zip_path)
        return responce
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
