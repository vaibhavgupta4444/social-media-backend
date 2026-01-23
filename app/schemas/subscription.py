from pydantic import BaseModel, HttpUrl


class SubscriptionKeys(BaseModel):
    p256dh: str
    auth: str


class Subscription(BaseModel):
    endpoint: HttpUrl
    keys: SubscriptionKeys