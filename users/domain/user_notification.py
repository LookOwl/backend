
from dataclasses import dataclass
from enum import Enum

from loans.domain.loan_request import LoanRequestId
from users.domain.user_id import UserId

class NotificationType(Enum):
    INTEREST_TIME_EXPIRED = "INTEREST_TIME_EXPIRED"
    PICKUP_TIME_EXPIRED = "PICKUP_TIME_EXPIRED"
    REQ_ASSIGNED = "REQ_ASSIGNED"

@dataclass
class NotificationId:
    id : int

@dataclass
class UserNotification:
    notification_id : NotificationId
    user : UserId
    type : NotificationType
    loan_req_id : LoanRequestId