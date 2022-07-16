import json
import sys
from urllib import request    
from pkg_resources import parse_version    

def versions(pkg_name):
    url = f'https://pypi.python.org/pypi/{pkg_name}/json'
    releases = json.loads(request.urlopen(url).read())['releases']
    releases = sorted(releases, key=parse_version, reverse=True)  
    return [releases[0]]

if __name__ == '__main__':
    print(*versions(sys.argv[1]), sep='\n')