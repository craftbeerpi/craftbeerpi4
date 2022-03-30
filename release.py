import code
import subprocess
import click
import re

@click.group()
def main():
    pass

@click.command()
@click.option('-m', prompt='Commit Message')
def commit(m):
    
    new_content = []
    file = "./cbpi/__init__.py"
    with open(file) as reader:
        match = re.search('.*\"(.*)\"', reader.readline())
        codename = reader.readline() 
        try:
            major, minor, patch, build = match.group(1).split(".")
        except:
            major, minor, patch = match.group(1).split(".")           
        patch = int(patch)
        patch += 1
        new_content.append("__version__ = \"{}.{}.{}\"".format(major,minor,patch))
        new_content.append(codename)
        with open(file,'w',encoding = 'utf-8') as file:
            print("New Version {}.{}.{}".format(major,minor,patch)) 
            file.writelines("%s\n" % i for i in new_content)

    subprocess.run(["git", "add", "-A"])
    subprocess.run(["git", "commit", "-m", "\"{}\"".format(m)])
    subprocess.run(["git", "push"])


@click.command()
def build():
    subprocess.run(["python3", "setup.py", "sdist"])
    


@click.command()
def release():
    subprocess.run(["python3", "setup.py", "sdist"])
    file = "./cbpi/__init__.py"
    with open(file) as reader:
        match = re.search('.*\"(.*)\"', reader.readline())
        version = match.group(1)
        
        path = "dist/cbpi-{}.tar.gz".format(version)
        print("Uploading File {} ".format(path))
        subprocess.run(["twine", "upload", path])
          

main.add_command(commit)
main.add_command(release)
main.add_command(build)

if __name__ == '__main__':
    main()
