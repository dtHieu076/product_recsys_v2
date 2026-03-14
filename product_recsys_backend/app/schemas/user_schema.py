from pydantic import BaseModel
from app.models.user import User
from pydantic import BaseModel, ConfigDict

class UserOut(BaseModel):
    user_id: int
    username: str

    model_config = ConfigDict(from_attributes=True)

