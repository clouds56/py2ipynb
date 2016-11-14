from paver.easy import *

basename = "py2ipynb"

@task
def build():
    sh(["./py2ipynb", "%s.ipynb" % basename, "-o", "%s.py" % basename, "--verb"])

@task
def install():
    sh("echo '#!/usr/bin/python' > '%s'" % basename)
    sh("cat '{0}.py' >> '{0}'".format(basename))
    sh("chmod +x '%s'" % basename)
