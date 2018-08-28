#!/usr/bin/env python
#
#	NOTE: Set tabs = 4 (set ts=4)
#	      See README.TXT for documentation
#
#	Log:
#	01/06/01 -rje-	Initial version
#	04/06/01 -rjw-	Check that the BEGIN and END blocks have been defined before 
#			        executing them.
#	04/06/01 -rjw-	Implemented next()
#	13/06/01 -rjw-	Removed debug
#	14/06/01 -rjw-	Added command line -f and -F options, Updated documentation
#	15/06/01 -rjw-	Added global variable '_' to contain list of fields.
#	16/06/01 -rjw-	RSTART and RLENGTH implemented.
#
import sys, string, re, traceback, types    #, exceptions

#####################################################################
# Exception raised when a next() is encountered

class PyAwkNext(Exception):
	def __init__(self):
		self.args = args

#####################################################################
# pyawk as a function, script and data are files...

def pyawk(Script, Data=None, FS=' ', Decl={}):
	try:
		fd = open(Script, 'r')
		scr = fd.readlines()
		fd.close()
	except:
		print("ERROR: Cannot open script file")
		return []

	try:
		fd = open(Data, 'r')
		dat = fd.readlines()
		fd.close()
	except:
		print("ERROR: Cannot open data file")	
		return  []

	aw = PyAwk(scr, FS, Decl)
	return aw.Run(dat, Data)

###################################################################### 
# Base object, all parameters are lists. 

class PyAwk:
	def __init__(self, Script=None, FS=' ', Decl={}):
		self.Begin  = None
		self.Script = []
		self.End    = None
		# awk vars
		self.Decl   	= Decl		# Pre-declarations, like awk -v
		# Namespaces
		self.LocNs		= {			# execution context local namespace
							'FS': ' ',
						}
		self.GlobNs		= {}		# execution context global namespace
		if Script != None:
			self.ParseScript(Script)

	# ------------------------------------------------------------
	# Call here to run the preloaded script on a liat of data
	def Run(self, Data=[], FileName='-'):
		self.GlobNs['FILENAME'] = FileName
		self.Data = Data
		self.Output = []
		so = sys.stdout
		se = sys.stderr
		sys.stdout = self
		sys.stderr = self
		try:
		#if 1:
			self.ParseData()
		except:
			sys.stdout = so
			sys.stdout = se
			print("ERROR: during parse data")
			traceback.print_exc()
		sys.stdout = so
		sys.stderr = se
		return self.Output

	# Parse each line of the data file, executing a block if the regular
	# expression matches it
	def ParseData(self):
		# calls
		self.GlobNs['getline'] = self.GetLine
		self.GlobNs['next'] = self.Next
		# vars
		self.LocNs['FNR'] = 0
		self.LocNs['_0']  = ''
		self.LocNs['NF']  = 0
		self.LocNs['NR']  = 0
		self.LocNs['RSTART'] = 0
		self.LocNs['RLENGTH'] = -1

		
		# Execute the BEGIN block if there is one
		if self.Begin != None:
			self.DoExec(self.Begin)

		# /.../
		filelen = len(self.Data)
		while self.LocNs['FNR'] < filelen:
			ln = self.Data[self.LocNs['FNR']][:-1]
			self.LocNs['FNR'] += 1
			self.LocNs['NR']  += 1
			self.LocNs['RSTART'] = 0
			self.LocNs['RLENGTH'] = -1
			for s in self.Script:
				m = s[0].search(ln)
				if m != None:
					self.LocNs['RSTART'] = m.start() + 1
					self.LocNs['RLENGTH'] = m.end() - m.start()
					self.PrepLine(ln)
					# If a next() is encountered, DoExec will
					# return 1, so continue with the next line
					ret = self.DoExec(s[1])
					if (ret != None) and (ret == 1):
						break

		# Execute the END block if there is one
		if self.End != None:
			self.DoExec(self.End)

	# Prepare the line form the data file
	def PrepLine(self, Line):
		if Line == None:
			del self.LocNs['_0'] 
		else:
			self.LocNs['_0'] = Line
		if self.LocNs['FS'] == ' ':
			#string.expandtabs(Line, 1)
			Line.expandtabs(1)
		flds = Line.split(self.LocNs['FS'])
		self.LocNs['_'] = flds
		nf = self.LocNs['NF']
		self.LocNs['NF']  = len(flds)
		i = 1
		# set up the fields for this pass
		for f in flds:
			if (self.LocNs['FS'] == ' ') and (f == ''):
					continue
			self.LocNs['_' + str(i)] = f
			i += 1
		self.LocNs['NF'] = i - 1

		# delete any fields from the last pass
		if self.LocNs['NF'] > nf:
			for i in range(self.LocNs['NF']+1,nf):
				exec('del self.LocNs["_%d"]' % (i, f))

	# execute the code block on a line that has been matched.
	# A PyAwkNext exception causes processing of the current line to
	# be abandoned and resumed with the next line
	def DoExec(self, codeobj):
		try:
			exec(codeobj, self.GlobNs, self.LocNs)
			return 0
		except PyAwkNext as e:
			return 1
		except Exception as e:

			print(traceback.print_exc())
			print("EError: Executing code object: %s (%s)" % (codeobj, str(e)))

	# ------------------------------------------------------------
	# Get the next line from the data array
	def GetLine(self, param=None):
		if param == None:
			# Get next input line, setting NF, NR, FNR
			ln = self.Data[self.LocNs['FNR']][:-1]
			self.LocNs['FNR'] += 1
			self.LocNs['NR']  += 1
			self.PrepLine(ln)
		elif hasattr(param, 'read'):
			self.PrepLine(param.readline()[:-1])
		elif isinstance(param, str):
			self.PrepLine(param)
		else:
			print("ERROR: getline param error")

	# ------------------------------------------------------------
	def ParseScript(self, Script):
		BlockNo = 0
		block   = []
		for l in Script:
			l.strip()
			l = l[:-1]
			if len(l) == 0:
				continue
			if l[0] == '#':
				continue
			block.append(l+'\n')
			if l == '}':
				BlockNo += 1
				self.ParseBlock(block, BlockNo)
				block =[] 

		return []

	def ParseBlock(self, Block, BlockNo):
		# The first line should be: 
		#		/<regexp>/ {
		#or 	BEGIN {
		#or 	END {
		BlockRex = ''
		if Block[0][0] == '/':
			try:
				e = Block[0].index("/", 1, -1)
			except:
				print("ERROR Block %s: unterminated regular expression: %s (%s)" % (BlockNo, Block[0], str(e)))
				return
			BlockRex = Block[0][0:e+1]
			Rex = self.MakeRegexp(Block[0][1:e])
			try:
				Code = self.CompileCode(Block[1:-1], BlockRex)
				self.Script.append([Rex, Code])
			except Exception as e:
				print("Compile error in Block %s: code error: %s (%s)" % (BlockNo, Block[0], str(e)))
		elif Block[0][0:5] == 'BEGIN':
			BlockRex = 'BEGIN'
			self.Begin = self.CompileCode(Block[1:-1], BlockRex)
		elif Block[0][0:3] == 'END':
			BlockRex = 'END'
			self.End = self.CompileCode(Block[1:-1], BlockRex)
		else:
			print("ERROR: incorrect regular expression: %s" % (Block[0]))

	def CompileCode(self, Code, BlockNo):
		codestr = ''
		for l in Code:
			codestr += l
		try:
			codeobj = compile(codestr, 'Block %s' % BlockNo, 'exec')
		except Exception as e:
			print("ERROR: compiling %s (%s)" % (codestr, str(e)))
			return None

		return codeobj

	def MakeRegexp(self, Exp):
		return re.compile(Exp)

	# ------------------------------------------------------------
	def write(self, Str):
		self.Output.append(Str)

	def Next(self):
		raise PyAwkNext
		
#
# Emulate the original awk command line where possible
#
if __name__ == '__main__':
	global verbose, args
	import getopt
	
	opts, args = getopt.getopt(sys.argv[1:], 'f:F:')
	script = None
	separator = ' '
	for o in opts:
		if   o[0] == '-f': script    = o[1]
		elif o[0] == '-F': separator = o[1]
		elif o[0] == '-v': verbose = True

	res = pyawk(script, args[0], separator)

	for l in res:
		print(l, end='')
	
