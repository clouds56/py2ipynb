from paver.easy import *

basename = "py2ipynb"

def compile(input, output):
    if not path(output).exists() or path(input).mtime > path(output).mtime:
        sh(["./py2ipynb", input, "-o", output, "--verb"])
    else:
        info('%s is latest' % output)

@task
def build():
    compile("%s.ipynb" % basename, "%s.py" % basename)

@task
@needs("build")
def install():
    sh("echo '#!/usr/bin/python' > '%s'" % basename)
    sh("cat '{0}.py' >> '{0}'".format(basename))
    sh("chmod +x '%s'" % basename)
