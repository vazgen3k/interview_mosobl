from uuid import UUID

from pydantic import BaseModel


class UUID4Model(BaseModel):
    uuid: UUID
