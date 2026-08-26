class BadRequest(Exception):
    def __init__(self, id="", signature="", message="Bad Request"):
        self.id = id
        self.signature = signature
        self.message = message
        self.status_code = 400


class InvalidSignature(Exception):
    def __init__(self, signature="", message="Invalid Signature"):
        self.signature = signature
        self.message = message
        self.status_code = 401


class InternalServerError(Exception):
    def __init__(self, message="Internal Server Error"):
        self.message = message
        self.status_code = 500
