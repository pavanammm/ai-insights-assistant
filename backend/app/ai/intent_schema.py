from pydantic import BaseModel, model_validator
from typing import Optional, Dict, Any


class DateRange(BaseModel):
    start: Optional[str] = None
    end: Optional[str] = None


class IntentModel(BaseModel):
    metric: str
    group_by: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    date_range: Optional[DateRange] = None
    comparison: Optional[str] = None
    top_n: Optional[int] = None

    @model_validator(mode="after")
    def coerce_empty_filters(self) -> "IntentModel":
        if self.filters == {}:
            self.filters = None
        return self