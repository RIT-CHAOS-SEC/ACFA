import hmac
import hashlib

expected = b'\xb2\xd3\x02\x8f\x11\xa1\xe8\xcb\xe1\x1c\x9dJ{9\xe8\x1c)\x81f\x87r\xc9t\xf5 \xb8Q\xb3\xce\x8a\x0f\xa4'
prv_mac = b'hZ\x1c\xb0\xc1\x1a\x08I\xf2\xfe\xfd\xe2\xb5\xcd\xb4\xc2\xaaT\xe0\xee\x1d\x01\xd4\xcc\x0f\x12\x93\xe0=\xb1\xdf\xd4' 
prv_cflog = b'@\xe0\x00\xa0'
hmac_debug = b'b.\x0cV\xc8\x9f\xe4\x00i\x7f\x9d\xcb\xfe&S~\xd8\xc6f<_\xc6\xa2\xf4\xd6\x8f\x05\n\x97\xe5\x98"'

mac = hmac.new(hmac_debug, msg=prv_cflog, digestmod=hashlib.sha256).digest()
print(mac)
print(prv_mac)