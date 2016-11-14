from paver.easy import *

src = path("src")
bin = path("bin")
basename = "py2ipynb"
exehead = "#!/usr/bin/python"

def makesure_bin():
    if not bin.exists():
        bin.mkdir()

def compile(input, output):
    makesure_bin()
    if not path(output).exists() or path(input).mtime > path(output).mtime:
        sh([bin / basename, input, "-o", output, "--verb"])
    else:
        info('%s is latest' % output)

@task
def build():
    compile(src / "%s.ipynb" % basename, bin / "%s.py" % basename)

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
