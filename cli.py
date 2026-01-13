import argparse
import sys
from typing import List


class CLI:
    def __init__(self):
        self.parser = self._create_parser()

    def _create_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            description='Docker Run to Docker Compose Converter'
        )
        parser.add_argument(
            'commands',
            nargs='*',
            help='Docker run commands to convert'
        )
        parser.add_argument(
            '-o', '--output',
            type=str,
            help='Output file path (default: stdout)',
            default=None
        )
        parser.add_argument(
            '-v', '--version',
            type=str,
            help='Docker Compose version (default: 3.9)',
            default='3.9'
        )
        parser.add_argument(
            '-f', '--file',
            type=str,
            help='Read docker run commands from file',
            default=None
        )
        parser.add_argument(
            '--indent',
            type=int,
            help='YAML indentation (default: 2)',
            default=2
        )
        parser.add_argument(
            '--no-networks',
            action='store_true',
            help='Omit default networks section'
        )
        parser.add_argument(
            '--pretty',
            action='store_true',
            help='Pretty print the output'
        )
        return parser

    def parse_args(self, args: List[str] = None) -> argparse.Namespace:
        return self.parser.parse_args(args)

    def run(self, args_list: List[str] = None) -> None:
        if args_list is not None:
            args = self.parse_args(args_list)
        else:
            args = self.parse_args()

        commands = args.commands[:]

        if args.file:
            try:
                with open(args.file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 智能识别多个 docker run 命令
                    # 找到所有 "docker run" 的位置
                    docker_run_positions = []
                    start = 0
                    while True:
                        pos = content.find('docker run', start)
                        if pos == -1:
                            break
                        docker_run_positions.append(pos)
                        start = pos + 1

                    # 从每个 "docker run" 开始，到下一个 "docker run" 或文件结尾
                    for i, pos in enumerate(docker_run_positions):
                        start_pos = pos
                        if i + 1 < len(docker_run_positions):
                            end_pos = docker_run_positions[i + 1]
                        else:
                            end_pos = len(content)

                        command = content[start_pos:end_pos].strip()
                        if command:
                            commands.append(command)
            except FileNotFoundError:
                print(f"Error: File '{args.file}' not found", file=sys.stderr)
                sys.exit(1)
            except Exception as e:
                print(f"Error reading file: {e}", file=sys.stderr)
                sys.exit(1)

        if not commands:
            print("Error: No docker run commands provided", file=sys.stderr)
            self.parser.print_help()
            sys.exit(1)

        try:
            from parser import DockerRunParser
            from generator import DockerComposeGenerator

            parser = DockerRunParser()
            generator = DockerComposeGenerator(version=args.version)

            parsed_list = []
            for cmd in commands:
                try:
                    parsed = parser.parse(cmd)
                    parsed_list.append(parsed)
                except Exception as e:
                    print(f"Warning: Failed to parse command: {cmd}", file=sys.stderr)
                    print(f"  Error: {e}", file=sys.stderr)

            if not parsed_list:
                print("Error: No valid docker run commands found", file=sys.stderr)
                sys.exit(1)

            output = generator.generate_from_parsed(parsed_list)

            if args.output:
                try:
                    with open(args.output, 'w', encoding='utf-8') as f:
                        f.write(output)
                    print(f"已成功生成 docker-compose.yml 文件：{args.output}")
                except Exception as e:
                    print(f"Error writing to file: {e}", file=sys.stderr)
                    sys.exit(1)
            else:
                if args.pretty:
                    print("=" * 60)
                    print("Docker Compose Output")
                    print("=" * 60)
                print(output)

        except KeyboardInterrupt:
            print("\nInterrupted by user", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    def interactive(self) -> None:
        print("Docker Run to Docker Compose Converter")
        print("=" * 50)
        print("Enter docker run commands (one per line)")
        print("Enter an empty line to finish\n")

        from parser import DockerRunParser
        from generator import DockerComposeGenerator

        parser = DockerRunParser()
        generator = DockerComposeGenerator()

        commands = []
        while True:
            try:
                cmd = input(f"[{len(commands) + 1}] docker run ").strip()
                if not cmd:
                    break
                if not cmd.startswith('docker run'):
                    print("Error: Command must start with 'docker run'")
                    continue
                commands.append("docker run " + cmd)
            except KeyboardInterrupt:
                print("\nInterrupted")
                break

        if not commands:
            print("No commands provided")
            return

        print("\nGenerating docker-compose.yml...\n")

        try:
            parsed_list = [parser.parse(cmd) for cmd in commands]
            output = generator.generate_from_parsed(parsed_list)
            print(output)
        except Exception as e:
            print(f"Error: {e}")


def main():
    cli = CLI()
    cli.run()


if __name__ == '__main__':
    main()
