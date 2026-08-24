from sqlalchemy.orm import Session


class VehicleCategoryService:
    def __init__(self, db: Session):
        self.db = db
