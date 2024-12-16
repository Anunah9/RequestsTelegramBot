from typing import Union


STATUSES = {
    1: "Created",
    2: "Sended",
    3: "Accepted",
    4: "In work",
    5: "Completed"
}


class Order:
    def __init__(self, text, department=None, status:int = 1):
        self.text: str = text
        self.department: Union[str, list] = department
        self.status: str = status
