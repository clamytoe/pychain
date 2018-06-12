import json
from datetime import datetime


class Transaction:
    def __init__(self, user_id, subject_id, desc, payload):
        self.trans_id = datetime.now().toordinal()
        self.user_id = user_id
        self.subject_id = subject_id
        self.desc = desc
        self.payload = payload

    @property
    def trans(self):
        return json.dumps(
            {
                "id": self.trans_id,
                "from": self.user_id,
                "to": self.subject_id,
                "desc": self.desc,
                "data": self.payload,
            }
        )

    @property
    def validate(self):
        trans = json.loads(self.trans)
        return (
            True
            if (
                trans["id"]
                and trans["from"]
                and trans["to"]
                and trans["desc"]
                and trans["data"]
            )
            else False
        )
