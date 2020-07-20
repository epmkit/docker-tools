#!/usr/bin/env python
import os
import jinja2
import argparse
import yaml
import subprocess
from urllib.parse import urlparse

_DIR = os.path.normpath(os.path.abspath(os.path.dirname(__file__)))
_ROOT_DIR = os.path.normpath(os.path.join(_DIR, '..'))

def render(name, version, config):
    if not os.path.exists(os.path.join(_ROOT_DIR, name, 'Dockerfile.j2')):
        raise Exception('Jinja2 template %s not exists' % name)

    kworkds = {'name': name, 'version': version,'config': config }

#    pip_options = ''
#    if args.pypi:
#        pip_options += ' -i %s' % args.pypi # --index-url
#        url = urlparse(args.pypi)
#        if url.scheme == 'http':
#            pip_options += ' --trusted-host %s' % url.hostname
#    if args.http_proxy:
#        pip_options += ' --proxy %s' % args.http_proxy
#
#    kworkds['pip_options'] = pip_options
#    kworkds['install_epm'] = 'sudo pip install %s %s' % (pip_options, ccache_dir)
#    if args.archive_url:
#        kworkds['archive_url'] = args.archive_url
    loader = jinja2.FileSystemLoader(searchpath=[os.path.join(_ROOT_DIR, i) for i in [name, 'common', '']])
    env = jinja2.Environment(loader=loader)
    template = env.get_template('Dockerfile.j2')
    return template.render(kworkds)

def build(name, version, config):
    filename = os.path.join(_DIR, '{}.Dockerfile'.format(name))
    txt = render(name, version, config)
    with open(filename, 'w') as f:
        f.write(txt)
    command = ['docker', 'build', _DIR, '-f', filename, '-t', 'epmkit/{}:{}'.format(name, version)]
    print(command)
    subprocess.run(command, check=True)

def Main():
    parser = argparse.ArgumentParser()
    parser.add_argument('name', nargs=1, help="name of the docker image to build.")
    parser.add_argument('--version', type=str, help="specify version of the image to build instead read from epm module.")
    parser.add_argument('--build', default=False, action="store_true", help="execute image build")
    parser.add_argument('--clear', default=False, action="store_true", help="clear exist image, if build")
    args = parser.parse_args()
    name = args.name[0]
    
    with open(os.path.join(_ROOT_DIR, 'config.yml')) as f:        
        config = yaml.safe_load(f)



    do_clear = args.clear and args.build
    do_build = args.build
    version = config['conan'] if name.startswith('conan-') else 'latest'

    if do_clear:
        command = ['docker', 'rmi', 'epmkit/%s:%s' % (name, version)]
        subprocess.run(command, check=False)
    
    if do_build:
        build(name, version, config)

if __name__ == '__main__':
    Main()
