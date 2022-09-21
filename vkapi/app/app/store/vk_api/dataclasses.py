from dataclasses import dataclass


# Базовые структуры, для выполнения задания их достаточно,
# поэтому постарайтесь не менять их пожалуйста из-за возможных проблем с тестами
@dataclass
class Message:
    user_id: int
    text: str
    user_not_registered: bool = False


@dataclass
class UpdateMessage:
    from_id: int
    text: str
    id: int
    payload: dict


@dataclass
class UpdateObject:
    message: UpdateMessage


@dataclass
class Update:
    type: str
    object: UpdateObject
