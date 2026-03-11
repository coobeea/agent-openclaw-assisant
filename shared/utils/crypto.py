"""
加密工具
提供敏感信息的加密和解密功能
"""

import os
import base64
from pathlib import Path
from typing import Optional
from cryptography.fernet import Fernet


class CredentialEncryptor:
    """凭证加密器"""
    
    def __init__(self, keyfile_path: Optional[Path] = None):
        """
        初始化加密器
        
        Args:
            keyfile_path: 密钥文件路径，如果不存在会自动生成
        """
        if keyfile_path is None:
            keyfile_path = Path("./workspace/.keyfile")
        
        self.keyfile_path = keyfile_path
        self._ensure_keyfile()
        self.fernet = Fernet(self._load_key())
    
    def _ensure_keyfile(self) -> None:
        """确保密钥文件存在"""
        if not self.keyfile_path.exists():
            self._generate_keyfile()
    
    def _generate_keyfile(self) -> None:
        """生成新的密钥文件"""
        self.keyfile_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 生成密钥
        key = Fernet.generate_key()
        
        # 写入文件，设置严格的权限
        self.keyfile_path.write_bytes(key)
        
        # 设置文件权限为只有所有者可读写（Unix系统）
        if os.name != 'nt':  # 非 Windows
            os.chmod(self.keyfile_path, 0o600)
        
        print(f"✅ 已生成密钥文件: {self.keyfile_path}")
    
    def _load_key(self) -> bytes:
        """加载密钥"""
        return self.keyfile_path.read_bytes()
    
    def encrypt(self, plaintext: str) -> str:
        """
        加密文本
        
        Args:
            plaintext: 明文
        
        Returns:
            加密后的 base64 字符串
        """
        encrypted = self.fernet.encrypt(plaintext.encode('utf-8'))
        return base64.urlsafe_b64encode(encrypted).decode('utf-8')
    
    def decrypt(self, encrypted_text: str) -> str:
        """
        解密文本
        
        Args:
            encrypted_text: 加密的 base64 字符串
        
        Returns:
            明文
        """
        encrypted = base64.urlsafe_b64decode(encrypted_text.encode('utf-8'))
        decrypted = self.fernet.decrypt(encrypted)
        return decrypted.decode('utf-8')
    
    def encrypt_dict(self, data: dict, keys_to_encrypt: list[str]) -> dict:
        """
        加密字典中的指定键
        
        Args:
            data: 原始数据字典
            keys_to_encrypt: 需要加密的键列表
        
        Returns:
            加密后的字典
        """
        result = data.copy()
        for key in keys_to_encrypt:
            if key in result:
                result[key] = self.encrypt(str(result[key]))
                result[f"{key}_encrypted"] = True
        return result
    
    def decrypt_dict(self, data: dict, keys_to_decrypt: list[str]) -> dict:
        """
        解密字典中的指定键
        
        Args:
            data: 加密的数据字典
            keys_to_decrypt: 需要解密的键列表
        
        Returns:
            解密后的字典
        """
        result = data.copy()
        for key in keys_to_decrypt:
            if key in result and result.get(f"{key}_encrypted"):
                result[key] = self.decrypt(result[key])
                del result[f"{key}_encrypted"]
        return result


def generate_password(length: int = 32) -> str:
    """
    生成随机密码
    
    Args:
        length: 密码长度
    
    Returns:
        随机密码字符串
    """
    import secrets
    import string
    
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password


def mask_sensitive_value(value: str, show_chars: int = 4) -> str:
    """
    遮罩敏感值，只显示部分字符
    
    Args:
        value: 原始值
        show_chars: 显示的字符数
    
    Returns:
        遮罩后的字符串，如 "sk-...xyz123"
    """
    if len(value) <= show_chars * 2:
        return "*" * len(value)
    
    prefix = value[:show_chars]
    suffix = value[-show_chars:]
    return f"{prefix}...{suffix}"


if __name__ == "__main__":
    # 测试代码
    print("=== 加密工具测试 ===\n")
    
    # 创建加密器
    encryptor = CredentialEncryptor(Path("./test_keyfile"))
    
    # 测试加密和解密
    secret_text = "my-secret-api-key-12345"
    print(f"原文: {secret_text}")
    
    encrypted = encryptor.encrypt(secret_text)
    print(f"加密: {encrypted}")
    
    decrypted = encryptor.decrypt(encrypted)
    print(f"解密: {decrypted}")
    
    assert secret_text == decrypted, "加密解密失败！"
    print("✅ 加密解密测试通过\n")
    
    # 测试字典加密
    config = {
        "app_id": "cli_xxxxx",
        "app_secret": "secret_12345",
        "name": "feishu-channel"
    }
    
    print("原始配置:")
    print(config)
    
    encrypted_config = encryptor.encrypt_dict(config, ["app_secret"])
    print("\n加密后配置:")
    print(encrypted_config)
    
    decrypted_config = encryptor.decrypt_dict(encrypted_config, ["app_secret"])
    print("\n解密后配置:")
    print(decrypted_config)
    
    assert config == decrypted_config, "字典加密解密失败！"
    print("\n✅ 字典加密解密测试通过")
    
    # 测试密码生成
    password = generate_password(32)
    print(f"\n生成的随机密码: {password}")
    
    # 测试遮罩
    masked = mask_sensitive_value("sk-1234567890abcdef", 4)
    print(f"遮罩测试: {masked}")
    
    # 清理测试文件
    test_keyfile = Path("./test_keyfile")
    if test_keyfile.exists():
        test_keyfile.unlink()
        print("\n✅ 清理完成")
