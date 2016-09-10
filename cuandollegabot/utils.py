# -*- coding: UTF-8 -*-


def magic_decode(text, deco='utf-8-sig', enco='utf-8'):
    try:
        return text.decode(deco).encode()
    except UnicodeEncodeError:
        return text.encode(enco)
    except:
        return text
