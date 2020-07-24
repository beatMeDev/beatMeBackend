# pylint: skip-file
"""
Base pydantic models
"""
from datetime import datetime
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from pydantic import BaseModel


item_type = Union[str, int, float, datetime]


class BaseResponse(BaseModel):
    data: Union[Dict[str, item_type], List[item_type]] = {}
    error: Optional[str] = None
    details: Optional[str] = None
