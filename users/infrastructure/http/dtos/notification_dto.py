


from pydantic import BaseModel

from users.domain.user_notification import NotificationType


class NotificationDto(BaseModel):
    id : int
    loan_req_id : int
    notification_type : NotificationType