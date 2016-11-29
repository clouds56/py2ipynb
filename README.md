Usage
=====

	usage: py2ipynb [-h] [--hook HOOK | --unhook] [-f | -t] [-o [OUTPUT]]
					[-i INPUT] [--no-strip | --strip] [--verbose]
					[input]

	Convert from py file to ipynb file.

	positional arguments:
	  input                 ipynb or py file

	optional arguments:
	  -h, --help            show this help message and exit
	  --hook HOOK           hook git inplace
	  --unhook              unhook git inplace
	  -f, --from            from ipynb to py
	  -t, --to              from py to ipynb
	  -o [OUTPUT], --output [OUTPUT]
							output filename, if not specific
							<file_basename.py(from)|file_basename.ipynb(to)> will
							be used, if not present will output to stdout
	  -i INPUT, --input INPUT
							input filename
	  --no-strip            whether strip trailing space in code cell
	  --strip               defaut is True
	  --verbose             print verbose information

Steps
=====
0. install `py2ipynb` to your path
1. inside a git repo run `py2ipynb --hook py2ipynb` to add **ipynb** filter in git config
2. add all .ipynb files with filter **ipynb** using `echo "*.ipynb filter=ipynb" >> .gitattributes`
3. now you are all set, all your .ipynb file would be convert into .py file when commit, enjoy yourself
