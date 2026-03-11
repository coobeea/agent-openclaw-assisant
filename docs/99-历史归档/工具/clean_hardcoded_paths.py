#!/usr/bin/env python3
"""
清理文档中的硬编码路径

将文档中的绝对路径替换为通用示例
"""
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 路径替换规则
REPLACEMENTS = {
    # 用户特定路径 → 通用示例
    r'/Users/lifeng/git/git-claw/agent-openclaw-assisant': '$PROJECT_ROOT',
    r'/Users/lifeng/git/git-claw/agent-openclaws': '/path/to/agent-openclaws',
    r'/Users/lifeng/git/git_agents/openclaw': '/path/to/openclaw',
    r'/Users/lifeng/Library/Application Support/openclaws': '$HOME/Library/Application Support/openclaws',
    r'/Users/lifeng': '$HOME',
}

def clean_file(file_path: Path):
    """清理单个文件中的硬编码路径"""
    try:
        content = file_path.read_text(encoding='utf-8')
        original = content
        
        # 应用所有替换规则
        for pattern, replacement in REPLACEMENTS.items():
            content = re.sub(pattern, replacement, content)
        
        # 只在有变化时写入
        if content != original:
            file_path.write_text(content, encoding='utf-8')
            return True
        return False
    except Exception as e:
        print(f"⚠️  处理失败 {file_path}: {e}")
        return False

def main():
    print("\n" + "=" * 80)
    print("清理文档中的硬编码路径")
    print("=" * 80)
    
    # 需要处理的目录
    docs_dirs = [
        PROJECT_ROOT / 'docs',
        PROJECT_ROOT,  # 根目录的 .md 文件
    ]
    
    total_files = 0
    cleaned_files = 0
    
    for docs_dir in docs_dirs:
        if not docs_dir.exists():
            continue
        
        # 查找所有 .md 文件
        if docs_dir.is_file():
            md_files = [docs_dir] if docs_dir.suffix == '.md' else []
        else:
            md_files = list(docs_dir.rglob('*.md'))
        
        for md_file in md_files:
            # 跳过知识库中引用 agent-openclaws 的文档（那些是有意的引用）
            if 'knowledge-base' in str(md_file):
                continue
            
            total_files += 1
            if clean_file(md_file):
                cleaned_files += 1
                print(f"✅ 已清理: {md_file.relative_to(PROJECT_ROOT)}")
    
    print("\n" + "=" * 80)
    print(f"📊 处理完成")
    print("=" * 80)
    print(f"总文件数: {total_files}")
    print(f"已清理: {cleaned_files}")
    print(f"未变化: {total_files - cleaned_files}")
    print("=" * 80 + "\n")

if __name__ == '__main__':
    main()
