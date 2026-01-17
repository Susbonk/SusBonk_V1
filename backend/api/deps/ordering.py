from typing import Optional
from fastapi import Query

class Ordering:
    def __init__(
        self,
        order_by: Optional[str] = Query(None, description="Field to order by"),
        order_dir: Optional[str] = Query("asc", pattern="^(asc|desc)$", description="Order direction")
    ):
        self.order_by = order_by
        self.order_dir = order_dir
    
    def apply(self, query, model, default_field: str = "created_at"):
        field = self.order_by or default_field
        if not hasattr(model, field):
            field = default_field
        
        column = getattr(model, field)
        if self.order_dir == "desc":
            return query.order_by(column.desc())
        return query.order_by(column.asc())
