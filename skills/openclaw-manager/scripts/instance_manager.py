#!/usr/bin/env python3
"""
OpenClaw 实例管理器

基于成功的 e2e 测试经验，使用正确的 OpenClaw 命令。

功能：
- 创建新的 OpenClaw 实例（使用 openclaw setup）
- 启动实例（使用 openclaw gateway）
- 停止/重启实例
- 查看实例状态和日志
- 列出所有实例
- 删除实例
"""

import sys
import json
import subprocess
import argparse
import os
import time
import signal
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

from shared.configs.path_manager import PathManager, get_openclaw_cli, should_use_node_prefix

# 导入 openclaw_cli
scripts_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(scripts_dir))
from openclaw_cli import OpenClawCLI

# 兼容变量
OPENCLAW_CLI = get_openclaw_cli()
USE_NODE_PREFIX = should_use_node_prefix()


class InstanceManager:
    """实例管理器"""
    
    def __init__(self):
        self.pm = PathManager()
        self.cli = OpenClawCLI()
        
        # 确保必要目录存在
        self.pm.ensure_directories()
    
    def create(self, name: str, model: Optional[str] = None, port: Optional[int] = None) -> Dict[str, Any]:
        """
        创建新实例
        
        Args:
            name: 实例名称（如 openclaw-test-01）
            model: AI模型（如 bailian/qwen3.5-plus）
            port: 端口号（如 18800，None则自动分配）
        
        Returns:
            实例信息字典
        """
        print(f"\n{'=' * 80}")
        print(f"📦 创建实例: {name}")
        print(f"{'=' * 80}\n")
        
        # 1. 检查实例是否已存在
        if self._instance_exists(name):
            print(f"❌ 实例已存在: {name}")
            return None
        
        # 2. 分配端口
        if port is None:
            port = self._allocate_port()
        print(f"✅ 分配端口: {port}")
        
        # 3. 选择模型
        if model is None:
            model = self._auto_select_model()
        print(f"✅ 选择模型: {model}")
        
        # 4. 创建工作空间
        instance_path = self.pm.get_instance_path(name)
        instance_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ 创建工作空间: {instance_path}")
        
        # 5. 运行 openclaw setup
        print(f"\n⏳ 运行 openclaw setup...")
        try:
            result = self.cli.run(
                ['setup', f'--workspace={instance_path}'],
                state_dir=str(instance_path),
                config_file=str(instance_path / '.openclaw' / 'openclaw.json'),
                check=True
            )
            
            print(f"✅ setup 成功")
            if result.stdout and result.stdout.strip():
                # 只显示第一行
                first_line = result.stdout.strip().split('\n')[0]
                print(f"   {first_line}")
        except subprocess.CalledProcessError as e:
            print(f"❌ setup 失败（返回码: {e.returncode}）")
            if e.stderr:
                print(f"   {e.stderr.strip()}")
            return None
        except Exception as e:
            print(f"❌ setup 失败: {e}")
            return None
        
        # 6. 配置默认模型
        print(f"\n⏳ 配置默认模型: {model}")
        if not self._configure_model(instance_path, model):
            print(f"⚠️  模型配置失败，使用默认配置")
        
        # 6.5. 自动同步完整的模型配置（预防 "Unknown model" 问题）
        print(f"\n⏳ 同步模型配置...")
        if self._sync_models_config(instance_path):
            print(f"✅ 模型配置已同步")
        else:
            print(f"⚠️  模型配置同步失败，可能影响 AI 功能")
        
        # 7. 记录实例信息
        instance_info = {
            "name": name,
            "status": "stopped",
            "process_pid": None,
            "gateway_port": port,
            "workspace_path": str(instance_path),
            "model": model,
            "created_at": datetime.now().isoformat()
        }
        
        self._save_instance_info(instance_info)
        print(f"✅ 实例信息已记录")
        
        print(f"\n{'=' * 80}")
        print(f"🎉 实例创建成功！")
        print(f"{'=' * 80}")
        print(f"\n📋 实例信息:")
        print(f"   名称: {name}")
        print(f"   端口: {port}")
        print(f"   模型: {model}")
        print(f"   工作空间: {instance_path}")
        print(f"\n🎯 下一步:")
        print(f"   启动实例: python {__file__} start {name}")
        print(f"   查看状态: python {__file__} status {name}")
        
        return instance_info
    
    def start(self, name: str, background: bool = True) -> Optional[int]:
        """
        启动实例
        
        Args:
            name: 实例名称
            background: 是否后台运行
        
        Returns:
            进程 PID（如果成功）
        """
        print(f"\n{'=' * 80}")
        print(f"🚀 启动实例: {name}")
        print(f"{'=' * 80}\n")
        
        # 1. 检查实例是否存在
        instance_info = self._load_instance_info(name)
        if not instance_info:
            print(f"❌ 实例不存在: {name}")
            return None
        
        # 2. 检查是否已经运行
        if instance_info.get('status') == 'running':
            pid = instance_info.get('process_pid')
            if pid and self._is_process_alive(pid):
                print(f"⚠️  实例已经在运行中（PID: {pid}）")
                return pid
        
        # 3. 构建启动命令
        instance_path = Path(instance_info['workspace_path'])
        port = instance_info['gateway_port']
        
        cmd = []
        if USE_NODE_PREFIX:
            cmd.append('node')
        cmd.extend([
            str(OPENCLAW_CLI),
            'gateway',
            '--port', str(port)
        ])
        
        env = os.environ.copy()
        env['OPENCLAW_STATE_DIR'] = str(instance_path)
        env['OPENCLAW_CONFIG_PATH'] = str(instance_path / '.openclaw' / 'openclaw.json')
        
        print(f"⏳ 启动命令: {' '.join(cmd)}")
        print(f"   端口: {port}")
        print(f"   工作空间: {instance_path}")
        
        # 4. 启动进程
        try:
            if background:
                # 后台启动
                log_file = self.pm.get_logs_dir() / f"{name}.log"
                log_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(log_file, 'w') as f:
                    process = subprocess.Popen(
                        cmd,
                        env=env,
                        stdout=f,
                        stderr=subprocess.STDOUT,
                        start_new_session=True
                    )
                
                pid = process.pid
                print(f"✅ 已启动，PID: {pid}")
                print(f"   日志文件: {log_file}")
                
                # 等待确认启动
                time.sleep(2)
                if self._is_process_alive(pid):
                    print(f"✅ 进程运行中")
                    
                    # 更新状态
                    instance_info['status'] = 'running'
                    instance_info['process_pid'] = pid
                    instance_info['started_at'] = datetime.now().isoformat()
                    self._update_instance_info(name, instance_info)
                    
                    print(f"\n🎉 实例启动成功！")
                    
                    # 读取 token 生成带认证的 URL
                    workspace_path_obj = Path(instance_info.get('workspace_path', ''))
                    token_url = self._get_dashboard_url(workspace_path_obj, port)
                    
                    print(f"\n🎯 访问方式:")
                    print(f"   Web UI: {token_url}")
                    print(f"   日志: tail -f {log_file}")
                    print(f"\n🎯 其他操作:")
                    print(f"   查看状态: python {__file__} status {name}")
                    print(f"   停止实例: python {__file__} stop {name}")
                    
                    return pid
                else:
                    print(f"❌ 进程启动失败")
                    print(f"   查看日志: tail -20 {log_file}")
                    return None
            else:
                # 前台运行
                print(f"⏳ 前台运行中...（Ctrl+C 停止）")
                subprocess.run(cmd, env=env)
                return None
                
        except Exception as e:
            print(f"❌ 启动失败: {e}")
            return None
    
    def stop(self, name: str) -> bool:
        """
        停止实例
        
        Args:
            name: 实例名称
        
        Returns:
            是否成功
        """
        print(f"\n{'=' * 80}")
        print(f"🛑 停止实例: {name}")
        print(f"={'=' * 80}\n")
        
        # 1. 加载实例信息
        instance_info = self._load_instance_info(name)
        if not instance_info:
            print(f"❌ 实例不存在: {name}")
            return False
        
        # 2. 获取 PID
        pid = instance_info.get('process_pid')
        if not pid:
            print(f"⚠️  实例未运行（无PID记录）")
            return True
        
        # 3. 检查进程是否存在
        if not self._is_process_alive(pid):
            print(f"⚠️  进程不存在（PID: {pid}）")
            instance_info['status'] = 'stopped'
            instance_info['process_pid'] = None
            self._update_instance_info(name, instance_info)
            return True
        
        # 4. 发送停止信号
        try:
            os.kill(pid, signal.SIGTERM)
            print(f"⏳ 已发送停止信号（PID: {pid}）")
            
            # 等待进程结束
            for i in range(10):
                time.sleep(0.5)
                if not self._is_process_alive(pid):
                    print(f"✅ 进程已停止")
                    break
            else:
                # 10次后仍未停止，强制kill
                print(f"⚠️  进程未响应，强制停止...")
                os.kill(pid, signal.SIGKILL)
                time.sleep(1)
            
            # 更新状态
            instance_info['status'] = 'stopped'
            instance_info['process_pid'] = None
            instance_info['stopped_at'] = datetime.now().isoformat()
            self._update_instance_info(name, instance_info)
            
            print(f"✅ 实例已停止: {name}")
            return True
            
        except ProcessLookupError:
            print(f"⚠️  进程已不存在")
            instance_info['status'] = 'stopped'
            instance_info['process_pid'] = None
            self._update_instance_info(name, instance_info)
            return True
        except Exception as e:
            print(f"❌ 停止失败: {e}")
            return False
    
    def restart(self, name: str) -> bool:
        """重启实例"""
        print(f"\n🔄 重启实例: {name}\n")
        
        # 先停止
        if not self.stop(name):
            print(f"❌ 停止失败，取消重启")
            return False
        
        time.sleep(2)
        
        # 再启动
        pid = self.start(name)
        return pid is not None
    
    def status(self, name: str) -> Optional[Dict[str, Any]]:
        """
        查看实例状态
        
        Args:
            name: 实例名称
        
        Returns:
            状态信息字典
        """
        print(f"\n{'=' * 80}")
        print(f"📊 实例状态: {name}")
        print(f"{'=' * 80}\n")
        
        # 加载实例信息
        instance_info = self._load_instance_info(name)
        if not instance_info:
            print(f"❌ 实例不存在: {name}")
            return None
        
        # 检查进程状态
        pid = instance_info.get('process_pid')
        process_alive = self._is_process_alive(pid) if pid else False
        
        # 如果PID记录与实际不符，更新状态
        if pid and not process_alive:
            instance_info['status'] = 'stopped'
            instance_info['process_pid'] = None
            self._update_instance_info(name, instance_info)
        
        # 显示状态
        print(f"名称: {name}")
        print(f"状态: {'🟢 运行中' if process_alive else '🔴 已停止'}")
        print(f"端口: {instance_info.get('gateway_port', 'N/A')}")
        print(f"模型: {instance_info.get('model', 'N/A')}")
        print(f"工作空间: {instance_info.get('workspace_path', 'N/A')}")
        
        if pid:
            print(f"进程PID: {pid}")
        
        if process_alive and pid:
            # 显示进程信息
            try:
                import psutil
                proc = psutil.Process(pid)
                print(f"CPU: {proc.cpu_percent()}%")
                print(f"内存: {proc.memory_info().rss / 1024 / 1024:.1f} MB")
                print(f"运行时间: {time.time() - proc.create_time():.0f} 秒")
            except:
                pass
        
        print(f"\n创建时间: {instance_info.get('created_at', 'N/A')}")
        if instance_info.get('started_at'):
            print(f"启动时间: {instance_info.get('started_at')}")
        
        # 如果正在运行，显示访问 URL
        if process_alive:
            workspace_path = Path(instance_info.get('workspace_path', ''))
            port = instance_info.get('gateway_port', 0)
            if workspace_path and port:
                dashboard_url = self._get_dashboard_url(workspace_path, port)
                print(f"\n🌐 访问地址:")
                print(f"   Web UI: {dashboard_url}")
        
        print(f"\n🎯 可用操作:")
        if process_alive:
            print(f"   停止: python {__file__} stop {name}")
            print(f"   重启: python {__file__} restart {name}")
            print(f"   日志: python {__file__} logs {name}")
        else:
            print(f"   启动: python {__file__} start {name}")
            print(f"   删除: python {__file__} delete {name}")
        
        return instance_info
    
    def list(self) -> List[Dict[str, Any]]:
        """列出所有实例"""
        print(f"\n{'=' * 80}")
        print(f"📋 实例列表")
        print(f"{'=' * 80}\n")
        
        agents_db = self.pm.get_agents_db()
        
        if not agents_db.exists():
            print("没有实例记录")
            return []
        
        instances = []
        with open(agents_db, 'r') as f:
            for line in f:
                if line.strip():
                    try:
                        instances.append(json.loads(line))
                    except:
                        pass
        
        if not instances:
            print("没有实例")
            return []
        
        # 显示表格
        print(f"{'名称':<25} {'状态':<10} {'端口':<8} {'模型':<30}")
        print("-" * 80)
        
        for inst in instances:
            name = inst.get('name', 'N/A')
            pid = inst.get('process_pid')
            status = '🟢 运行中' if (pid and self._is_process_alive(pid)) else '🔴 已停止'
            port = inst.get('gateway_port', 'N/A')
            model = inst.get('model', 'N/A')
            
            print(f"{name:<25} {status:<10} {port:<8} {model:<30}")
        
        print(f"\n总计: {len(instances)} 个实例")
        return instances
    
    def delete(self, name: str, force: bool = False) -> bool:
        """
        删除实例
        
        Args:
            name: 实例名称
            force: 是否跳过确认
        
        Returns:
            是否成功
        """
        print(f"\n{'=' * 80}")
        print(f"🗑️  删除实例: {name}")
        print(f"{'=' * 80}\n")
        
        # 1. 加载实例信息
        instance_info = self._load_instance_info(name)
        if not instance_info:
            print(f"❌ 实例不存在: {name}")
            return False
        
        instance_path = Path(instance_info['workspace_path'])
        
        # 2. 确认删除
        if not force:
            print(f"⚠️  警告: 即将删除实例 {name}")
            print(f"   工作空间: {instance_path}")
            print(f"   这将删除所有数据，无法恢复！\n")
            confirm = input("是否继续？[yes/no]: ")
            if confirm.lower() not in ['yes', 'y']:
                print("操作已取消")
                return False
        
        # 3. 停止实例（如果运行中）
        pid = instance_info.get('process_pid')
        if pid and self._is_process_alive(pid):
            print(f"⏳ 停止运行中的实例（PID: {pid}）...")
            self.stop(name)
        
        # 4. 删除工作空间
        print(f"⏳ 删除工作空间...")
        try:
            import shutil
            shutil.rmtree(instance_path)
            print(f"✅ 工作空间已删除")
        except Exception as e:
            print(f"❌ 删除工作空间失败: {e}")
            return False
        
        # 5. 从数据库移除
        self._remove_instance_info(name)
        print(f"✅ 实例记录已移除")
        
        print(f"\n✅ 实例已删除: {name}")
        return True
    
    def logs(self, name: str, lines: int = 50):
        """查看实例日志"""
        instance_info = self._load_instance_info(name)
        if not instance_info:
            print(f"❌ 实例不存在: {name}")
            return
        
        log_file = self.pm.get_logs_dir() / f"{name}.log"
        
        if not log_file.exists():
            print(f"⚠️  日志文件不存在: {log_file}")
            # 尝试查找 OpenClaw 自己的日志
            instance_path = Path(instance_info['workspace_path'])
            openclaw_log = instance_path / '.openclaw' / 'logs' / 'gateway.log'
            if openclaw_log.exists():
                log_file = openclaw_log
                print(f"   使用 OpenClaw 日志: {log_file}")
            else:
                return
        
        print(f"\n📋 实例日志: {name}")
        print(f"{'=' * 80}\n")
        
        os.system(f"tail -n {lines} {log_file}")
    
    # ========== 内部辅助方法 ==========
    
    def _instance_exists(self, name: str) -> bool:
        """检查实例是否存在"""
        return self._load_instance_info(name) is not None
    
    def _load_instance_info(self, name: str) -> Optional[Dict[str, Any]]:
        """加载实例信息"""
        agents_db = self.pm.get_agents_db()
        
        if not agents_db.exists():
            return None
        
        with open(agents_db, 'r') as f:
            for line in f:
                if line.strip():
                    try:
                        info = json.loads(line)
                        if info.get('name') == name:
                            return info
                    except:
                        pass
        
        return None
    
    def _save_instance_info(self, instance_info: Dict[str, Any]):
        """保存实例信息"""
        agents_db = self.pm.get_agents_db()
        agents_db.parent.mkdir(parents=True, exist_ok=True)
        
        with open(agents_db, 'a') as f:
            f.write(json.dumps(instance_info, ensure_ascii=False) + '\n')
    
    def _get_dashboard_url(self, workspace_path: Path, port: int) -> str:
        """
        获取带 token 的 dashboard URL
        
        Args:
            workspace_path: 工作空间路径
            port: 端口号
        
        Returns:
            带 token 的完整 URL
        """
        try:
            config_file = workspace_path / '.openclaw' / 'openclaw.json'
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                token = config.get('gateway', {}).get('auth', {}).get('token', '')
                if token:
                    return f"http://127.0.0.1:{port}/#token={token}"
        except Exception:
            pass
        
        # 如果无法获取 token，返回不带 token 的 URL（会需要手动输入）
        return f"http://127.0.0.1:{port}/"
    
    def _update_instance_info(self, name: str, new_info: Dict[str, Any]):
        """更新实例信息"""
        agents_db = self.pm.get_agents_db()
        
        if not agents_db.exists():
            return
        
        # 读取所有实例
        instances = []
        with open(agents_db, 'r') as f:
            for line in f:
                if line.strip():
                    try:
                        info = json.loads(line)
                        if info.get('name') == name:
                            instances.append(new_info)
                        else:
                            instances.append(info)
                    except:
                        pass
        
        # 写回
        with open(agents_db, 'w') as f:
            for info in instances:
                f.write(json.dumps(info, ensure_ascii=False) + '\n')
    
    def _remove_instance_info(self, name: str):
        """移除实例信息"""
        agents_db = self.pm.get_agents_db()
        
        if not agents_db.exists():
            return
        
        # 读取所有实例（排除要删除的）
        instances = []
        with open(agents_db, 'r') as f:
            for line in f:
                if line.strip():
                    try:
                        info = json.loads(line)
                        if info.get('name') != name:
                            instances.append(info)
                    except:
                        pass
        
        # 写回
        with open(agents_db, 'w') as f:
            for info in instances:
                f.write(json.dumps(info, ensure_ascii=False) + '\n')
    
    def _allocate_port(self) -> int:
        """自动分配端口"""
        base_port = 18800
        step = 100
        
        # 获取所有已用端口
        used_ports = set()
        agents_db = self.pm.get_agents_db()
        if agents_db.exists():
            with open(agents_db, 'r') as f:
                for line in f:
                    if line.strip():
                        try:
                            info = json.loads(line)
                            used_ports.add(info.get('gateway_port'))
                        except:
                            pass
        
        # 分配未使用的端口
        port = base_port
        while port in used_ports:
            port += step
        
        return port
    
    def _auto_select_model(self) -> str:
        """自动选择模型"""
        # 尝试从 models.json 读取第一个可用模型
        models_config = self.pm.get_models_config()
        
        if models_config.exists():
            try:
                with open(models_config, 'r') as f:
                    config = json.load(f)
                    providers = config.get('models', {}).get('providers', {})
                    
                    # 找第一个有模型的 provider
                    for provider_name, provider_config in providers.items():
                        models = provider_config.get('models', [])
                        if models and len(models) > 0:
                            model_id = models[0].get('id') or models[0].get('name')
                            if model_id:
                                return f"{provider_name}/{model_id}"
            except:
                pass
        
        # 默认模型
        return "gpt-3.5-turbo"
    
    def _configure_model(self, instance_path: Path, model: str) -> bool:
        """
        配置默认模型
        
        注意: 此方法已弃用原有的模型配置合并逻辑，现在由 _sync_models_config 负责
        """
        config_file = instance_path / '.openclaw' / 'openclaw.json'

        if not config_file.exists():
            return False

        try:
            # 读取配置
            with open(config_file, 'r') as f:
                config = json.load(f)

            # 设置默认模型
            if 'agents' not in config:
                config['agents'] = {}
            if 'defaults' not in config['agents']:
                config['agents']['defaults'] = {}
            if 'model' not in config['agents']['defaults']:
                config['agents']['defaults']['model'] = {}

            config['agents']['defaults']['model']['primary'] = model

            # 写回配置
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            return True
        except Exception as e:
            print(f"⚠️  配置模型失败: {e}")
            return False
    
    def _sync_models_config(self, instance_path: Path) -> bool:
        """
        同步完整的模型配置到实例
        
        从 workspace/data/models.json 读取配置，合并到实例的 openclaw.json
        这样可以避免 "Unknown model" 问题
        
        Args:
            instance_path: 实例路径
        
        Returns:
            是否成功
        """
        config_file = instance_path / '.openclaw' / 'openclaw.json'
        global_models_file = self.pm.get_data_dir() / 'models.json'
        
        if not config_file.exists():
            return False
        
        if not global_models_file.exists():
            return False
        
        try:
            # 读取实例配置
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # 读取全局模型配置
            with open(global_models_file, 'r') as f:
                global_models = json.load(f)
            
            # 合并 models 配置
            if 'providers' in global_models:
                # 全局配置格式: { "providers": { "bailian": {...} } }
                if 'models' not in config:
                    config['models'] = {}
                config['models']['providers'] = global_models['providers']
            
            # 确保 agents.defaults.models 包含所有可用模型
            if 'agents' in config and 'defaults' in config['agents']:
                if 'models' not in config['agents']['defaults']:
                    config['agents']['defaults']['models'] = {}
                
                # 添加所有 bailian 模型
                if 'bailian' in global_models.get('providers', {}):
                    bailian_models = global_models['providers']['bailian'].get('models', [])
                    for model_info in bailian_models:
                        model_id = f"bailian/{model_info['id']}"
                        if model_id not in config['agents']['defaults']['models']:
                            config['agents']['defaults']['models'][model_id] = {}
            
            # 保存配置
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"⚠️  同步模型配置失败: {e}")
            return False
    
    def _is_process_alive(self, pid: Optional[int]) -> bool:
        """检查进程是否存在"""
        if not pid:
            return False
        
        try:
            os.kill(pid, 0)
            return True
        except (OSError, ProcessLookupError):
            return False
    
    # ==================== 健康检查功能（整合自 scripts/health_check.py） ====================
    
    def health_check(self, instance_name: Optional[str] = None) -> int:
        """
        健康检查
        
        Args:
            instance_name: 实例名称（None=检查所有实例）
        
        Returns:
            退出码 (0=正常, 1=有问题)
        """
        print("=" * 80)
        print("🏥 OpenClaw 实例健康检查")
        print("=" * 80)
        print()
        
        # 获取要检查的实例
        if instance_name:
            instance_path = self.pm.get_instance_path(instance_name)
            if not instance_path.exists():
                print(f"❌ 实例不存在: {instance_name}")
                return 1
            instances = [instance_path]
            print(f"📋 检查单个实例: {instance_name}\n")
        else:
            lobsters_dir = self.pm.get_lobsters_dir()
            if not lobsters_dir.exists():
                print(f"⚠️  实例目录不存在: {lobsters_dir}")
                return 0
            instances = [d for d in lobsters_dir.iterdir() if d.is_dir()]
            if not instances:
                print(f"ℹ️  没有找到实例")
                return 0
            print(f"📋 检查 {len(instances)} 个实例...\n")
        
        # 检查每个实例
        all_results = []
        critical_count = 0
        warning_count = 0
        
        for instance_path in instances:
            result = self._check_instance_health(instance_path)
            all_results.append(result)
            
            # 统计问题
            for issue in result['issues']:
                if issue['severity'] == 'critical':
                    critical_count += 1
                elif issue['severity'] == 'warning':
                    warning_count += 1
        
        # 显示结果
        for result in all_results:
            if not result['issues']:
                print(f"✅ {result['name']}: 健康")
            else:
                print(f"⚠️  {result['name']}: 发现 {len(result['issues'])} 个问题")
                for issue in result['issues']:
                    severity_icon = "🔴" if issue['severity'] == 'critical' else "⚠️ "
                    print(f"   {severity_icon} [{issue['type']}] {issue['message']}")
        
        # 总结
        print()
        print("=" * 80)
        print("📊 健康检查结果")
        print("=" * 80)
        print(f"总实例数: {len(instances)}")
        print(f"健康实例: {len([r for r in all_results if not r['issues']])}")
        print(f"有问题实例: {len([r for r in all_results if r['issues']])}")
        print(f"  - 严重问题: {critical_count}")
        print(f"  - 警告: {warning_count}")
        print()
        
        return 1 if (critical_count > 0 or warning_count > 0) else 0
    
    def _check_instance_health(self, instance_path: Path) -> Dict[str, Any]:
        """检查单个实例"""
        instance_name = instance_path.name
        
        result = {
            "name": instance_name,
            "path": str(instance_path),
            "issues": []
        }
        
        # 1. 检查命名规范
        naming_ok, naming_msg = self._check_naming_convention(instance_name)
        if not naming_ok:
            result["issues"].append({
                "type": "naming",
                "severity": "warning",
                "message": f"命名不规范: {naming_msg}"
            })
        
        # 2. 检查模型配置
        model_ok, model_msg = self._check_model_config(instance_path)
        if not model_ok:
            result["issues"].append({
                "type": "model_config",
                "severity": "critical",
                "message": f"模型配置问题: {model_msg}"
            })
        
        # 3. 检查配对状态
        pairing_ok, pairing_msg = self._check_pairing_status(instance_path)
        if not pairing_ok:
            result["issues"].append({
                "type": "pairing",
                "severity": "warning",
                "message": f"配对状态: {pairing_msg}"
            })
        
        return result
    
    def _check_naming_convention(self, instance_name: str) -> tuple:
        """检查命名规范"""
        # 检查中文字符
        if any('\u4e00' <= c <= '\u9fff' for c in instance_name):
            return False, "包含中文字符"
        
        # 检查前缀
        if not instance_name.startswith('openclaw-'):
            return False, "缺少 'openclaw-' 前缀"
        
        # 检查大小写
        if instance_name != instance_name.lower():
            return False, "包含大写字母"
        
        # 检查非法字符
        allowed = set('abcdefghijklmnopqrstuvwxyz0123456789-')
        if not all(c in allowed for c in instance_name):
            return False, "包含非法字符"
        
        return True, "符合规范"
    
    def _check_pairing_status(self, instance_path: Path) -> tuple:
        """检查飞书配对状态"""
        pairing_file = instance_path / 'credentials' / 'feishu-pairing.json'
        
        if not pairing_file.exists():
            return True, "无配对文件（正常）"
        
        try:
            with open(pairing_file, 'r') as f:
                pairing = json.load(f)
            
            pending_count = len(pairing.get('requests', []))
            
            if pending_count > 0:
                users = [req.get('meta', {}).get('name', '未知') for req in pairing['requests']]
                return False, f"有 {pending_count} 个待配对请求: {', '.join(users)}"
            else:
                return True, "无待配对请求"
        except Exception as e:
            return False, f"检查失败: {e}"
    
    def _check_model_config(self, instance_path: Path) -> tuple:
        """检查模型配置完整性"""
        config_file = instance_path / '.openclaw' / 'openclaw.json'
        
        if not config_file.exists():
            return False, "配置文件不存在"
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # 检查 models.providers 是否存在
            if 'models' not in config:
                return False, "缺少 models 配置"
            
            if 'providers' not in config['models']:
                return False, "缺少 models.providers 配置"
            
            if 'bailian' not in config['models']['providers']:
                return False, "缺少 bailian provider 配置"
            
            # 检查 bailian 配置完整性
            bailian = config['models']['providers']['bailian']
            required_fields = ['baseUrl', 'apiKey', 'api', 'models']
            
            for field in required_fields:
                if field not in bailian:
                    return False, f"bailian 缺少 {field} 字段"
            
            if not isinstance(bailian['models'], list):
                return False, "bailian.models 格式错误"
            
            if len(bailian['models']) == 0:
                return False, "bailian.models 为空"
            
            return True, f"配置正常 ({len(bailian['models'])} 个模型)"
            
        except Exception as e:
            return False, f"配置文件解析失败: {e}"


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description='OpenClaw 实例管理器')
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # create 命令
    create_parser = subparsers.add_parser('create', help='创建新实例')
    create_parser.add_argument('name', help='实例名称（如 openclaw-test-01）')
    create_parser.add_argument('--model', help='AI模型（如 bailian/qwen3.5-plus）')
    create_parser.add_argument('--port', type=int, help='端口号（默认自动分配）')
    
    # start 命令
    start_parser = subparsers.add_parser('start', help='启动实例')
    start_parser.add_argument('name', help='实例名称')
    start_parser.add_argument('--foreground', action='store_true', help='前台运行')
    
    # stop 命令
    stop_parser = subparsers.add_parser('stop', help='停止实例')
    stop_parser.add_argument('name', help='实例名称')
    
    # restart 命令
    restart_parser = subparsers.add_parser('restart', help='重启实例')
    restart_parser.add_argument('name', help='实例名称')
    
    # status 命令
    status_parser = subparsers.add_parser('status', help='查看实例状态')
    status_parser.add_argument('name', help='实例名称')
    
    # list 命令
    list_parser = subparsers.add_parser('list', help='列出所有实例')
    
    # logs 命令
    logs_parser = subparsers.add_parser('logs', help='查看实例日志')
    logs_parser.add_argument('name', help='实例名称')
    logs_parser.add_argument('--lines', type=int, default=50, help='显示行数')
    
    # delete 命令
    delete_parser = subparsers.add_parser('delete', help='删除实例')
    delete_parser.add_argument('name', help='实例名称')
    delete_parser.add_argument('--force', action='store_true', help='强制删除，不确认')
    
    # health-check 命令
    health_parser = subparsers.add_parser('health-check', help='健康检查')
    health_parser.add_argument('name', nargs='?', help='实例名称（可选，默认检查所有）')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 创建管理器
    manager = InstanceManager()
    
    # 执行命令
    try:
        if args.command == 'create':
            manager.create(args.name, model=args.model, port=args.port)
        elif args.command == 'start':
            manager.start(args.name, background=not args.foreground)
        elif args.command == 'stop':
            manager.stop(args.name)
        elif args.command == 'restart':
            manager.restart(args.name)
        elif args.command == 'status':
            manager.status(args.name)
        elif args.command == 'list':
            manager.list()
        elif args.command == 'logs':
            manager.logs(args.name, lines=args.lines)
        elif args.command == 'delete':
            manager.delete(args.name, force=args.force)
        elif args.command == 'health-check':
            exit_code = manager.health_check(args.name)
            sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
