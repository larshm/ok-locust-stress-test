import base64
import codecs

expectedResultString = "QUwxMDAwOgABAgMEBQYH////////////////"

usernameBytes = bytes("AL1000:", "utf-8")
passwordBytes = bytes.fromhex("0001020304050607FFFFFFFFFFFFFFFFFFFFFFFF")

print(usernameBytes)
print(passwordBytes)

asd = usernameBytes + passwordBytes

print(asd)

authstring = base64.b64encode(asd).decode("utf-8")

print(authstring)

if expectedResultString == authstring:
    print("AWESOME!!!")