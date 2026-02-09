from fastapi import Query


class PaginationParams:
    def __init__(
        self,
        page_number: int = Query(1, alias="page[number]", ge=1),
        page_size: int = Query(50, alias="page[size]", ge=1, le=100),
    ):
        self.page_number = page_number
        self.page_size = page_size
