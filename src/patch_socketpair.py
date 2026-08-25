import socket

_original_socketpair = socket.socketpair

def _safe_socketpair(family=socket.AF_UNIX, type=socket.SOCK_STREAM, proto=0):
    try:
        return _original_socketpair(family, type, proto)
    except Exception:
        lsock = socket.socket(socket.AF_INET, type, proto)
        lsock.bind(('127.0.0.1', 0))
        lsock.listen(1)
        port = lsock.getsockname()[1]
        csock = socket.socket(socket.AF_INET, type, proto)
        csock.connect(('127.0.0.1', port))
        ssock, _ = lsock.accept()
        lsock.close()
        return ssock, csock

socket.socketpair = _safe_socketpair
