from typing import List, Literal, get_args

from pydantic import BaseModel, conint

CATEGORY_NAMES = Literal["apple", "banana"]
CATEGORY_NAMES_LIST = get_args(CATEGORY_NAMES)


class COCOCategory(BaseModel):
    id: conint(ge=0, le=len(CATEGORY_NAMES_LIST))
    name: CATEGORY_NAMES
    supercategory: str = "object"


class COCOImage(BaseModel):
    id: int
    width: int
    height: int
    file_name: str
    category_id: conint(ge=0, le=len(CATEGORY_NAMES_LIST))


class COCOClassificationDataset(BaseModel):
    images: List[COCOImage]
    categories: List[COCOCategory]
