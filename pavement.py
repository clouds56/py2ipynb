from paver.easy import *

src = path("src")
bin = path("bin")
test_dir = path("test")
basename = "py2ipynb"
exehead = "#!/usr/bin/python"

def makesuredir(*args):
    for dir in args:
        if not dir.exists():
            dir.mkdir()

def check(input, output):
    if not path(output).exists() or path(input).mtime > path(output).mtime:
        return True
    info('%s is latest' % output)
    return False

def decompile(input, output, pipe=False):
    if check(input, output):
        if not pipe:
            sh([bin / basename, "-t", "--strip", "-o", output, "-i", input, "--verb"])
        else:
            sh("cat '%s' | '%s' --to --verbose > '%s'" % (input, bin/basename, output))

def compile(input, output, pipe=False):
    if check(input, output):
        if not pipe:
            sh([bin / basename, "-f", input, "-o", output, "--verb"])
        else:
            sh("cat '%s' | '%s' --from --verbose > '%s'" % (input, bin/basename, output))

@task
def build():
    """build bin/py2ipynb.py"""
    makesuredir(bin)
    compile(src / ("%s.ipynb" % basename), bin / ("%s.py" % basename))

@task
def test():
    """test compile(decompile(bin/py2ipynb.py)) is fixed"""
    makesuredir(bin, test_dir)
    test_in = bin / ("%s.py" % basename)
    test_out = test_dir / ("%s.ipynb" % basename)
    test_in2 = test_dir / ("%s.py" % basename)
    decompile(test_in, test_out, pipe=True)
    compile(test_out, test_in2, pipe=True)
    sh(["diff", "-u", test_in, test_in2])

class Lines(list):
    def __repr__(self):
        return "<%d lines>" % len(self)

@task
@needs("build")
def install():
    """install executable file bin/py2ipynb"""
    makesuredir(bin)
    exefile = bin / basename
    lines = Lines((bin / ("%s.py" % basename)).lines())
    lines[0] = exehead
    exefile.write_lines(lines, linesep='\n')
    sh("chmod +x '%s'" % exefile)

@task
@needs("install", "test")
def all():
    pass

@task
def hook():
    """hoot git config"""
    exefile = bin / basename
    sh([exefile, "--hook", exefile, "--verbose"])

@task
def unhook():
    """remove git config"""
    exefile = bin / basename
    sh([exefile, "--unhook", "--verbose"])
