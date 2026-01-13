from typing import Dict, List, Optional, Tuple
from parser import DockerRunParser


class DockerComposeMapper:
    def __init__(self):
        self.parser = DockerRunParser()

    def map_to_service(self, parsed: Dict) -> Dict:
        service = {}
        params = parsed.get('params', {})

        service['image'] = parsed['image']

        if parsed.get('command'):
            service['command'] = parsed['command']

        if 'name' in params:
            service['container_name'] = params['name']

        if 'hostname' in params:
            service['hostname'] = params['hostname']

        if 'entrypoint' in params:
            service['entrypoint'] = self._parse_command(params['entrypoint'])

        if 'workdir' in params:
            service['working_dir'] = params['workdir']

        # 新增参数处理
        if 'annotation' in params:
            # Annotations in Docker Compose are not directly supported
            # They can be added as labels with a specific prefix
            if 'labels' not in service:
                service['labels'] = {}
            for annotation in params['annotation']:
                key, value = annotation.split('=', 1) if '=' in annotation else (annotation, '')
                service['labels'][f'annotation.{key}'] = value

        if 'cgroupns' in params:
            service['cgroup'] = params['cgroupns']

        if 'cpu_count' in params:
            # Windows specific, not directly supported in Docker Compose
            pass

        if 'cpu_percent' in params:
            # Windows specific, not directly supported in Docker Compose
            pass

        if 'cpu_rt_period' in params:
            # Real-time CPU scheduling, not directly supported in Docker Compose
            pass

        if 'cpu_rt_runtime' in params:
            # Real-time CPU scheduling, not directly supported in Docker Compose
            pass

        if 'detach_keys' in params:
            # Not applicable in Docker Compose
            pass

        if 'domainname' in params:
            service['domainname'] = params['domainname']

        if 'gpus' in params:
            service['deploy'] = service.get('deploy', {})
            service['deploy']['resources'] = service['deploy'].get('resources', {})
            service['deploy']['resources']['reservations'] = service['deploy']['resources'].get('reservations', {})
            service['deploy']['resources']['reservations']['devices'] = [{'driver': 'nvidia', 'count': params['gpus'][0], 'capabilities': ['gpu']}]

        if 'health_start_interval' in params:
            if 'healthcheck' not in service:
                service['healthcheck'] = {}
            service['healthcheck']['start_interval'] = params['health_start_interval']

        if 'health_start_period' in params:
            if 'healthcheck' not in service:
                service['healthcheck'] = {}
            service['healthcheck']['start_period'] = params['health_start_period']

        if 'io_maxbandwidth' in params:
            # Windows specific, not directly supported
            pass

        if 'io_maxiops' in params:
            # Windows specific, not directly supported
            pass

        if 'kernel_memory' in params:
            # Deprecated parameter
            pass

        if 'mac_address' in params:
            service['mac_address'] = params['mac_address']

        if 'mount' in params:
            # Mount syntax is different from volume
            # This is complex, for now we'll treat it as volumes
            for mount in params['mount']:
                if 'type=bind' in mount or 'type=volume' in mount:
                    # Parse mount options
                    mount_parts = mount.split(',')
                    source = dest = ''
                    options = []
                    for part in mount_parts:
                        if part.startswith('source=') or part.startswith('src='):
                            source = part.split('=', 1)[1]
                        elif part.startswith('destination=') or part.startswith('dst=') or part.startswith('target='):
                            dest = part.split('=', 1)[1]
                        elif part.startswith('readonly') or part == 'ro':
                            options.append('ro')
                    if source and dest:
                        volume_str = f"{source}:{dest}"
                        if 'ro' in options:
                            volume_str += ':ro'
                        if 'volumes' not in service:
                            service['volumes'] = []
                        service['volumes'].append(volume_str)

        if 'platform' in params:
            service['platform'] = params['platform']

        if 'pull' in params:
            service['pull_policy'] = params['pull']

        if 'quiet' in params:
            # Not applicable in Docker Compose
            pass

        if 'use_api_socket' in params:
            # This would bind mount the Docker socket
            if 'volumes' not in service:
                service['volumes'] = []
            service['volumes'].extend([
                '/var/run/docker.sock:/var/run/docker.sock',
                '/usr/bin/docker:/usr/bin/docker:ro'
            ])
            service['privileged'] = True

        if 'user' in params:
            service['user'] = params['user']

        if 'restart' in params:
            service['restart'] = self._map_restart(params['restart'])

        if 'privileged' in params:
            service['privileged'] = True

        if 'read_only' in params:
            service['read_only'] = True

        if 'publish' in params:
            service['ports'] = [self._map_publish(p) for p in params['publish']]

        if 'expose' in params:
            service['expose'] = [self.parser.parse_expose(e) for e in params['expose']]

        if 'env' in params:
            service['environment'] = self._map_env(params['env'])

        if 'env_file' in params:
            service['env_file'] = params['env_file']

        if 'volume' in params:
            service['volumes'] = [self._map_volume(v) for v in params['volume']]

        if 'volumes_from' in params:
            service['volumes_from'] = params['volumes_from']

        if 'network' in params:
            service['networks'] = {params['network']: {}}
        elif 'network_alias' in params:
            service['networks'] = {'default': {'aliases': [self.parser.parse_network_alias(a) for a in params['network_alias']]}}

        if 'link' in params:
            service['links'] = [self._map_link(l) for l in params['link']]

        if 'cap_add' in params:
            service['cap_add'] = params['cap_add']

        if 'cap_drop' in params:
            service['cap_drop'] = params['cap_drop']

        if 'device' in params:
            service['devices'] = [self.parser.parse_device(d) for d in params['device']]

        if 'dns' in params:
            service['dns'] = params['dns']

        if 'dns_search' in params:
            service['dns_search'] = params['dns_search']

        if 'dns_option' in params:
            service['dns_options'] = params['dns_option']

        if 'shm_size' in params:
            service['shm_size'] = params['shm_size']

        if 'tmpfs' in params:
            service['tmpfs'] = params['tmpfs']

        if 'sysctl' in params:
            service['sysctls'] = [dict([self.parser.parse_sysctl(s)]) for s in params['sysctl']]

        if 'ulimit' in params:
            service['ulimits'] = [self.parser.parse_ulimit(u) for u in params['ulimit']]

        if 'log_driver' in params or 'log_opt' in params:
            service['logging'] = {}
            if 'log_driver' in params:
                service['logging']['driver'] = params['log_driver']
            if 'log_opt' in params:
                service['logging']['options'] = dict([opt.split('=', 1) for opt in params['log_opt']])

        if 'label' in params:
            service['labels'] = [dict([l.split('=', 1) if '=' in l else (l, '')]) for l in params['label']]

        if 'ipc' in params:
            service['ipc'] = params['ipc']

        if 'pid' in params:
            service['pid'] = params['pid']

        if 'stop_signal' in params:
            service['stop_signal'] = params['stop_signal']

        if 'stop_timeout' in params:
            service['stop_grace_period'] = f"{params['stop_timeout']}s"

        if 'health_cmd' in params:
            service['healthcheck'] = {}
            service['healthcheck']['test'] = self._parse_command(params['health_cmd'])
            if 'health_interval' in params:
                service['healthcheck']['interval'] = params['health_interval']
            if 'health_timeout' in params:
                service['healthcheck']['timeout'] = params['health_timeout']
            if 'health_retries' in params:
                service['healthcheck']['retries'] = params['health_retries']

        if 'memory' in params or 'cpus' in params:
            service['deploy'] = {}
            service['deploy']['resources'] = {}
            if 'memory' in params:
                service['deploy']['resources']['limits'] = {'memory': params['memory']}
            if 'cpus' in params:
                if 'limits' not in service['deploy']['resources']:
                    service['deploy']['resources']['limits'] = {}
                service['deploy']['resources']['limits']['cpus'] = params['cpus']

        if 'memory_reservation' in params:
            if 'deploy' not in service:
                service['deploy'] = {}
            if 'resources' not in service['deploy']:
                service['deploy']['resources'] = {}
            service['deploy']['resources']['reservations'] = {'memory': params['memory_reservation']}

        if 'oom_kill_disable' in params:
            service['oom_kill_disable'] = True

        if 'oom_score_adj' in params:
            service['oom_score_adj'] = params['oom_score_adj']

        if 'group_add' in params:
            service['group_add'] = params['group_add']

        return self._clean_service(service)

    def _parse_command(self, cmd_str: str) -> List[str]:
        parts = cmd_str.split()
        if len(parts) > 1:
            return parts
        return [cmd_str]

    def _map_restart(self, restart: str) -> str:
        restart_map = {
            'no': 'no',
            'always': 'always',
            'unless-stopped': 'unless-stopped',
            'on-failure': 'on-failure'
        }
        if ':' in restart:
            policy, max_retries = restart.split(':', 1)
            return restart_map.get(policy, policy)
        return restart_map.get(restart, restart)

    def _map_publish(self, publish: str) -> Dict:
        parsed = self.parser.parse_publish(publish)
        if not parsed:
            return {}

        if 'published' in parsed:
            result = f"{parsed['published']}:{parsed['target']}"
        else:
            result = parsed['target']

        if 'protocol' in parsed:
            result += f"/{parsed['protocol']}"

        return result

    def _map_volume(self, volume: str) -> Dict:
        parsed = self.parser.parse_volume(volume)
        if parsed['type'] == 'bind':
            result = f"{parsed['source']}:{parsed['target']}"
            if parsed.get('read_only'):
                result += ':ro'
            return result
        return parsed

    def _map_env(self, env_list: List[str]) -> Dict:
        result = {}
        for env in env_list:
            key, value = self.parser.parse_env(env)
            if value is not None:
                result[key] = value
            else:
                result[key] = ''
        return result



    def _map_link(self, link: str) -> str:
        container, alias = self.parser.parse_link(link)
        if alias:
            return f"{container}:{alias}"
        return container

    def _clean_service(self, service: Dict) -> Dict:
        return {k: v for k, v in service.items() if v is not None and v != [] and v != {}}
