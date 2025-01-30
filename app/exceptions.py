from fastapi import HTTPException

class EntityNotFoundException(HTTPException):
    def __init__(self, entity_name: str):
        super().__init__(status_code=404, detail=f"{entity_name} not found")