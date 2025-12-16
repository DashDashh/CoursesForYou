from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import datetime
import ipaddress

# Генерация приватного ключа
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

# Создание самоподписанного сертификата
subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, u"RU"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Moscow"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, u"Moscow"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Test"),
    x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"), # Можно заменить на ваш IP, например u"217.66.159.161"
])

cert = x509.CertificateBuilder().subject_name(
    subject
).issuer_name(
    issuer
).public_key(
    private_key.public_key()
).serial_number(
    x509.random_serial_number()
).not_valid_before(
    datetime.datetime.utcnow()
).not_valid_after(
    datetime.datetime.utcnow() + datetime.timedelta(days=365)
).add_extension(
    x509.SubjectAlternativeName([x509.DNSName(u"localhost"),
                                 x509.IPAddress(ipaddress.IPv4Address('217.66.159.161')),  # ✅ Исправлено!
                                 ]),
    critical=False,
).sign(private_key, hashes.SHA256())

# Убедитесь, что папка ssl существует
import os
os.makedirs('./ssl', exist_ok=True)

# Сохранение ключа и сертификата
with open("./ssl/key.pem", "wb") as f:
    f.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ))

with open("./ssl/cert.pem", "wb") as f:
    f.write(cert.public_bytes(serialization.Encoding.PEM))

print("Сертификаты успешно созданы в папке ./ssl/")