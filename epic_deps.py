"""
Unificar la instalación de dependencias (pip_reqs.txt) en los diferentes servidores: 
- Si es local el archivo '.env' tiene variables relevantes. 
- Si es Databricks, el archivo 'user_databricks.json' vincula con el llavero correspondiente.

En cualquier caso se confirma un token de github: GH_ACCESS_TOKEN. 
"""
# pylint: disable=import-error
# pylint: disable=import-outside-toplevel
# pylint: disable=possibly-used-before-assignment
# pylint: disable=unspecified-encoding

from argparse import ArgumentParser
import os
from pathlib import Path
import re
from subprocess import check_call, CalledProcessError
from sys import argv
from warnings import warn

from config import EPIC_REF, REQS_FILE

TOKEN_VAR = "GH_ACCESS_TOKEN" 
EPIC_URL = "Bineo2/data-python-tools"
BASE_AT = Path(__file__).parent

REG_ENV = r"\$\{([A-Z_]*)\}"
REG_SCT = r"([A-Z_]*)\s*?=\s?\"?([^\s\=]*)\"?"
REG_CMT = r"#.*$"


def dotenv_manual(env_file=None):
    env_file = env_file or '.env'
    rm_comment = lambda ss: re.sub(REG_CMT, '', ss).strip()
    with open(env_file, 'r') as _f: 
        tier_0 = _f.readlines()
    tier_1 = map(rm_comment, tier_0)
    the_secrets = {mm.group(1): mm.group(2)
        for ll in tier_1 if (mm := re.match(REG_SCT, ll))}         
    os.environ.update(the_secrets)
        


def token_from_server(force=False):
    if (TOKEN_VAR in os.environ) and (not force): 
        warn(f"Access token already stored in {TOKEN_VAR}")   
    if Path(BASE_AT/'.env').is_file(): 
        dotenv_manual(BASE_AT/'.env')
    else: 
        raise EnvironmentError("Cannot set Github token to install from Github.")


def parse_reqsfile(a_file, no_envs=False):
    rm_comment = lambda ss: re.sub(REG_CMT, '', ss).strip()
    not_blank = lambda ss: ss.strip() != ""
    def with_out_env(line): 
        has_env = re.search(REG_ENV, line)
        if not has_env:
            return line
        with_env = "" if no_envs else os.path.expandvars(line)
        return with_env
        
    with open(a_file, 'r') as _f: 
        tier_0 = _f.readlines()
    tier_1 = map(rm_comment, tier_0)
    tier_2 = map(with_out_env, tier_1) 
    tier_3 = filter(not_blank, tier_2)
    return list(tier_3)


def install_reqs(r_file=None, no_envs=False):
    r_file = r_file or REQS_FILE 
    pipers = parse_reqsfile(BASE_AT/r_file, no_envs)
    try: 
        check_call(["pip", "install", *pipers])
    except CalledProcessError as _: 
        stringed = ' '.join(pipers)
        print(f"Error when installing Reqs with command:\n$> pip install {stringed}")
    

def install_epicpy(ref=None, method=None, **kwargs): 
    ref = ref or EPIC_REF
    method = method or 'https'
    token = os.environ[TOKEN_VAR]
    
    if method == 'https': 
        the_url = f"git+https://{token}@github.com/{EPIC_URL}@{ref}"
    elif method == 'ssh': 
        if 'host' not in kwargs: 
            warn("May need to provide SSH Host from ~/.ssh/config")
        host = kwargs.get('host', 'github.com')
        the_url = f"git+ssh://{host}/{EPIC_URL}@{ref}"
    check_call(["pip", "install", the_url])


def create_parser(): 
    parser = ArgumentParser('epic_dependencies', 
        "Install dependencies with pip, useful for local and Databricks vanilla environments.")
    subbers = parser.add_subparsers(dest='installee', 
        help='Dependencies options to install')

    req_parser = subbers.add_parser('reqs', 
        help="In order to install requirement file")
    req_parser.add_argument('-r', '--requirement', default=REQS_FILE, 
        help="The requirement file as in PIP.")
    req_parser.add_argument('--no-envs', action='store_true')
    req_parser.set_defaults(func=install_reqs, 
        pargs=('requirement', 'no_envs'), kwargs=())

    epic_parser = subbers.add_parser('epic_py', 
        help='In order to install epic_py')
    epic_parser.add_argument('-r', '--ref', default=EPIC_REF, 
        help="The branch, tag or reference to install from Github.")
    epic_parser.add_argument('-m', '--method', choices=['https','ssh'], default='https', 
        help="How to connect to Github for epic-py install.")
    epic_parser.add_argument('--host', required=('ssh' in argv), 
        help="The host to use from ~/.ssh/config")
    epic_parser.set_defaults(
        func=install_epicpy, pargs=('ref', 'method'), kwargs=('host',))
    return parser


if __name__ == '__main__':
    deps_parser = create_parser()
    args = deps_parser.parse_args()
    
    token_from_server()
    
    positional = [getattr(args, pp) for pp in args.pargs]  
    kwords = {kk: getattr(args, kk) for kk in args.kwargs}
    args.func(*positional, **kwords)
