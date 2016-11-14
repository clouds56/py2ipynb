from paver.easy import *

src = path("src")
bin = path("bin")
basename = "py2ipynb"
exehead = "#!/usr/bin/python"

def makesure_bin():
    if not bin.exists():
        bin.mkdir()

def check(input, output):
    if not path(output).exists() or path(input).mtime > path(output).mtime:
        return True
    info('%s is latest' % output)
    return False

def decompile(input, output):
    if check(input, output):
        sh([bin / basename, "-t", "--strip", "-o", output, "-i", input, "--verb"])

def compile(input, output):
    if check(input, output):
        sh([bin / basename, "-f", input, "-o", output, "--verb"])

@task
def build():
    makesure_bin()
    compile(src / ("%s.ipynb" % basename), bin / ("%s.py" % basename))

@task
def test():
    makesure_bin()
    test_in = bin / ("%s.py" % basename)
    test_out = bin / ("%s.ipynb" % basename)
    test_in2 = bin / ("%s-new.py" % basename)
    decompile(test_in, test_out)
    compile(test_out, test_in2)
    sh(["diff", "-u", test_in, test_in2])

class Lines(list):
    def __repr__(self):
        return "<%d lines>" % len(self)

@task
@needs("build")
def install():
    makesure_bin()
    exefile = bin / basename
    lines = Lines((bin / ("%s.py" % basename)).lines())
    lines[0] = exehead
    exefile.write_lines(lines, linesep='\n')
    sh("chmod +x '%s'" % exefile)
