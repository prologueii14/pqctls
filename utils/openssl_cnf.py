import os
import tempfile
from utils.settings import settings

_CNF_CACHE = None

def get_minimal_openssl_cnf() -> str:
    """回傳最小 openssl.cnf 路徑"""
    global _CNF_CACHE
    if _CNF_CACHE and os.path.exists(_CNF_CACHE):
        return _CNF_CACHE
    
    config = settings.openssl
    activate_oqs = config.get('activate_oqs_provider', True)
    
    lines = [
        "openssl_conf = openssl_init",
        "",
        "[openssl_init]",
        "providers = provider_sect",
        "",
        "[provider_sect]",
        "default = default_sect",
    ]
    
    if activate_oqs:
        lines.append("oqsprovider = oqs_sect")
    
    lines.extend([
        "",
        "[default_sect]",
        "activate = 1",
    ])
    
    if activate_oqs:
        lines.extend([
            "",
            "[oqs_sect]",
            "activate = 1",
        ])
    
    lines.extend([
        "",
        "[req]",
        "default_bits        = 2048",
        "distinguished_name  = dn",
        "x509_extensions     = v3_req",
        "prompt              = no",
        "",
        "[dn]",
        f"CN = {config['subject'].replace('/CN=', '')}",
        "",
        "[v3_req]",
        "basicConstraints = CA:FALSE",
        "keyUsage         = digitalSignature, keyEncipherment",
        "extendedKeyUsage = serverAuth",
    ])
    
    content = "\n".join(lines) + "\n"
    fd, path = tempfile.mkstemp(suffix=".cnf")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(content)
    _CNF_CACHE = path
    return path