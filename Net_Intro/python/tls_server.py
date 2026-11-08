# HTTPS 서버 (실습 보조) - 자체 서명 인증서를 즉석에서 만들어 TLS 로 같은 센서 값을 제공한다
#   compose.yaml 의 tls 서비스로 자동 실행된다. 인터넷 없이도 HTTP 와 HTTPS 의 차이를 캡처로 비교하기 위한 서버.
import datetime
import http.server
import json
import os
import ssl
import tempfile

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID

PORT = 8443


def make_cert(directory):
    key = ec.generate_private_key(ec.SECP256R1())
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "tls")])
    now = datetime.datetime.now(datetime.timezone.utc)
    cert = (x509.CertificateBuilder()
            .subject_name(name).issuer_name(name)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(now - datetime.timedelta(minutes=1))
            .not_valid_after(now + datetime.timedelta(days=1))
            .add_extension(x509.SubjectAlternativeName([x509.DNSName("tls"), x509.DNSName("localhost")]), critical=False)
            .sign(key, hashes.SHA256()))
    cert_path, key_path = os.path.join(directory, "cert.pem"), os.path.join(directory, "key.pem")
    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    with open(key_path, "wb") as f:
        f.write(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.TraditionalOpenSSL,
                                  serialization.NoEncryption()))
    return cert_path, key_path


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps({"sensor": "temp-01", "value": 23.5, "unit": "C"}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print("[https]", self.address_string(), fmt % args, flush=True)


with tempfile.TemporaryDirectory() as d:
    cert, key = make_cert(d)
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(cert, key)
    server = http.server.ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    server.socket = ctx.wrap_socket(server.socket, server_side=True)
    print(f"HTTPS 서버 시작: 포트 {PORT} (TLS, 자체 서명 인증서)", flush=True)
    server.serve_forever()
