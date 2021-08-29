from typing import List, Optional

from pydantic import BaseModel


class PagedResponse(BaseModel):
    # NOTE: whether we should include total is debatable. If we include it,
    #   it's likely just an approximate number
    # approx_total: int

    # TODO: custom schema to make `data` and `error` mutually exclusive
    data: Optional[List[BaseModel]]
    cursor: Optional[str]
