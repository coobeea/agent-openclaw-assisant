#!/usr/bin/env python3
"""
凭证加密工具
"""

import sys
import click
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from shared.utils.crypto import CredentialEncryptor, mask_sensitive_value


@click.group()
def cli():
    """凭证加密工具"""
    pass


@cli.command()
@click.argument('plaintext')
def encrypt(plaintext):
    """加密文本"""
    encryptor = CredentialEncryptor()
    encrypted = encryptor.encrypt(plaintext)
    
    click.echo(f"原文: {mask_sensitive_value(plaintext)}")
    click.echo(f"密文: {encrypted}")


@cli.command()
@click.argument('encrypted_text')
def decrypt(encrypted_text):
    """解密文本"""
    encryptor = CredentialEncryptor()
    try:
        decrypted = encryptor.decrypt(encrypted_text)
        click.echo(f"明文: {decrypted}")
    except Exception as e:
        click.echo(f"解密失败: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()
