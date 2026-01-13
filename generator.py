import yaml
from typing import Dict, List


class DockerComposeGenerator:
    def __init__(self, version: str = '3.9'):
        self.version = version

    def generate(self, services: Dict, networks: Dict = None, volumes: Dict = None) -> str:
        compose = {'version': self.version, 'services': services}

        if networks:
            compose['networks'] = networks
        # 不添加默认的 networks 部分

        if volumes:
            compose['volumes'] = volumes

        yaml_str = self._dump_yaml(compose)

        # 添加中文注释
        lines = yaml_str.split('\n')
        result = []
        result.append('# Docker Compose 配置文件')
        result.append(f'# 由 Docker Run 到 Docker Compose 转换器生成')
        result.append('')
        result.extend(lines)

        return '\n'.join(result)

    def _dump_yaml(self, data: Dict) -> str:
        yaml.Dumper.ignore_aliases = lambda *args: True
        return yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True)

    def add_network(self, compose: Dict, network_name: str, network_config: Dict = None):
        if 'networks' not in compose:
            compose['networks'] = {}
        if network_config:
            compose['networks'][network_name] = network_config
        else:
            compose['networks'][network_name] = {'driver': 'bridge'}

    def add_volume(self, compose: Dict, volume_name: str, volume_config: Dict = None):
        if 'volumes' not in compose:
            compose['volumes'] = {}
        if volume_config:
            compose['volumes'][volume_name] = volume_config
        else:
            compose['volumes'][volume_name] = {}

    def generate_from_parsed(self, parsed_list: List[Dict]) -> str:
        services = {}
        networks = {}
        volumes = {}

        for parsed in parsed_list:
            params = parsed.get('params', {})
            service_name = params.get('name', f"service_{len(services) + 1}")

            if 'network' in params:
                network_name = params['network']
                if network_name not in networks:
                    networks[network_name] = {'driver': 'bridge'}

            if 'volume' in params:
                from parser import DockerRunParser
                parser = DockerRunParser()
                for vol_str in params['volume']:
                    parsed_vol = parser.parse_volume(vol_str)
                    if parsed_vol['type'] == 'volume' and 'source' in parsed_vol:
                        volume_name = parsed_vol['source']
                        if volume_name not in volumes:
                            volumes[volume_name] = {}

        for i, parsed in enumerate(parsed_list):
            params = parsed.get('params', {})
            if 'name' in params:
                service_name = params['name']
            else:
                # 从镜像名中提取服务名
                image_name = parsed.get('image', '')
                if '/' in image_name:
                    # 处理带命名空间的镜像，如 library/nginx 或 myuser/myapp
                    image_name = image_name.split('/')[-1]
                if ':' in image_name:
                    service_name = image_name.split(':')[0]
                else:
                    service_name = image_name
                # 如果还是空的，使用默认名称
                if not service_name:
                    service_name = f"service_{len(services) + 1}"

            services[service_name] = self._generate_service_dict(parsed)

        return self.generate(services, networks, volumes)

    def _generate_service_dict(self, parsed: Dict) -> Dict:
        from mapper import DockerComposeMapper
        mapper = DockerComposeMapper()
        return mapper.map_to_service(parsed)
