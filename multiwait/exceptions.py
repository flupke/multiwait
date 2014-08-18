class MultiWaitError(Exception): pass
class Timeout(MultiWaitError): pass
class NameConflict(MultiWaitError): pass
