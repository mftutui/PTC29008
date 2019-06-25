
class Response():


    def __init__(self, type, tkllen, code, mid, token, payload):
        self.type = type
        self.tkllen = tkllen
        self.code = code
        self.mid = mid
        self.token = token
        self.payload = payload
    
    def getPayload(self):
        return self.payload
    
    def getCode(self):
        return self.code
    def getMid(self):
        return self.mid
    
    def getToken(self):
        return self.token
    def getType(self):
        return self.type