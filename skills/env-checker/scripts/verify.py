"""
环境验证脚本 - 检查 Python 环境和所有依赖是否就绪
退出码: 0=全部通过  1=有失败项
"""
import sys
import importlib
import platform

REQUIRED_PACKAGES = {
    # 命令行工具
    "click":          "click",
    "rich":           "rich",
    # 进程管理
    "psutil":         "psutil",
    # 配置解析
    "pyyaml":         "yaml",
    "python-dotenv":  "dotenv",
    # 加密和安全
    "cryptography":   "cryptography",
    # HTTP/API客户端
    "requests":       "requests",
    "httpx":          "httpx",
    # AI模型API
    "openai":         "openai",
    "anthropic":      "anthropic",
    # 文档处理
    "python-docx":    "docx",
    "pdfplumber":     "pdfplumber",
    "openpyxl":       "openpyxl",
    # 日志管理
    "colorlog":       "colorlog",
}

MIN_PYTHON = (3, 12)


def check_python_version():
    ver = sys.version_info[:2]
    ok = ver >= MIN_PYTHON
    ver_str = f"{ver[0]}.{ver[1]}"
    target = f"{MIN_PYTHON[0]}.{MIN_PYTHON[1]}"
    return ok, ver_str, target


def check_package(pip_name, import_name):
    try:
        mod = importlib.import_module(import_name)
        version = getattr(mod, "__version__", getattr(mod, "VERSION", "unknown"))
        return True, str(version)
    except ImportError:
        return False, None


def main():
    print()
    print("=" * 52)
    print("  环境验证报告")
    print("=" * 52)
    print()

    ok_py, ver_str, target = check_python_version()
    status = "PASS" if ok_py else "FAIL"
    print(f"  Python 版本:   {ver_str}  (需要 >={target})  [{status}]")
    print(f"  Python 路径:   {sys.executable}")
    print(f"  操作系统:      {platform.system()} {platform.machine()}")
    print()

    print("  依赖库检查:")
    print("  " + "-" * 48)

    failures = []
    for pip_name, import_name in REQUIRED_PACKAGES.items():
        ok, version = check_package(pip_name, import_name)
        if ok:
            print(f"    {pip_name:<20s} {version:<15s} [PASS]")
        else:
            print(f"    {pip_name:<20s} {'未安装':<15s} [FAIL]")
            failures.append(pip_name)

    print()
    print("  " + "-" * 48)

    total = len(REQUIRED_PACKAGES)
    passed = total - len(failures)

    if not ok_py:
        failures.insert(0, f"Python >={target}")

    if not failures:
        print(f"  结果: 全部通过 ({passed}/{total} 库)")
        print()
        print("=" * 52)
        print("  环境就绪，可以运行所有 Skill")
        print("=" * 52)
        print()
        return 0
    else:
        print(f"  结果: {len(failures)} 项失败")
        print(f"  失败项: {', '.join(failures)}")
        print()
        print("=" * 52)
        print("  环境未就绪，请重新运行 setup 脚本")
        print("=" * 52)
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
