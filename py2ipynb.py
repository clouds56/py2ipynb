
# coding: utf-8

# # py2ipynb
# 

# In[ ]:

import nbformat
from nbconvert import export_python

def clean_cell(cell):
    if cell["cell_type"] == "code":
        del cell["execution_count"]
    if cell["cell_type"] == "markdown":
        if isinstance(cell["source"], str) and (len(cell["source"])==0 or cell["source"][-1]!='\n'):
            cell["source"] += "\n"
    return cell

def convert_to(in_name):
    nb0 = nbformat.read(in_name, as_version=4)
    for x in nb0["cells"]:
        clean_cell(x)

    (a0, _) = export_python(nb0)

    return a0


# This script will convert python file to ipynb
# 
# ...
# 

# In[ ]:

import os
from base64 import encodestring

from nbformat.v4.nbbase import (
    new_code_cell, new_markdown_cell, new_notebook,
    new_output, new_raw_cell
)


# In[ ]:

import re

def lexer(token_expr):
    token_expr = [(name, re.compile(regex)) for name, regex in token_expr]
    def lx(t):
        for name, regex in token_expr:
            m = re.match(regex, t)
            if m is not None:
                g = m.groups()
                return (name, m.groups())
        return None
    return lx


# In[ ]:

token_expr = (
    ("NEWLINE",      r"^\n"),
    ("COMMENT_HEAD", r"^# coding: utf-8\n"),
    ("COMMENT_IN",   r"^# In\[( |\d+)\]:\n"),
    ("COMMENT_MD",   r"^# (.*)\n"),
    ("CODE",         r"^(.*)\n"),
)

lx = lexer(token_expr)


# In[ ]:

import regex
def short_parse():
    dx = {"NEWLINE":" ", "COMMENT_HEAD":"H", "COMMENT_MD":"M", "CODE":"O", "COMMENT_IN":"I"}
    st = "".join([dx[x] for x,y in t])
    r = r" H (M+ |I [OM ]+?  )*"
    m = regex.match(r, st+" ")
    m, m.captures(1)


# In[ ]:

class CompileError():
    pass

class ParseElement():
    def __add__(self, b):
        if not isinstance(b, ParseElement):
            raise CompileError()
        return PAnd(self, b)

    def __or__(self, b):
        if not isinstance(b, ParseElement):
            raise CompileError()
        return POr(self, b)

class ParseExpression(ParseElement):
    pass

class PAnd(ParseExpression):
    def __init__(self, a, b):
        if not isinstance(a, ParseElement) or not isinstance(b, ParseElement):
            raise CompileError()
        if isinstance(a, PAnd):
            self.q = [*a.q, b]
        elif isinstance(b, PAnd):
            self.q = [a, *b.q]
        else:
            self.q = [a, b]
    
    def __str__(self):
        return "%s" % ("".join([str(x) for x in self.q]))
    
    def parse(self, t):
        its, tx = [], t
        for x in self.q:
            i, tx = x.parse(tx)
            if i is None:
                return None, t
            its += i
        return its, tx

class POr(ParseExpression):
    def __init__(self, a, b):
        if not isinstance(a, ParseElement) or not isinstance(b, ParseElement):
            raise CompileError()
        if isinstance(a, POr):
            self.q = [*a.q, b]
        elif isinstance(b, POr):
            self.q = [a, *b.q]
        else:
            self.q = [a, b]
    
    def __str__(self):
        return "%s" % ("|".join([str(x) for x in self.q]))
    
    def parse(self, t):
        for x in self.q:
            i, tx = x.parse(t)
            if i is not None:
                return i, tx
        return None, t

class ZeroOrMore(ParseExpression):
    def __init__(self, a, greedy = True):
        if not isinstance(a, ParseElement):
            raise CompileError()
        if isinstance(a, ZeroOrMore):
            self.a = a.a
        else:
            self.a = a
        self.greedy = greedy

    def __str__(self):
        return "(%s)*%s" % (self.a, not self.greedy and "?" or "")
    
    def parse(self, t):
        its, tx = [], t
        while True:
            i, tx = self.a.parse(tx)
            if i is None:
                break
            its += i
        return its, tx

class OneOrMore(ParseExpression):
    def __init__(self, a, greedy = True):
        if not isinstance(a, ParseElement):
            raise CompileError()
        if isinstance(a, OneOrMore):
            self.a = a.a
        else:
            self.a = PAnd(a, ZeroOrMore(a, greedy=greedy))
    
    def __str__(self):
        return "%s" % self.a
    
    def parse(self, t):
        return self.a.parse(t)

class PToken(ParseElement):
    def __init__(self, s):
        self.s = s
    
    def __str__(self):
        return r'~\d+\.%s' % self.s
    
    def isequal(self, x):
        return x[0] == self.s
    
    def parse(self, t):
        if self.isequal(t[0]):
            return [t[0]], t[1:]
        return None, t

class PSuppress(ParseElement):
    def __init__(self, a):
        if not isinstance(a, ParseElement):
            raise CompileError()
        self.a = a
    
    def __str__(self):
        return "%s" % self.a
    
    def parse(self, t):
        i, t = self.a.parse(t)
        if i is None:
            return i, t
        else:
            return [], t

class PCapture(ParseElement):
    def __init__(self, a):
        if not isinstance(a, ParseElement):
            raise CompileError()
        self.a = a
    
    def __str__(self):
        return "(%s)" % self.a
    
    def parse(self, t):
        return self.a.parse(t)


# In[ ]:

newline = PSuppress(PToken("NEWLINE"))
comment_head = PToken("COMMENT_HEAD")
comment_in = PToken("COMMENT_IN")
comment_md = PToken("COMMENT_MD")
code = PToken("CODE")
head = newline + comment_head + newline
md = OneOrMore(comment_md) + newline
code_block = ZeroOrMore(PToken("NEWLINE") | code | comment_md, greedy = False)
code = comment_in + newline + code_block + newline + newline
cell = md | code
article = PCapture(head) + ZeroOrMore(cell)
str(article)


# In[ ]:

def parse(t):
    s = "~".join(["", *["%d.%s" % (x,y[0]) for x,y in enumerate(t)], "0.NEWLINE"])
    p = regex.match(str(article), s)
    return p

def parse_zip(t, p):
    def z(t, i):
        ii = int(i.split(".")[0])
        return (ii, t[ii])
    tp = [[z(t, i) for i in x.strip("~").split("~")] if isinstance(x, str) else parse_zip(t, x) for x in p]
    return tp


# In[ ]:

def build_ast(tp):
    a = []
    for cell in tp:
        ct, cc = cell[0][1][0], []
        for i in cell:
            it = i[1][0]
            if it == "CODE":
                cc.append(i[1][1][0])
            elif it == "NEWLINE":
                if cc:
                    cc.append("")
            elif it == "COMMENT_MD":
                if ct == it:
                    cc.append(i[1][1][0])
                else:
                    cc.append("# " +  i[1][1][0])
        while len(cc)>0 and cc[-1] == "":
            cc.pop()
        a.append((ct, cc))
    return a


# In[ ]:

def normalize_cell(ct, cc):
    cc_n = [x if len(x)>0 and x[-1]=='\n' else x+"\n" for x in cc]
    if len(cc_n) > 0:
        cc_n[-1].strip("\n")
    if ct == "COMMENT_IN":
        return new_code_cell(cc_n)
    if ct == "COMMENT_MD":
        return new_markdown_cell(cc_n)
    return new_raw_cell(cc_n)


# In[ ]:

import nbformat

def convert_from(in_name):
    with open(in_name) as f:
        a = f.readlines()
    t = [lx(x) for x in a]

    p = parse(t)
    tp = parse_zip(t, p.captures(2))
    ast = build_ast(tp)

    cells = [normalize_cell(ct,cc) for ct,cc in ast]
    nb0 = new_notebook(cells=cells, metadata={'language': 'python',})
    return nb0


# In[ ]:

import sys
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <filename.ipynb|filename.py>")
    else:
        fn = sys.argv[1]
        if fn.endswith(".ipynb"):
            print(convert_to(fn))
        elif fn.endswith(".py"):
            nbformat.write(convert_from(fn), sys.stdout, 4)


# In[ ]:

sys.exit()


# In[ ]:

with open("py2ipynb.py", "w") as f:
    f.write(convert_to("py2ipynb.ipynb"))

