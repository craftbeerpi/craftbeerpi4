import subprocess
import click
import re


@click.group()
def main():
    pass


@click.command()
@click.option("-m", prompt="Commit Message")
def commit(m):

    file = "./cbpi/__init__.py"
    with open(file) as reader:
        match = re.search('.*"(.*)"', reader.readline())
        major, minor, patch, build = match.group(1).split(".")
        build = int(build)
        build += 1
        new_version = '__version__ = "{}.{}.{}.{}"'.format(major, minor, patch, build)
        with open(file, "w", encoding="utf-8") as file:
            print("New Version {}.{}.{}.{}".format(major, minor, patch, build))
            file.write(new_version)

    subprocess.run(["git", "add", "-A"])
    subprocess.run(["git", "commit", "-m", '"{}"'.format(m)])
    subprocess.run(["git", "push"])


@click.command()
def build():
    subprocess.run(["python3", "setup.py", "sdist"])


@click.command()
def release():
    subprocess.run(["python3", "setup.py", "sdist"])
    file = "./cbpi/__init__.py"
    with open(file) as reader:
        match = re.search('.*"(.*)"', reader.readline())
        version = match.group(1)

        path = "dist/cbpi-{}.tar.gz".format(version)
        print("Uploading File {} ".format(path))
        subprocess.run(["twine", "upload", path])


main.add_command(commit)
main.add_command(release)
main.add_command(build)

if __name__ == "__main__":
    main()
