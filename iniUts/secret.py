import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes

# Retorna 32 bytes (SHA-256) da senha (usada como chave final)
def _derive_key_from_password(password: str) -> bytes:
    # Hash SHA-256 da senha -> chave de 32 bytes
    digest = hashes.Hash(hashes.SHA256())
    digest.update(password.encode('utf-8'))
    return digest.finalize()

# Encripta texto (str) com senha (str). Retorna string Base64 contendo: nonce + ciphertext + tag
def encrypt(text: str, password: str) -> str:
    """
    // text: texto em claro
    // password: senha/segredo que será transformado em hash (SHA-256) para usar como chave
    // retorna: base64(nonce || ciphertext || tag)
    """
    key = _derive_key_from_password(password)         # 32 bytes
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)                            # nonce/IV recomendado para GCM: 12 bytes
    plaintext = text.encode('utf-8')
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)  # dados adicionais (AAD) = None
    payload = nonce + ciphertext                      # armazenar nonce + ciphertext (ciphertext já inclui tag no AESGCM)
    return base64.b64encode(payload).decode('utf-8')

# Decripta string Base64 gerada por encrypt()
def decrypt(token_b64: str, password: str) -> str:
    """
    // token_b64: string retornada por encrypt (base64(nonce||ciphertext||tag))
    // password: mesma senha usada na encriptação
    // retorna: texto em claro (str) ou levanta exceção se inválido
    """
    key = _derive_key_from_password(password)
    data = base64.b64decode(token_b64)
    if len(data) < 12:
        raise ValueError("Payload inválido")
    nonce = data[:12]
    ciphertext = data[12:]
    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext.decode('utf-8')

# Exemplo de uso:
if __name__ == "__main__":
    senha = "minha-senha-secreta"
    texto = "mensagem ultra secreta"
    cifrado = encrypt(texto, senha)
    print("Cifrado:", cifrado)
    dec = decrypt(cifrado, senha)
    print("Decifrado:", dec)