#!/usr/bin/env python
import os, logging, argparse, platform
from string import Template

try:
    import apt
except ImportError as e:
    logging.critical("python-apt module is not installed. Maybe this is not Ubuntu.")
    raise e

REQURIED_PACKAGES_PRE = 'wget'.split()

REQURIED_PACKAGES_CWP = 'xvfb google-chrome-stable nodejs-legacy nodejs tcpdump python-numpy scrot npm firefox'.split()
REQURIED_PACKAGES_H2A = 'python-pip python-dev libxml2-dev libxslt1-dev'.split()
REQURIED_PACKAGES_TSHARK = 'libtool autoconf automake bison flex libglib2.0-dev libpcap-dev libgnutls-dev libssl-dev'.split()


os.chdir(os.path.abspath(os.path.dirname(__file__)))
TEST_DRIVER = os.path.abspath(r'../chrome-webpage-profiler')
H2_ANALYZER = os.path.abspath(r'../http2-dump-anatomy')
HAR_CAPTURER = os.path.abspath(r'../chrome-har-capturer-cache')
PYSHARK = os.path.abspath(r'../pyshark-ssl')
WEBUI = os.path.abspath(r'../chrome-webpage-profiler-webui')

#WIRESHAKR_URL='https://1.na.dl.wireshark.org/src/wireshark-1.99.7.tar.bz2'
WIRESHAKR_URL='https://1.na.dl.wireshark.org/src/wireshark-1.99.8.tar.bz2'

TSHARK = os.path.abspath(r'../wireshark-1.99.8')

def install(args):
    content = {}
    logging.info('Start preparing install script')
    checkStatus = check(args)
    if checkStatus[0] != 0:
        logging.error('Checking failed. Stop installation.')
        return

    logging.debug('Package to install first %s', str(checkStatus[2]))
    if len(checkStatus[2]) > 0:
        content['preInstall'] = 'true'
    else:
        content['preInstall'] = 'false'
    content['installFirst'] = ' '.join(checkStatus[2])

    logging.debug('Package to install %s', str(checkStatus[1]))
    if len(checkStatus[1]) > 0:
        content['installPackages'] = 'true'
    else:
        content['installPackages']= 'false'
    content['toInstall'] = ' '.join(checkStatus[1])

    content['installChrome'] = 'false'
    cannotInstall = checkStatus[3]
    if len(cannotInstall) > 0:
        logging.warning('Some packages are required but apt-get cannot install them %s', str(cannotInstall))
        if 'google-chrome-stable' in cannotInstall:
            logging.info('Will add google chrome repo')
            content['installChrome'] = 'true'

    content['tsharkURL'] = WIRESHAKR_URL
    if not args.no_tshark:
        logging.debug('Will download %s and compile tshark', WIRESHAKR_URL)
        content['compileTshark'] = 'true'
    else:
        content['compileTshark'] = 'false'
    logging.info('Start creating install script')
    with open('install.sh.tpl', 'r') as tpl:
        result_tpl = Template(tpl.read())
    result = result_tpl.safe_substitute(content)

    with open('install.sh', 'w') as script:
        script.write(result)
    os.chmod('install.sh', 0755)
    logging.info('Done, please run ./install.sh')
    

def upgrade(_):
    logging.critical('Upgrade is not implemented yet.')

def check(args):
    logging.info('Start checking')
    logging.debug('Checking system')
    system = platform.system()
    if system != 'Linux':
        logging.critical('Cannot work on %s, must be Linux', system)
        return (-1)
    dist = platform.linux_distribution()
    logging.debug('Linux distro is %s', str(dist))
    if dist[0] != 'Ubuntu':
        logging.error('The suite may work on %s, but this tool is for Ubuntu', dist[0])
        return (-2)
    if dist[1] != '14.04':
        logging.warning('This tool is for Ubuntu 14.04, but it may work on %s. Try to continue.', dist[0])

    logging.debug('Checking installed Ubuntu packages')
    cache = apt.Cache()
    packageToInstall = []
    cannotInstall = []
    installFirst = []


    logging.debug('Checking packages for preinstallation')
    for p in REQURIED_PACKAGES_PRE:
        if p not in cache:
            logging.error('Package %s not found in apt-cache, installation may fail', p)
            cannotInstall.append(p)
            continue
        if not cache[p].is_installed:
            logging.debug('Packages %s not installed, will install it', p)
            installFirst.append(p)
        else:
            logging.debug('Packages %s installed, ignore it', p)

    for p in REQURIED_PACKAGES_CWP:
        if p not in cache:
            logging.error('Package %s not found in apt-cache, installation may fail', p)
            cannotInstall.append(p)
            continue
        if not cache[p].is_installed:
            logging.debug('Packages %s not installed, will install it', p)
            packageToInstall.append(p)
        else:
            logging.debug('Packages %s installed, ignore it', p)

    logging.debug('Checking packages for http2 dump analyzer')
    for p in REQURIED_PACKAGES_H2A:
        if p not in cache:
            logging.error('Package %s not found in apt-cache, installation may fail', p)
            cannotInstall.append(p)
            continue
        if not cache[p].is_installed:
            logging.debug('Packages %s not installed, will install it', p)
            packageToInstall.append(p)
        else:
            logging.debug('Packages %s installed, ignore it', p)
    if not args.no_tshark:
        for p in REQURIED_PACKAGES_TSHARK:
            if p not in cache:
                logging.error('Package %s not found in apt-cache, installation may fail', p)
                cannotInstall.append(p)
                continue
            if not cache[p].is_installed:
                logging.debug('Packages %s not installed, will install it', p)
                packageToInstall.append(p)
            else:
                logging.debug('Packages %s installed, ignore it', p)

    logging.debug('Checking suite directories')
    if not os.path.isdir(TEST_DRIVER):
        logging.error('chrome-webpage-profiler directory not found, should be %s', TEST_DRIVER)
        return (-3)
    else:
        logging.debug('OK, chrome-webpage-profiler directory found')

    if not os.path.isdir(HAR_CAPTURER):
        logging.error('chrome-har-capturer-cache directory not found, should be %s', HAR_CAPTURER)
        return (-3)
    else:
        logging.debug('OK, chrome-har-capturer-cache directory found')

    if not os.path.isdir(H2_ANALYZER):
        logging.error('http2-dump-anatomy directory not found, should be %s', H2_ANALYZER)
        return (-3)
    else:
        logging.debug('OK, http2-dump-anatomy directory found')

    if not os.path.isdir(PYSHARK):
        logging.error('pyshark-ssl directory not found, should be %s', PYSHARK)
        return (-3)
    else:
        logging.debug('OK, pyshark-ssl directory found')

    if not os.path.isdir(WEBUI):
        logging.error('WEBUI directory not found, should be %s', WEBUI)
        return (-3)
    else:
        logging.debug('OK, WEBUI directory found')

    return (0, packageToInstall, installFirst, cannotInstall)

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,\
                                     description='Chrome webpage profiler suite setup tool')
    parser.add_argument('action', nargs='?', default='install', help='What to do: "install", "upgrade" or "check"')
    parser.add_argument('--no-tshark', action='store_true', default=False, help='Do not compile tshark')
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help='print debug infomation')
    parser.add_argument('-q', '--quiet', action='store_true', default=False, help='print nothing unless errors occur')
    args = parser.parse_args()

    if args.quiet:
        level = logging.ERROR
    elif args.verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logging.basicConfig(
        format = "%(levelname)s:%(message)s",
        level = level
    )

    if args.action == 'install':
        install(args)
    elif args.action == 'upgrade':
        upgrade(args)
    elif args.action == 'check':
        rc = check(args)
        if rc[0] == 0:
            logging.info('OK. Looks Good.')
        else:
            logging.warning('There are problems')
    else:
        logging.critical("Unknown action %s", args.action)

if __name__ == '__main__':
    main()
