import pydantic


class GroupModel(pydantic.BaseModel):
    group: str
