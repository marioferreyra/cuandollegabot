from ..modules.rosario import RosarioCuandoLlega


def test_getBusArray():
    r = RosarioCuandoLlega(None)
    assert len(r.getBusArray()) > 0


def test_getBusStopInfo():
    r = RosarioCuandoLlega(None)
    assert r.getBusStopInfo(134, 8424)
