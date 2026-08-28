from pydantic import BaseModel

# Token model
class Token(BaseModel):
    access_token: str
    token_type: str
    