import shlex
import re
from typing import Dict, List, Optional, Tuple


class DockerRunParser:
    def __init__(self):
        self.param_mapping = {
            '-a': 'attach',
            '--attach': 'attach',
            '--add-host': 'add_host',
            '--blkio-weight': 'blkio_weight',
            '--blkio-weight-device': 'blkio_weight_device',
            '--cap-add': 'cap_add',
            '--cap-drop': 'cap_drop',
            '--cgroup-parent': 'cgroup_parent',
            '--cidfile': 'cidfile',
            '--cpu-period': 'cpu_period',
            '--cpu-quota': 'cpu_quota',
            '-c': 'cpu_shares',
            '--cpu-shares': 'cpu_shares',
            '--cpus': 'cpus',
            '--cpuset-cpus': 'cpuset_cpus',
            '--cpuset-mems': 'cpuset_mems',
            '-d': 'detach',
            '--detach': 'detach',
            '--device': 'device',
            '--device-cgroup-rule': 'device_cgroup_rule',
            '--device-read-bps': 'device_read_bps',
            '--device-read-iops': 'device_read_iops',
            '--device-write-bps': 'device_write_bps',
            '--device-write-iops': 'device_write_iops',
            '--disable-content-trust': 'disable_content_trust',
            '--dns': 'dns',
            '--dns-option': 'dns_option',
            '--dns-search': 'dns_search',
            '--entrypoint': 'entrypoint',
            '-e': 'env',
            '--env': 'env',
            '--env-file': 'env_file',
            '--expose': 'expose',
            '--group-add': 'group_add',
            '--health-cmd': 'health_cmd',
            '--health-interval': 'health_interval',
            '--health-retries': 'health_retries',
            '--health-timeout': 'health_timeout',
            '-h': 'hostname',
            '--hostname': 'hostname',
            '--init': 'init',
            '--init-path': 'init_path',
            '-i': 'interactive',
            '--interactive': 'interactive',
            '--ip': 'ip',
            '--ip6': 'ip6',
            '--ipc': 'ipc',
            '--isolation': 'isolation',
            '--kernel-memory': 'kernel_memory',
            '-l': 'label',
            '--label': 'label',
            '--label-file': 'label_file',
            '--link': 'link',
            '--link-local-ip': 'link_local_ip',
            '--log-driver': 'log_driver',
            '--log-opt': 'log_opt',
            '--mac-address': 'mac_address',
            '-m': 'memory',
            '--memory': 'memory',
            '--memory-reservation': 'memory_reservation',
            '--memory-swap': 'memory_swap',
            '--memory-swappiness': 'memory_swappiness',
            '--name': 'name',
            '--network-alias': 'network_alias',
            '--network': 'network',
            '--no-healthcheck': 'no_healthcheck',
            '--oom-kill-disable': 'oom_kill_disable',
            '--oom-score-adj': 'oom_score_adj',
            '--pid': 'pid',
            '--pids-limit': 'pids_limit',
            '--privileged': 'privileged',
            '-p': 'publish',
            '--publish': 'publish',
            '-P': 'publish_all',
            '--publish-all': 'publish_all',
            '--read-only': 'read_only',
            '--restart': 'restart',
            '--rm': 'rm',
            '--runtime': 'runtime',
            '--security-opt': 'security_opt',
            '--shm-size': 'shm_size',
            '--sig-proxy': 'sig_proxy',
            '--stop-signal': 'stop_signal',
            '--stop-timeout': 'stop_timeout',
            '--storage-opt': 'storage_opt',
            '--sysctl': 'sysctl',
            '--tmpfs': 'tmpfs',
            '-t': 'tty',
            '--tty': 'tty',
            '--ulimit': 'ulimit',
            '-u': 'user',
            '--user': 'user',
            '--userns': 'userns',
            '--uts': 'uts',
            '-v': 'volume',
            '--volume': 'volume',
            '--volume-driver': 'volume_driver',
            '--volumes-from': 'volumes_from',
            '-w': 'workdir',
            '--workdir': 'workdir',
            '--annotation': 'annotation',
            '--cgroupns': 'cgroupns',
            '--cpu-count': 'cpu_count',
            '--cpu-percent': 'cpu_percent',
            '--cpu-rt-period': 'cpu_rt_period',
            '--cpu-rt-runtime': 'cpu_rt_runtime',
            '--detach-keys': 'detach_keys',
            '--domainname': 'domainname',
            '--gpus': 'gpus',
            '--health-start-interval': 'health_start_interval',
            '--health-start-period': 'health_start_period',
            '--io-maxbandwidth': 'io_maxbandwidth',
            '--io-maxiops': 'io_maxiops',
            '--kernel-memory': 'kernel_memory',
            '--mac-address': 'mac_address',
            '--mount': 'mount',
            '--platform': 'platform',
            '--pull': 'pull',
            '-q': 'quiet',
            '--quiet': 'quiet',
            '--use-api-socket': 'use_api_socket',
        }

    def parse(self, command: str) -> Dict:
        if not command.startswith('docker run'):
            raise ValueError("Command must start with 'docker run'")

        # 处理反斜杠续行符
        command = command.replace('\\\n', ' ').replace('\\\r\n', ' ')

        try:
            args = shlex.split(command)
        except ValueError:
            # 如果shlex.split失败，尝试手动清理反斜杠
            command = re.sub(r'\\\s*$', '', command, flags=re.MULTILINE)
            args = shlex.split(command)

        args = args[2:]

        result = {
            'image': None,
            'command': [],
            'params': {}
        }

        i = 0
        while i < len(args):
            arg = args[i]

            if arg.startswith('-'):
                param_key = arg
                param_name = self._get_param_name(param_key)

                if self._is_bool_param(param_name):
                    result['params'][param_name] = True
                    i += 1
                else:
                    if i + 1 < len(args) and not args[i + 1].startswith('-'):
                        value = args[i + 1]
                        self._add_param(result, param_name, value)
                        i += 2
                    else:
                        result['params'][param_name] = True
                        i += 1
            else:
                if result['image'] is None:
                    result['image'] = arg
                else:
                    result['command'].append(arg)
                i += 1

        return result

    def _get_param_name(self, param_key: str) -> str:
        return self.param_mapping.get(param_key, param_key.lstrip('-'))

    def _is_bool_param(self, param_name: str) -> bool:
        bool_params = [
            'detach', 'interactive', 'tty', 'privileged', 'read_only',
            'rm', 'init', 'no_healthcheck', 'oom_kill_disable', 'publish_all',
            'disable_content_trust', 'sig_proxy'
        ]
        return param_name in bool_params

    def _add_param(self, result: Dict, param_name: str, value: str):
        multi_value_params = [
            'attach', 'add_host', 'annotation', 'cap_add', 'cap_drop', 'device', 'dns',
            'dns_option', 'dns_search', 'env', 'env_file', 'expose',
            'group_add', 'gpus', 'label', 'link', 'log_opt', 'mount', 'network_alias',
            'publish', 'security_opt', 'sysctl', 'tmpfs', 'ulimit', 'volume'
        ]

        if param_name in multi_value_params:
            if param_name not in result['params']:
                result['params'][param_name] = []
            result['params'][param_name].append(value)
        else:
            result['params'][param_name] = value

    def parse_publish(self, publish_str: str) -> Optional[Dict]:
        if ':' not in publish_str:
            return {'target': publish_str}

        parts = publish_str.split(':')
        if len(parts) == 2:
            host_port, container_port = parts
            if '/' in container_port:
                container_port, protocol = container_port.split('/')
                return {'published': host_port, 'target': container_port, 'protocol': protocol}
            return {'published': host_port, 'target': container_port}
        elif len(parts) == 3:
            host_ip, host_port, container_port = parts
            if '/' in container_port:
                container_port, protocol = container_port.split('/')
                return {'host_ip': host_ip, 'published': host_port, 'target': container_port, 'protocol': protocol}
            return {'host_ip': host_ip, 'published': host_port, 'target': container_port}

        return None

    def parse_volume(self, volume_str: str) -> Dict:
        result = {'type': 'bind'}

        parts = volume_str.split(':')
        if len(parts) == 1:
            result['target'] = parts[0]
        elif len(parts) == 2:
            result['source'], result['target'] = parts
        elif len(parts) >= 3:
            result['source'], result['target'] = parts[0], parts[1]
            options = ':'.join(parts[2:])
            result['read_only'] = 'ro' in options

        return result

    def parse_env(self, env_str: str) -> Tuple[str, str]:
        if '=' in env_str:
            key, value = env_str.split('=', 1)
            # 移除外层的引号（单引号或双引号）
            value = value.strip()
            if (value.startswith("'") and value.endswith("'")) or \
               (value.startswith('"') and value.endswith('"')):
                value = value[1:-1]
            return key, value
        return env_str, None

    def parse_link(self, link_str: str) -> Tuple[str, Optional[str]]:
        if ':' in link_str:
            container, alias = link_str.split(':', 1)
            return container, alias
        return link_str, None

    def parse_network_alias(self, alias_str: str) -> str:
        return alias_str

    def parse_add_host(self, host_str: str) -> Tuple[str, str]:
        if ':' in host_str:
            host, ip = host_str.split(':', 1)
            return host, ip
        return host_str, ''

    def parse_ulimit(self, ulimit_str: str) -> Dict:
        parts = ulimit_str.split('=')
        if len(parts) == 2:
            name, value = parts
            if ':' in value:
                soft, hard = value.split(':', 1)
                return {'name': name, 'soft': int(soft), 'hard': int(hard)}
            else:
                return {'name': name, 'soft': int(value), 'hard': int(value)}
        return {}

    def parse_sysctl(self, sysctl_str: str) -> Tuple[str, str]:
        if '=' in sysctl_str:
            key, value = sysctl_str.split('=', 1)
            return key, value
        return sysctl_str, ''

    def parse_device(self, device_str: str) -> Dict:
        if ':' in device_str:
            parts = device_str.split(':')
            if len(parts) >= 2:
                result = {'path_on_host': parts[0], 'path_in_container': parts[1]}
                if len(parts) >= 3:
                    result['permissions'] = parts[2]
                return result
        return {'path_on_host': device_str, 'path_in_container': device_str}

    def parse_expose(self, expose_str: str) -> str:
        if '/' in expose_str:
            port, protocol = expose_str.split('/', 1)
            return int(port)
        return int(expose_str)
