import os
import subprocess
import sys

def_log = '.git/logs/HEAD'
branch_log = '.git/logs/refs/heads/%s'

commit_str = 'commit'
reset_str = 'reset'
checkout_str = 'checkout'

GIT_LOG_FIELDS = ["%h", "%an", "%s"]

DEBUG = False


def cmd(cmd_str):
    cmd_str = cmd_str.replace('*', '\*')
    if DEBUG:
        print cmd_str
    # raw_input('waiting to run command')
    pipe = subprocess.Popen(cmd_str, shell=True, cwd=os.getcwd(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, error = pipe.communicate()
    if error:
        print 'error'
        print error
    pipe.wait()
    return out

class LogEvent(object):

    def __init__(self, parent, hash, type, message):
        self.parent_hash = parent
        self.hash = hash
        self.type = type
        self.message = message.replace('\n', '')

    def __str__(self):
        return "%-16s %s" % (self.type, self.message)

class Git(object):
    cmds = {}

    @classmethod
    def _assign_cmds(cls):
        cls.stg = cls.stage
        cls.ustg = cls.unstage
        for value in dir(Git).__iter__():
            if value.startswith('_'):
                continue
            cmd = cls.__dict__[value]
            if callable(cmd):
                cls.cmds[value] = cmd

    def _parse_log(self, branch):
        '''
        if branch == '' or branch == 'HEAD':
            path = def_log
        else:
            path = branch_log % branch
        events = []
        with file(path, 'r') as log:
            for line in log.readlines():
                info, event = line.split("\t")
                infos = info.split(' ')
                event_infos = event.split(': ')
                log = LogEvent(infos[0], infos[1], event_infos[0], event_infos[1])
                events.append(log)
        events.reverse()
        return events'''
        git_log_input_format = '\x1f'.join(GIT_LOG_FIELDS) + '\x1e'
        log = cmd('git log %s --format="%s"' % (branch, git_log_input_format,) )
        log = log.strip('\n\x1e').split("\x1e")
        return log


    def _get_hash(self, branch, commit_nu):
        branch = self._interpret_commit(branch)
        hash = self._parse_log(branch)[commit_nu].hash
        return hash

    def _get_current_refs(self):
        pass

    def _interpret_commit(self, raw):
        if raw == 'stage':
            return '--cached'
        elif raw == 'remote':
            return 'HEAD'
        elif raw == 'local':
            return ''
        elif ':' in raw:
            vals = raw.split(':')
            print 'i got the :"s'
            return self._get_hash(vals[0], int(vals[1], 10))
        else:
            try:
                num = int(raw, 10)
            except ValueError:
                return raw
            hash = self._get_hash('HEAD', num)
            return hash

    def _get_curr_branch(self):
        return cmd("git rev-parse --symbolic --abbrev-ref $(git symbolic-ref HEAD)").strip('\n')


    def __init__(self):
        """
        this creates all the systems functions. It will just match string to their python function name
        """
        self.self = self
        Git._assign_cmds()

    def commit(self, params):
        cmd('git commit -m "%s"' % " ".join(params[0:]))

    def uncommit(self, params):
        if len(params) > 0:
            num = int(params[0])
        else:
            num = 1
        if num == 0:
            print 'waaaa??'
            return
        times = '^'*num
        cmd('git reset HEAD%s' % times)

    def create(self, params):
        cmd('git init')

    def stage(self, params):
        files = ' '.join(params)
        cmd('git add ' + files)

    def unstage(self, params):
        files = ' '.join(params)
        cmd('git reset '+files)

    def status(self, params):
        cmd('git status')

    def history(self, params):
        if len(params)> 0:
            branch = params[0]
        else:
            branch = self._get_curr_branch()
        logs = self._parse_log(branch)
        for num, log in enumerate(logs):
            print "%-2s %s" % (num, log)


    def diff(self, params):
        """
            got diff stage remote # compares stage to whats been pushed
            git diff --cached
            got diff local stage # compares local to stage
            got diff local remote # compares local to whats been pushed
            git diff HEAD
            got diff # equivalent to got diff local stage
        """
        if len(params) == 0:
            this = ''
            that = ''
        elif len(params) == 2:
            this = params[0]
            that = params[1]
        else:
            print 'waaaaa'
            sys.exit(1)
        this = self._interpret_commit(this)
        that = self._interpret_commit(that)

        cmd('git diff %s %s' % (this, that))


if __name__ == '__main__':
    index = 1
    git = Git()
    # print Git.__mro__
    if DEBUG:
        print sys.argv
    try:
        func = git.cmds[sys.argv[index]]
        func(git, sys.argv[index+1:])
    except KeyError:
        print 'unknown command %s' % sys.argv[index]
        sys.exit(1)
    except IndexError:
        print 'commands ' + ', '.join(git.cmds.keys())


# todo get the colors back
# todo run less on python output

# todo history should only show checkout on history long
# todo branch and commit defaults should be relative to commit
# todo handle wildcards correctly
# todo commit resilient to " and '
# todo checkout/ get file better
# todo rename working, stage, local, remote
# todo megre commits
# todo get a list of how versions looked in the past
# todo sqashing commits
# gat add should do add all the file you are tracking (including deltes)
# gat wipe everything to the previous version. wipe head cleans everything, 
#wipe file removes stores, wipe 

''' hash, auther msg'''
GIT_LOG_FIELDS = ["%h", "%an", "%s"]
git_log_input_format = '%x1f'.join(GIT_LOG_FIELDS) + '%x1e'

"""
GIT_DIR_="$(git rev-parse --git-dir)"
BRANCH="$()"

git stash save " aldkfjasdlfj"
git stash apply stash^{/ aldkfjasdlfj} <- or regular expression
"""

# git config --global core.excludesfile '~/.gitignore'
# git config --global push.default upstream

