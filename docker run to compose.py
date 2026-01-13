#!/usr/bin/env python3
import sys
from cli import CLI


def main():
    if len(sys.argv) == 1:
        # Check if docker run.txt exists
        import os
        docker_run_file = os.path.join(os.getcwd(), 'docker run.txt')
        if os.path.exists(docker_run_file):
            # Run with file input and output to docker-compose.yml
            cli = CLI()
            output_file = os.path.join(os.getcwd(), 'docker-compose.yml')
            args = ['--file', docker_run_file, '--output', output_file]
            cli.run(args)
        else:
            cli = CLI()
            cli.interactive()
    else:
        cli = CLI()
        cli.run()


if __name__ == '__main__':
    main()
