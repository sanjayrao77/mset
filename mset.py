#!/usr/bin/python3 -B

#  * github.com/sanjayrao77
#  * mset.py - text processor using group membership
#  * Copyright (C) 2024 Sanjay Rao
#  *
#  * This program is free software; you can redistribute it and/or modify
#  * it under the terms of the GNU General Public License as published by
#  * the Free Software Foundation; either version 2 of the License, or
#  * (at your option) any later version.
#  *
#  * This program is distributed in the hope that it will be useful,
#  * but WITHOUT ANY WARRANTY; without even the implied warranty of
#  * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  * GNU General Public License for more details.
#  *
#  * You should have received a copy of the GNU General Public License
#  * along with this program; if not, write to the Free Software
#  * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import sys
from fractions import Fraction
from decimal import Decimal

isdebug_global=False

allcommands_global={'join','variable','map','unmap''global0','globalint','globalstring',
		'name','include','suppress','unsuppress','adopt','set','setstring','unset','sum','printvar','assert'}

def errorout(desc):
	if isdebug_global: raise Exception('Error: %s'%desc)
	print('Error: %s'%desc)
	exit(-1)
def node_errorout(node,desc):
	if not node: errorout(desc)
	if isdebug_global: raise Exception('Error in node: %s, node: %s'%(desc,node.orig_lines))
	print('Error: (%s), in node: %s'%(desc,node.orig_lines))
	exit(-1)

class GlobalVars():
	def __init__(self):
		self.vars={}
	def clone(self):
		gv=GlobalVars()
		gv.vars.update(self.vars)
		return gv
	def istrue(self,n):
		if not n in self.vars: return False
		v=self.vars[n]
		if not v: return False
		return True
	def setvarint(self,a,b=None,c=None):
		if b==None: self.vars[a]=Fraction(0)
		elif c==None: self.vars[a]=Fraction(Decimal(b))
		else: self.vars[a]=Fraction(int(b),int(c))
	def setvar(self,a,b):
		self.vars[a]=b
	def setvarparse(self,arg):
		j=arg.find('=')
		if j<0:
			self.setvarint(arg.strip(),1)
			return
		name=arg[:j].strip()
		val=arg[j+1:].strip()
		if val=='': self.setvarint(name) # 0
		else: self.setvar(name,val)
	def getstring(self,name,default=None):
		if name not in self.vars: return default
		v=self.vars[name]
		if isinstance(v,str): return v
		if isinstance(v,Fraction):
			nd=v.as_integer_ratio()
			if nd[1]==1: return '%s'%nd[0]
			return '%.2f'%float(v)
		errorout('Globalvars: name "%s" has unknown type "%s"'%(name,type(v)))

class Phase0():
	class Chunk():
		def __init__(self,words,lines):
			self.isactive=True
			self.words=words
			self.requires=[]
			self.globalcmds=[]
			self.names=[] # only used for inclusion checks
			self.lines=lines
			for w in words:
				if w.startswith('.?'):
					if w in ('.?','.?+','.?-'): errorout('Empty conditional: %s in %s'%(w,lines))
					self.requires.append(w)
				elif w.startswith('._global'): self.globalcmds.append(w)
				elif w.startswith('._name('): self.names.append(w[8:-1].trim())
				elif w.startswith('.='): self.names.append(w[2:])
	
	def finddotlength(l_in): # assumes l starts with .
		if len(l_in)==1: return 1
		if l_in[1]=='#': return len(l_in)
		ret=1
		l=l_in[1:]
		pcount=0
		while True:
			if not l:
				if pcount: raise ValueError("Unmatch parenthesis in %s",l_in)
				return ret
			c=l[0]
			if not pcount:
				if c in (' ','\t','\\'): return ret
			if c=='\\':
				if l[1] in ('(',')',):
					ret+=2
					l=l[2:]
			elif c=='(': pcount+=1
			elif c==')': pcount-=1
			ret+=1
			l=l[1:]

	def findwordlength(l):
		for i,c in enumerate(l):
			if c==' ' or c=='\t': return i
		return len(l)

	def parseline(l):
		dest=[]
		inescape=False
		while True:
			if not l: break
			c=l[0]
			if c==' ' or c=='\t':
				l=l[1:]
				inescape=False
				continue
			if c=='.':
				j=Phase0.finddotlength(l)
				w=l[:j]
				if w=='.': dest.append('.')
				elif w[1]=='#': break # ignore rest of line
				else: dest.append(w)
				l=l[j+1:]
				continue
			if c=='\\':
				if l.startswith('\\\\') or l.startswith('\\.'): 
					j=Phase0.findwordlength(l)
					dest.append(l[:j])
					l=l[j+1:]
					continue
				inescape=True
				l=l[1:]
				if l.startswith('n'): dest.append('\\n') ; l=l[1:]
				elif l.startswith('space'): dest.append('\\space') ; l=l[5:]
				elif l.startswith('s'): dest.append('\\space') ; l=l[1:]
				elif l.startswith('tab'): dest.append('\\t') ; l=l[3:]
				elif l.startswith('t'): dest.append('\\t') ; l=l[1:]
				elif l.startswith('bs'): dest.append('\\backspace') ; l=l[2:]
				elif l.startswith('backspace'): dest.append('\\backspace') ; l=l[9:]
				elif l.startswith('br'): dest.append('\\br') ; l=l[2:]
				elif l.startswith('bold'): dest.append('\\bold') ; l=l[4:]
				elif l.startswith('b'): dest.append('\\bold') ; l=l[1:]
				elif l.startswith('Bold'): dest.append('\\Bold') ; l=l[4:]
				elif l.startswith('B'): dest.append('\\Bold') ; l=l[1:]
				elif l.startswith('italic'): dest.append('\\italic') ; l=l[6:]
				elif l.startswith('i'): dest.append('\\italic') ; l=l[1:]
				elif l.startswith('Italic'): dest.append('\\Italic') ; l=l[6:]
				elif l.startswith('I'): dest.append('\\Italic') ; l=l[1:]
				elif l.startswith('paragraph'): dest.append('\\paragraph') ; l=l[9:]
				elif l.startswith('p'): dest.append('\\paragraph') ; l=l[1:]
				elif l.startswith('Paragraph'): dest.append('\\Paragraph') ; l=l[9:]
				elif l.startswith('P'): dest.append('\\Paragraph') ; l=l[1:]
				elif l.startswith('underline'): dest.append('\\underline') ; l=l[9:]
				elif l.startswith('u'): dest.append('\\underline') ; l=l[1:]
				elif l.startswith('Underline'): dest.append('\\Underline') ; l=l[9:]
				elif l.startswith('U'): dest.append('\\Underline') ; l=l[1:]
				continue
			if inescape:
				for i,c in enumerate(l):
					if c=='\\':
						dest.append(l[:i])
						l=l[i:]
						break
					if c==' ' or c=='\t':
						inescape=False
						dest.append(l[:i])
						l=l[i:]
						break
				else:
					dest.append(l)
					break
				continue

			j=Phase0.findwordlength(l)
			dest.append(l[:j])
			l=l[j+1:]
		return dest

	def __init__(self):
		self.chunks=[]
		self.globalvars=GlobalVars()
	def dump(self):
		for chunk in self.chunks:
			print("Chunk: %s"%(chunk.isactive))
			for i,c in enumerate(chunk.words):
				print('%s: %s'%(i,c))
	def setvarcmd(self,text):
		if text[-1]!=')': raise ValueError("bad close: %s"%text)
		if text.startswith('._global0('):
			param=text[10:-1].strip()
			self.globalvars.setvar(param,0)
		elif text.startswith('._globalint('): 
			params=text[12:-1]
			a=params.split(',')
			if len(a)>3: raise ValueError("Too many arguments: %s"%text)
			for i,b in enumerate(a): a[i]=b.strip()
			self.globalvars.setvarint(*a)
		elif text.startswith('._globalstring('): 
			param=text[15:-1]
			j=param.find(',')
			if j<0: raise ValueError("Too few arguments: %s"%text)
			name=param[:j].strip()
			value=param[j+1:].strip()
			self.globalvars.setvar(name,value)
		else: raise ValueError("bad line: %s"%text)
	def addfile(self,fn):
		f=open(fn) if isinstance(fn,str) else fn
		words=[]
		lines=[]
		while True:
			l=f.readline()
			if not l: break
			if l[-1]!='\n': raise ValueError("unexpected eol")
			l=l[:-1]
			if l and l[-1]=='\r': l=l[:-1]
			if not l:
				if words:
					self.chunks.append(Phase0.Chunk(words,lines))
					words=[]
					lines=[]
				continue
			if not words and l.startswith(('. ','.\t')):
				l=l[2:]
				words=Phase0.parseline(l)
				if words:
					self.chunks.append(Phase0.Chunk(words,[l]))
					words=[]
				continue
			dest=Phase0.parseline(l)
			if dest:
				words.extend(dest)
				lines.append(l)
		if words:
			self.chunks.append(Phase0.Chunk(words,lines))
	def collectvars(self): # we first set vars from chunks with no requirements
		gvv=self.globalvars.vars
		for chunk in self.chunks:
			if not chunk.isactive: continue
			for name in chunk.names:
				val=gvv.get(name,1)
				if val==0:
					chunk.isactive=False
					break
			else:
				if chunk.requires: continue
				for w in chunk.globalcmds:
					self.setvarcmd(w)
	def process(self):
		gvv=self.globalvars.vars
		for chunk in self.chunks:
			if not chunk.isactive: continue
			for name in chunk.names:
				val=gvv.get(name,1)
				if val==0:
					chunk.isactive=False
					break
			else:
				if not chunk.requires: continue # these are set in .collectvars
				for word in chunk.requires:
					req=word[2:]
					if req[0]=='-': # .?-
						req=req[1:]
						if self.globalvars.istrue(req):
							chunk.isactive=False
							break
					else: # .? or .?+
						if req[0]=='+': req=req[1:] # .?+
						if not self.globalvars.istrue(req):
							chunk.isactive=False
							break
				if chunk.isactive:
					for w in chunk.globalcmds:
						self.setvarcmd(w)

def parsenamestring(text,node):
	n=len(text)
	if not n: return []
	ret=[]
	start=0
	idx=0
	pcount=0
	while True:
		if idx==n:
			if start!=idx: ret.append(Word.parsename(text[start:],node))
			break
		c=text[idx]
		if not pcount and start!=idx:
			if c=='.':
				ret.append(Word.parsename(text[start:idx],node))
				ret.append(Word.literal('_component'))
				idx+=1
				start=idx
				continue
			if c==':':
				ret.append(Word.parsename(text[start:idx],node))
				ret.append(Word.literal('_example'))
				idx+=1
				start=idx
				continue
			if c=='/':
				ret.append(Word.parsename(text[start:idx],node))
				ret.append(Word.literal('_item'))
				idx+=1
				start=idx
				continue
		if c=='\\':
			idx+=1
			if idx==n: raise ValueError("Bad trailing escape in %s"%text)
			if text[idx] in ('(',')'): idx+=1 # need to escape "()"
			continue
		if c=='(': pcount+=1
		elif c==')': pcount-=1;
		idx+=1
		continue
	return ret

def raw_parseparams(text,node):
	if text[0]!='(': node_errorout(node,"Param string doesn't start with paren: %s"%text)
	if text[-1]!=')': node_errorout(node,"Param string doesn't end with paren: %s"%text)
	text=text[1:-1]
	n=len(text)
	ret=[]
	start=0
	idx=0
	pcount=0
	while True:
		if idx==n:
			if start!=idx: ret.append(text[start:].strip())
			break
		c=text[idx]
		if not pcount:
			if c==',':
				ret.append(text[start:idx].strip())
				idx+=1
				start=idx
				continue
		if c=='\\':
			idx+=1
			if idx==n: node_errorout(node,'Bad trailing escape character in "%s"'%text)
			if text[idx] in ('(',')',','): idx+=1 # need to escape "(),"
			continue
		if c=='(': pcount+=1
		elif c==')': pcount-=1;
		idx+=1
	return ret

def words_parseparams(text,node):
	texts=raw_parseparams(text,node)
	for i,text in enumerate(texts): texts[i]=Word.parseparam(text,node)
	return texts

def findequals_parsenamestring(text):
	for i,c in enumerate(text):
		if c=='(': return -1
		if c=='=': return i
	return -1

			
class Generation():
	def __init__(self,node,isgenerator):
		self.node=node
		self.isgenerator=isgenerator
		self.params=[] # if we are defined as x(a,b,c) then we'll have [a,b,c] here
		self.values=None # if we are an instance of (foo,bar), then we'll have [foo,bar] here
		self.generator=None # Node, for generated, points to creator node
		self.generateds={} # cname -> node, for generator
	def clearparams(self):
		self.params.clear()
	def addparam(self,name):
		self.params.append(name)
	def setgenerator(self,node):
		self.generator=node
	def setvalues(self,params):
		self.values=params
	def setvars(self,globalvars):
		gg=self.generator.generation
		if not gg: node_errorout(self.generator,'Generation.setvars: generator without generation')
		if len(gg.params)!=len(self.values):
			node_errorout(self.node,'Generated node has %s parameters instead of %s'%(len(self.values),len(gg.params)))
		for i in range(len(self.values)):
			globalvars.vars[gg.params[i]]=self.values[i]
	def addgenerated(self,cname,uid):
		self.generateds[cname]=uid
		
				
class Word():
	def literal(text):
		w=Word()
		w.orig=text
		w.text=text
		return w
	def command(orig,text,params):
		w=Word()
		w.orig=orig
		w.cmd=text
		w.params=params
		return w
	def escape(text):
		w=Word()
		w.orig=text
		w.escape=text
		return w
	def node(node):
		w=Word()
		w.orig='node'
		w.node=node
		return w
	def loadcommand(text,caller): # don't start with ._
		j=text.find('(')
		if j<0:
			if text=='_default':
				return Word.command(text,'path',[Word.literal(text)])
			else: node_errorout(caller,'command without paren: "%s"'%text)
		else:
			return Word.command(text,text[:j],words_parseparams(text[j:],caller))
	def parseparamcommand(text,caller): # don't start with a . , should have started with a .
		c=text[0]
		if c.isalnum():
			w=Word()
			w.orig=text
			w.cmd='path'
			w.params=parsenamestring(text,caller)
			return w
		if c=='$': return Word.command(text,'variable',[Word.literal(text[1:])])
		if c=='_': return Word.loadcommand(text[1:],caller)
		return Word.literal(text)
	def noparen_parsenamepart(text,caller): # a component in path w/o a paren
		c=text[0]
		if c=='$': return Word.command(text,'variable',[Word.literal(text[1:])])
		if not c.isalnum(): node_errorout(caller,'Invalid name or unknown command: "%s"'%text)
		return Word.literal(text)
	def parseparam(text,caller): # may start with .
		if len(text)<2: return Word.literal(text)
		if text[0]=='(' and text[-1]==')': return Word.literal(text[1:-1])
		if text[0]!='.': return Word.literal(text)
		return Word.parseparamcommand(text[1:],caller)
	def parsename(text,caller): # a component of a path
		if len(text)<2: return Word.literal(text)
		elif text[0]=='(' and text[-1]==')': return Word.literal(text[1:-1])
		j=text.find('(')
		if j<0: return Word.noparen_parsenamepart(text,caller)
		params=raw_parseparams(text[j:],caller)
		w=Word()
		w.orig=text
		w.cmd='generate'
		w.params=[]
		namepart=text[:j]
		if namepart in ('_l','_literal'):
			w.params.append(Word.literal(namepart))
		else:
			w.params.append(Word.noparen_parsenamepart(namepart,caller))
		for p in params: w.params.append(Word.parseparam(p,caller))
		return w
	def loadword(text,caller): # from a phase0 word
		if len(text)<2: return Word.literal(text)
		else:
			c=text[0]
			if c=='.':
				c=text[1]
				if c.isalnum():
					j=findequals_parsenamestring(text)
					if j<0:
						return Word.command(text,'join',[Word.pathcmd(text[1:],caller)])
					else:
						if j+1==len(text): node_errorout(caller,'Empty map value or trailing equals in "%s"'%text)
						params=[]
						params.append(Word.pathcmd(text[1:j],caller))
						params.append(Word.parseparam(text[j+1:],caller))
						return Word.command(text,'map',params)
				elif c=='_':
					command=text[2:]
					if command=='default' or command.startswith(('literal(','l(')):
						return Word.command(text,'join',[Word.pathcmd(text[1:],caller)])
					else:
						return Word.loadcommand(command,caller)
				elif c=='=':
					return Word.command(text,'name',[Word.pathcmd(text[2:],caller)])
				elif c=='<':
					return Word.command(text,'include',[Word.pathcmd(text[2:],caller)])
				elif c=='$':
					return Word.command(text,'variable',[Word.literal(text[2:])])
				elif c=='-':
					return Word.command(text,'suppress',[Word.pathcmd(text[2:],caller)])
				elif c=='+':
					return Word.command(text,'unsuppress',[Word.pathcmd(text[2:],caller)])
				else:
					node_errorout(caller,'Unknown command word: "%s"'%text)
			else:
				if c=='\\':
					text=text[1:]
					c=text[0]
					if c=='.' or c=='\\': return Word.literal(text)
					else: return Word.escape(text)
		return Word.literal(text)
	def unparen(text,caller): # paren escaping, from a parameter
		w=Word()
		w.orig=text
		if len(text)<2: w.text=text
		elif text[0]=='(' and text[-1]==')': w.text=text[1:-1]
		elif text[0]=='.': w.setcmd(text,caller)
		else: w.text=text
		return w
	def pathcmd(text,caller): # from a namestring, convert to path command
		w=Word()
		w.orig=text
		if len(text)<2: w.text=text ; return w
		elif text[0]=='(' and text[-1]==')': w.text=text[1:-1] ; return w
		w.cmd='path'
		w.params=parsenamestring(text,caller)
		return w
	def clonewords(words):
		ret=[]
		for w in words: ret.append(w.clone())
		return ret
	def __init__(self,text=None):
		self.orig=text
		self.text=text
		self.texts=None
		self.escape=None
		self.cmd=None
		self.params=None
		self.node=None
		self.relt=None
		self.nodes=None
	def clone(self):
		r=Word()
		r.orig=self.orig
		r.text=self.text
		if self.texts:
			r.texts=self.texts.copy()
		r.escape=self.escape
		r.cmd=self.cmd
		if self.params:
			r.params=[]
			for w in self.params: r.params.append(w.clone())
		r.node=self.node
		r.relt=self.relt
		if self.nodes:
			r.nodes=self.nodes.copy()
		return r
	def __repr__(self):
		if self.nodes: return 'nodes: %s'%self.nodes
		if self.text: return 'text: %s'%self.text
		if self.node: return '%s: #%s'%(self.cmd,self.node.uid)
		if self.texts: return self.texts
		if self.escape: return 'escape: %s'%self.escape
		return "%s: params: %s"%(self.cmd,self.params)
	def onlytext(self,caller=None):
		if self.text!=None: return self.text
		node_errorout(caller,'word is not a literal: %s'%self.orig)
	def textparams(self,errormsg):
		ret=[]
		if not self.params: return ret
		for w in self.params:
			if w.text!=None: ret.append(w.text)
			else: errorout('Error: [%s] in "%s" from "%s"'%(errormsg,self.params,self.orig))
		return ret
	def setnode(self,node,relt=1):
		self.node=node
		self.relt=relt
	def setnodes(self,nodes):
		self.nodes=nodes

class Suppressions():
	def __init__(self,old=None):
		if old:
			self.uids=old.uids.copy()
		else:
			self.uids=set()
	def issuppressed(self,nodes,node):
		if node.uid in self.uids: return True
		uid=node.getgeneratoruid(nodes)
		if uid in self.uids: return True
		return False
	def add(self,nodes,node,relt,isunsuppress): # relt: 1: self, 2: all, 3: component, 4: example, 5: item
		if isunsuppress:
			if relt==1:
				self.uids.discard(node.uid)
			elif relt==2:
				self.uids.discard(node.uid)
				for n in node.components: self.uids.discard(n.uid)
				for n in node.examples: self.uids.discard(n.uid)
				for n in node.items: self.uids.discard(n.uid)
			elif relt==3:
				for n in node.components: self.uids.discard(n.uid)
			elif relt==4:
				for n in node.examples: self.uids.discard(n.uid)
			elif relt==5:
				for n in node.items: self.uids.discard(n.uid)
		else:
			if relt==1:
				self.uids.add(node.uid)
			elif relt==2:
				self.uids.add(node.uid)
				for n in node.components: self.uids.add(n.uid)
				for n in node.examples: self.uids.add(n.uid)
				for n in node.items: self.uids.add(n.uid)
			elif relt==3:
				for n in node.components: self.uids.add(n.uid)
			elif relt==4:
				for n in node.examples: self.uids.add(n.uid)
			elif relt==5:
				for n in node.items: self.uids.add(n.uid)
	def addpath(self,nodes,path,isunsuppress):
		(node,relt)=nodes.path_findname(path,None,3)
		self.add(nodes,node,relt,isunsuppress)

class Node():
	def __init__(self,uid,lines):
		self.uid=uid				# other uids may also point to us
		self.orig_lines=lines
		self.words=[]
		self.ismarked=False # if plain text, we join to ''
		self.nickname=None # first name, if any
		self.components=[] # nodes in order of loading
		self.named_components={} # name -> node
		self.examples=[] # uids of nodes
		self.named_examples={} # name -> node
		self.items=[] # uids of nodes
		self.named_items={} # name -> node
		self.maps={} # key is uid of dimension, value is array of nodes points to
		self.revmaps={} # reverse of maps (in destination pointing back), key is dimension uid, value is array of nodes point to us
		self.generation=None # Generation()
	def makeorfindname(self,nodes,relt,w,caller): # relt: 3: components, 4: examples, 5: items
		if relt==3:
			nn=nodes.nodesbyuid.get(self.findnamedcomponent(w))
			if not nn:
				nn=nodes.makenode(w,caller)
				self.addnamedcomponent(w,nn)
		elif relt==4:
			nn=nodes.nodesbyuid.get(self.findnamedexample(w))
			if not nn:
				nn=nodes.makenode(w,caller)
				self.addnamedexample(w,nn)
		elif relt==5:
			nn=nodes.nodesbyuid.get(self.findnameditem(w))
			if not nn:
				nn=nodes.makenode(w,caller)
				self.addnameditem(w,nn)
		return nn
	def addnamednode(self,relt,node,w): # relt: 3: components, 4: examples, 5: items
		if relt==3:
			if self.findnamedcomponent(w): node_errorout(self,"Duplicate component %s"%w)
			self.addnamedcomponent(w,node)
		elif relt==4:
			if self.findnamedexample(w): node_errorout(self,"Duplicate example %s"%w)
			self.addnamedexample(w,node)
		elif relt==5:
			if self.findnameditem(w): node_errorout(self,"Duplicate item %s"%w)
			self.addnameditem(w,node)
	def adopt2(self,nodes,dest,src,word):
		s=set()
		for n in src: s.add(n.uid)
		if self.uid in src: node_errorout(self,'adoption of self in "%s"'%word)
		for n in dest: s.add(n.uid)
		dest.clear()
		for uid in s:
			dest.append(nodes.nodesbyuid[uid])
	def adopt(self,nodes,node,relt,word): # relt: 2: all, 3: components, 4: examples: 5: items
		if relt==2:
			self.adopt2(nodes,self.components,node.components,word)
			self.adopt2(nodes,self.examples,node.examples,word)
			self.adopt2(nodes,self.items,node.items,word)
		elif relt==3:
			self.adopt2(nodes,self.components,node.components,word)
		elif relt==4:
			self.adopt2(nodes,self.examples,node.examples,word)
		elif relt==5:
			self.adopt2(nodes,self.items,node.items,word)
		else: node_errorout(self,'adopt with invalid relt: %s in word "%s"'%(relttostring(relt),word))
	def name_cmd(self,nodes,params):
		np=len(params)
		if not np: node_errorout(self,"empty name")
		if np==1:
			p=params[0]
			if p.text: nodes.registerowner(p.text,self)
			else:
				if p.cmd=='path':
					p=p.params[0]
					if p.text: nodes.registerowner(p.text,self)
				elif p.cmd=='generate':
					name=p.params[0].onlytext(self)
					nodes.registerowner(name,self)
					if not self.generation: self.generation=Generation(self,True)
					self.generation.clearparams()
					for p in p.params[1:]:
						self.generation.addparam(p.onlytext(self))
				else: node_errorout(self,'unknown command in name: "%s"'%p)
		else:
			node=nodes.name_findtopnode(params[0].onlytext(self))
			if not node: node_errorout(self,'Couldn\'t find first node in "%s"'%params)
			relt=3 # 1: self, 3: components, 4: examples, 5: items
			for w in params[1:-1]:
				w=w.onlytext(self)
				if not w: node_errorout(self,"empty name component")
				if w[0]=='_':
					if w in ('_component','_components','_c'): relt=3
					elif w in ('_example','_examples','_e'): relt=4
					elif w in ('_item','_items','_i'): relt=5
					elif w=='_self' or w=='_s': relt=1
					else: node_errorout(self,"unknown reserved command %s"%w)
					continue
				if relt==3: node=node.findnamedcomponent(w)
				elif relt==4: node=node.findnamedexample(w)
				elif relt==5: node=node.findnameditem(w)
				if not node: node_errorout(self,'Couldn\'t find node in path "%s"'%w)
				relt=3
			text=params[-1].onlytext(self)
			node.addnamednode(relt,self,text)
			nodes.registerowner(text,self)
	def loadwords(self,nodes,texts):
		for text in texts:
			if text.startswith('.?'): continue
			w=Word.loadword(text,self)
			self.words.append(w)
			if not w.cmd: continue
			if w.cmd=='name':
				if 1!=len(w.params): errorout('name takes 1 parameter, got: "%s"'%w.params)
				self.name_cmd(nodes,w.params[0].params)
	def prebuild(self,nodes,globalvars):
		for w in self.words:
			if not w.cmd: continue
			if w.cmd=='join':
				if 1!=len(w.params): node_errorout(self,'_join takes 1 parameter, got "%s"'%w.params)
				p0=w.params[0]
				if p0.cmd!='path': node_errorout(self,'_join takes path parameter, got "%s"'%w.params)
				(node,relt)=nodes.findpath(p0.params,self,globalvars,3)
				if relt==3: node.addcomponent(self)
				elif relt==4: node.addexample(self)
				elif relt==5: node.additem(self)
			elif w.cmd=='variable':
				self.flattenword(nodes,globalvars,w)
			elif w.cmd=='map':
				if len(w.params)!=2: node_errorout(self,'_map takes 2 parameters, got %s'%w.params)
				dimp=w.params[0]
				if dimp.text: node_errorout(self,'_map needs node for first parameter, got "%s"'%dimp)
				if dimp.cmd!='path': node_errorout(self,'_map first parameter should be path command, got "%s"'%dimp)
				(dimnode,relt)=nodes.findpath(dimp.params,self,globalvars,1)
				if relt!=1: node_errorout(self,'_map parameters can\'t point to children in "%s"'%dimp)
				destp=w.params[1]
				if destp.text:
					w=Word.command(destp.text,'generate',[Word.literal('_literal'),Word.literal(destp.text)])
					params=[w]
				else:
					if destp.cmd!='path': node_errorout(self,'_map second parameter should be path command, got "%s"'%destp)
					params=destp.params
				(destnode,relt)=nodes.findpath(params,self,globalvars,1)
				if relt!=1: node_errorout(self,'_map parameters can\'t point to children in "%s"'%destp)
				self.addmap(dimnode,destnode)
			elif w.cmd=='unmap':
				if 2==len(w.params):
					p0=w.params[0]
					if p0.cmd=='variable':
						self.flattenword(nodes,globalvars,p0)
					dimp=w.params[1]
				elif 1==len(w.params):
					dimp=w.params[0]
				else:
					node_errorout(self,'unmap takes 1 or 2 parameters, got "%s"'%w.params)
				if dimp.cmd!='path': node_errorout(self,'unmap takes a path parameter, got "%s"'%dimp)
				(dimnode,relt)=nodes.findpath(dimp.params,self,globalvars,1)
				dimp.setnode(dimnode,relt)
			elif w.cmd in ('global0','globalint','globalstring', # Phase0
						'name', # loadwords
						'include','suppress','unsuppress','adopt', # postbuild
						'set','setstring','unset','sum','printvar','assert'): # RuntimeVars
				pass
			else:
				node_errorout(self,'Node.loadwords: Unknown command "%s"'%w.cmd)
	def flatten_textparams(self,nodes,globalvars,word):
		ret=[]
		if not word.params: return ret
		clone=word.clone()
		self.flattenword(nodes,globalvars,clone)
		for w in clone.params:
			if w.node: ret.append(w.node.uid)
			else: ret.append(w.text)
		return ret
	def flattenword(self,nodes,globalvars,word):
		if word.text: return
		for w in word.params:
			self.flattenword(nodes,globalvars,w)
		if word.cmd=='variable':
			if len(word.params)!=1: node_errorout(self,'variable takes 1 parameter, got %s'%word.params)
			name=word.params[0].onlytext(self)
			value=globalvars.vars.get(name)
			if value==None: node_errorout(self,'variable not found: "%s" in %s'%(name,globalvars.vars))
			if isinstance(value,int):
				n=nodes.nodesbyuid[value]
				word.setnode(n)
			else:
				word.text=globalvars.getstring(name)
		elif word.cmd=='unmap':
			node=self
			if 2==len(word.params):
				node=word.params[0].node
				dimnode=word.params[1].node
			elif 1==len(word.params):
				dimnode=word.params[0].node
			mappednodes=node.findmaps(dimnode)
			word.setnodes(mappednodes)
			word.texts=[]
			for n in mappednodes:
				for w in n.words:
					if w.text: word.texts.append(w.text)
			word.text=' '.join(word.texts)
		elif word.cmd=='path':
			(node,relt)=nodes.findpath(word.params,self,globalvars,0)
			word.setnode(node,relt)
	def postbuild(self,nodes,globalvars_in):
		globalvars=globalvars_in.clone()
		globalvars.setvar('_uid',self.uid)
		for w in self.words:
			if not w.cmd: continue
			if w.cmd=='include':
				if 1==len(w.params): pass
				elif 2==len(w.params):
					self.flattenword(nodes,globalvars,w.params[1])
				else: node_errorout(self,'_include takes 1 or 2 parameters, got "%s"'%w)
				p0=w.params[0]
				if p0.cmd!='path': node_errorout(self,'_include takes a path parameter, got "%s"'%w)
				(node,relt)=nodes.findpath(p0.params,self,globalvars,0)
				w.setnode(node,relt)
			elif w.cmd=='adopt':
				if 1!=len(w.params): node_errorout(self,'_adopt takes 1 parameter, got "%s"'%w)
				p0=w.params[0]
				if p0.cmd!='path': node_errorout(self,'_adopt takes a path parameter, got "%s"'%w)
				(node,relt)=nodes.findpath(p0.params,self,globalvars,2)
				self.adopt(nodes,node,relt,w)
			elif w.cmd=='unmap':
				self.flattenword(nodes,globalvars,w)
			elif w.cmd=='suppress':
				if 1!=len(w.params): node_errorout(self,'_suppress takes 1 parameter, got "%s"'%w)
				p0=w.params[0]
				if p0.cmd!='path': node_errorout(self,'_suppress takes a path parameter, got "%s"'%w)
				(node,relt)=nodes.findpath(p0.params,self,globalvars,2)
				if not node: node_errorout(self,'suppress node not found: "%s"'%w.params)
				w.node=node
				w.relt=relt
			elif w.cmd=='unsuppress':
				if 1!=len(w.params): node_errorout(self,'_unsuppress takes 1 parameter, got "%s"'%w)
				p0=w.params[0]
				if p0.cmd!='path': node_errorout(self,'_unsuppress takes a path parameter, got "%s"'%w)
				(node,relt)=nodes.findpath(p0.params,self,globalvars,2)
				if not node: node_errorout(self,'unsuppress node not found: "%s"'%w.params)
				w.node=node
				w.relt=relt
			elif w.cmd in ('set','setstring','unset','sum','printvar','assert'):
				self.flattenword(nodes,globalvars,w)
	def findnamedcomponent(self,name): return self.named_components.get(name)
	def addnamedcomponent(self,name,node):
		self.components.append(node)
		self.named_components[name]=node
	def addcomponent(self,node):
		self.components.append(node)
	def findnamedexample(self,name): return self.named_examples.get(name)
	def addnamedexample(self,name,node):
		self.examples.append(node)
		self.named_examples[name]=node
	def addexample(self,node):
		self.examples.append(node)
	def findnameditem(self,name): return self.named_items.get(name)
	def addnameditem(self,name,node):
		self.items.append(node)
		self.named_items[name]=node
	def additem(self,node):
		self.items.append(node)
	def addmap(self,dimnode,destnode):
		va=self.maps.get(dimnode.uid)
		if not va: va=self.maps[dimnode.uid]=[]
		va.append(destnode)
		va=destnode.revmaps.get(dimnode.uid)
		if not va: va=destnode.revmaps[dimnode.uid]=[]
		va.append(self)
	def findmaps(self,dimnode,empty=[]):
		va=self.maps.get(dimnode.uid)
		if not va: return empty # [] is static
		return va
	def word_export(self,nodes,suppressions,po,depth,word):
		if not depth: node_errorout(self,'Recursion depth too high')
		depth-=1

		if word.node:
			if suppressions.issuppressed(nodes,word.node): return
			for w in word.node.words:
				po.addword(w) # (ignore)
			return
		if word.nodes:
			for node in word.nodes:
				self.word_export(nodes,suppressions,po,depth,Word.node(node))
		if po.addword(word): return
		node_errorout(self,'word_export: unhandled format: %s'%word)
	def export(self,nodes,suppressions_in,po,depth,relt=1,childbreak=None):
		if suppressions_in.issuppressed(nodes,self): return

		if not depth: node_errorout(self,'Recursion depth too high')
		depth-=1

		suppressions=suppressions_in

		if relt==0:
			relt=3 if self.components else 1

		if relt==3:
			for i,node in enumerate(self.components):
				if i and childbreak: self.word_export(nodes,suppressions,po,depth,childbreak)
				node.export(nodes,suppressions,po,depth)
		elif relt==4:
			for i,node in enumerate(self.examples):
				if i and childbreak: self.word_export(nodes,suppressions,po,depth,childbreak)
				node.export(nodes,suppressions,po,depth)
		elif relt==5:
			for i,node in enumerate(self.items):
				if i and childbreak: self.word_export(nodes,suppressions,po,depth,childbreak)
				node.export(nodes,suppressions,po,depth)
		else:
			for w in self.words:
				if w.nodes:
					for node in w.nodes:
						node.export(nodes,suppressions,po,depth)
				elif w.text: po.literal(w.text)
				elif w.escape: po.escape(w.escape)
				elif w.cmd:
					if w.cmd=='include':
						cb=None
						if 2==len(w.params): cb=w.params[1]
						node=w.node
						node.export(nodes,suppressions,po,depth,relt=w.relt,childbreak=cb)
					elif w.cmd=='variable':
						if w.node: po.literal('#%s(%s)'%(w.node.uid,w.node.nickname))
					elif w.cmd=='unmap':
						for node in w.nodes:
							node.export(nodes,suppressions,po,depth)
					elif w.cmd=='suppress':
						if suppressions==suppressions_in: suppressions=Suppressions(suppressions_in)
						suppressions.add(nodes,w.node,w.relt,False)
					elif w.cmd=='unsuppress':
						if suppressions==suppressions_in: suppressions=Suppressions(suppressions_in)
						suppressions.add(nodes,w.node,w.relt,True)
					else:
						po.command(w.cmd,w.params)
	def components_export(self,po):
		for node in self.components:
			node.dump()
	def examples_export(self,po):
		for node in self.examples:
			node.dump()
	def items_export(self,po):
		for node in self.items:
			node.dump()
	def addgenerated(self,cname,node):
		if not self.generation: self.generation=Generation(self)
		self.generation.addgenerated(cname,node.uid)
	def getgeneratoruid(self,nodes):
		x=self.generation
		if not x: return 0
		x=x.generator
		if not x: return 0
		return x.uid
	def dump(self):
		print("Node %s: %s"%(self.uid,self.nickname or ''))
		if self.orig_lines: print("orig:",self.orig_lines)
		if self.words: print("words:",self.words)
		if self.components:
			print('components:',end='')
			for n in self.components: print(' #%s(%s)'%(n.uid,n.nickname),end='')
			print()
		if self.named_components: print("named_components:",self.named_components)
		if self.examples: print("examples:",self.examples)
		if self.named_examples: print("named_examples:",self.named_examples)
		if self.items: print("items:",self.items)
		if self.named_items: print("named_items:",self.named_items)
		print()

class Nodes():
	def relttostring(relt):
		if relt==1: return '_self'
		if relt==2: return '_all'
		if relt==3: return '_component'
		if relt==4: return '_example'
		if relt==5: return '_item'
		return 'unknown (%s)'%relt
	def __init__(self):
		self.nextuid=1
		self.nodes=[]
		self.nodesbyuid={}
		self.nodesbyname={}
		self.globalvars=None
	def setglobalvars(self,g): self.globalvars=g
	def createnode(self,lines):
		node=Node(self.nextuid,lines)
		self.nodes.append(node)
		self.nodesbyuid[self.nextuid]=node
		self.nextuid+=1
		return node
	def adddefaultnode(self):
		node=self.createnode(['_built-in'])
		node.nickname='_default'
		self.nodesbyname['_default']=node
		return node
	def addliteralnode(self):
		node=self.createnode(['_built-in'])
		node.nickname='_literal'
		node.words.append(Word.command('built-in','variable',[Word.literal('a')]))
		gen=Generation(node,True)
		gen.params.append('a')
		node.generation=gen
		self.nodesbyname['_literal']=node
		self.nodesbyname['_l']=node
		return node
	def lines_addnode(self,words,lines):
		node=self.createnode(lines)
		node.loadwords(self,words)
		if node.generation and node.generation.isgenerator:
			pass # we don't prebuild or postbuild on generators, just the generateds
		else:
			node.prebuild(self,self.globalvars) # this fixes maps and variables
			node.postbuild(self,self.globalvars) # can now access maps, we can pass our uid to generators
		return node
	def makenode(self,name,caller):
		if not name or not name[0].isalnum(): errorout('Illegal node name: %s'%name)
		node=self.createnode(None)
		node.nickname=name
		return node
	def registerowner(self,name,node):
		if name in self.nodesbyname: node_errorout(node,'Node already exists: "%s"'%name)
		node.nickname=name
		self.nodesbyname[name]=node
	def nodes_dump(self):
		for node in self.nodes: node.dump()
	def names_dump(self):
		for name in self.nodesbyname:
			print("%s (%s)"%(name,type(name)))
	def name_findtopnode(self,name):
		return self.nodesbyname.get(name)
	def makegenenode(self,generator,params,cname,caller):
		node=self.createnode(None)
		node.nickname=cname
		node.words=Word.clonewords(generator.words)
		gen=Generation(node,False)
		gen.setvalues(params)
		gen.setgenerator(generator)
		node.generation=gen
		generator.addgenerated(cname,node)
		return node
	def findtopgenenode(self,w,globalvars,caller):
		if w.text: return self.nodesbyname.get(w.text)
		if w.cmd=='generate':
			textparams=caller.flatten_textparams(self,globalvars,w)
			generator=textparams[0]
			cname=self.makecanonical(generator,textparams[1:])
			node=self.nodesbyname.get(cname)
			if node: return node
			node=self.nodesbyname.get(generator)
			if not node:
				sug=', perhaps you meant "_%s"'%generator if generator in allcommands_global else ''
				node_errorout(caller,'Generator "%s" not found%s'%(generator,sug))
			node=self.makegenenode(node,textparams[1:],cname,caller)
			self.nodesbyname[cname]=node
			gv=globalvars.clone()
			node.generation.setvars(gv)
			node.prebuild(self,gv)
			node.postbuild(self,gv)
			return node
		node_errorout(caller,'Unknown format: w: "%s"'%(w))
	def findpath(self,params,node,globalvars,def_relt):
		np=len(params)
		if not np: node_errorout(node,"empty path in %s"%path)
		p=params[0]
		nn=self.findtopgenenode(p,globalvars,node)
		if not nn: node_errorout(node,'topnode not found "%s"'%(p))
		node=nn
		relt=0 # 1: self, 2: all, 3: components, 4: examples, 5: items
		for w in params[1:]:
			w=w.onlytext(self)
			if not w: node_errorout(node,"empty name component in %s"%path)
			if w[0]=='_':
				if w in ('_component','_components','_c'): relt=3
				elif w in ('_example','_examples','_e'): relt=4
				elif w in ('_item','_items','_i'): relt=5
				elif w=='_self' or w=='_s': relt=1
				elif w=='_all' or w=='_a': relt=2
				else: node_errorout(node,"unknown reserved command %s"%w)
				continue
			if relt==0 or relt==3:
				nn=node.findnamedcomponent(w)
				if not nn: node_errorout(node,'namedcomponent not found: "%s" in "%s", have "%s"'%(w,params,node.named_components.keys()))
				node=nn
			elif relt==4:
				nn=node.findnamedexample(w)
				if not nn: node_errorout(node,'namedexample not found: "%s" in "%s", have "%s"'%(w,params,node.named_examples.keys()))
				node=nn
			elif relt==5:
				nn=node.findnameditem(w)
				if not nn: node_errorout(node,'nameditems not found: "%s" in "%s", have "%s"'%(w,params,node.named_items.keys()))
				node=nn
			else: node_errorout(node,'invalid relation type %s in %s'%(relt,params))
			if not node: node_errorout(node,'node not found "%s" in %s'%(w,params))
			relt=0
		if relt==0: relt=def_relt
		return (node,relt)
	def path_findname(self,path,node,defrelt): # this is meant to be called from main
		params=parsenamestring(path,node)
		return self.findpath(params,node,self.globalvars,defrelt)
	def makecanonical(self,generator,params):
		a=[]
		a.append('('+generator+')')
		for p in params:
			a.append('(%s)'%p)
		return ''.join(a)

class RuntimeVars():
	def __init__(self):
		self.vars={'sum':Fraction(0)}
	def run(self,w):
		cmd=w.cmd
		params=w.textparams('Runtimevars only support text parameters')
		np=len(params) if params else 0
		if cmd=='set':
			if np==1: self.vars[params[0]]=Fraction(1)
			elif np==2: self.vars[params[0]]=Fraction(Decimal(params[1]))
			elif np==3: self.vars[params[0]]=Fraction(int(params[1]),int(params[2]))
			else: errorout('invalid number of parameters to _set: %s'%w)
		elif cmd=='setstring':
			if np==2: self.vars[params[0]]=params[1]
			else: errorout('invalid number of parameters to _setstring: %s'%w)
		elif cmd=='unset':
			for p in params: self.vars[p]=Fraction(0)
		elif cmd=='sum':
			if np==1: self.vars['sum']+=Fraction(Decimal(params[0]))
			elif np==2:
				if params[0] not in self.vars: raise ValueError("Unknown var %s"%(params[0]))
				self.vars[params[0]]+=Fraction(Decimal(params[1]))
			elif np==3:
				if params[0] not in self.vars: raise ValueError("Unknown var %s"%(params[0]))
				self.vars[params[0]]+=Fraction(int(params[1]),int(params[2]))
			else: errorout('unknown _sum %s'%params)
		elif cmd=='printvar':
			if not params: params=['sum']
			for v in params:
				if not v in self.vars: errorout('Bad var %s'%(v))
				nd=self.vars[v].as_integer_ratio()
				if nd[1]==1: print(nd[0],end='')
				else: print(float(self.vars[v]),end='')
		elif cmd=='assert':
			for p in params:
				c=True
				if p[0]=='-':
					c=False
					p=p[1:]
				if p not in self.vars:
					errorout('Error: Runtime variable assert failed: "%s" not found'%(p))
				if c!=(self.vars[p]!=0):
					errorout('Error: Runtime variable assert failed: "%s" is %s instead of %s'%(p,self.vars[p],c))
		else: errorout('unknown cmd %s %s'%(cmd,params))

class html_Escapes():
# this WILL print redundant closes
	def __init__(self):
		self.dict={
				'Paragraph':'<p>','paragraph':'</p>',
				'br':'<br>',
				'Bold':'<b>','bold':'</b>',
				'Italic':'<i>','italic':'</i>',
				'Underline':'<u>','underline':'</u>', }
	def process(self,w): return self.dict[w]
	def filter(self,w): return w

class xhtml_Escapes():
# this WILL print redundant closes
	def __init__(self):
		self.dict={
				'Paragraph':'<p>','paragraph':'</p>',
				'br':'<br/>',
				'Bold':'<b>','bold':'</b>',
				'Italic':'<i>','italic':'</i>',
				'Underline':'<u>','underline':'</u>', }
	def process(self,w): return self.dict[w]
	def filter(self,w): return w

class text_Escapes():
# this will NOT print redundant closes
	def __init__(self):
		self.italic=0
		self.bold=0
		self.underline=0
		self.all=0
	def process(self,w):
		if w=='Paragraph': return ''
		if w=='paragraph': return '\n'
		if w=='br': return '\n'
		if w=='Bold':
			self.bold+=1
			self.all+=1
			return '*'
		if w=='bold':
			if not self.bold: return ''
			self.bold-=1
			self.all-=1
			return '*'
		if w=='Italic':
			self.italic+=1
			self.all+=1
			return '_'
		if w=='italic':
			if not self.italic: return ''
			self.italic-=1
			self.all-=1
			return '_'
		if w=='Underline':
			self.underline+=1
			self.all+=1
			return '__'
		if w=='underline':
			if not self.underline: return ''
			self.underline-=1
			self.all-=1
			return '__'
		raise ValueError('unhandled escape')
	def filter(self,w):
		if not self.all: return w
		if w!=' ': return w
		if self.bold: return '*'
		return '_'

class Escapes:
	def find(name):
		if name=='html': return html_Escapes()
		if name=='xhtml': return xhtml_Escapes()
		if name=='text': return text_Escapes()
		raise ValueError('Unknown escapes type: %s'%name)
		return None

class PreOutput():
	def __init__(self,globalvars,fout):
		self.words=[]
		self.wantspace=False
		self.space=Word(' ')
		self.globalvars=globalvars
		self.fout=fout
		self.isbrokenline=False
	def literal(self,text):
		if self.wantspace: self.words.append(self.space)
		else: self.wantspace=True
		self.words.append(Word.literal(text))
	def escape(self,text):
		if text=='space':
			self.words.append(self.space)
			self.wantspace=False
			return
		if text=='backspace':
			self.wantspace=False
			return
		if text in ('t','n','br'):
			self.wantspace=False
		w=Word.escape(text)
		self.words.append(w)
	def addword(self,word):
		if word.escape: self.escape(word.escape) ; return True
		if word.text: self.literal(word.text) ; return True
		return False
	def command(self,text,params):
		if text not in ('set','setstring','unset','sum','printvar','assert'): return
		w=Word.command(text,text,params)
		self.words.append(w)
	def printout(self,text):
		if 0==len(text): return
		self.isbrokenline=(text[-1]!='\n')
		print(text,end='',file=self.fout)
	def finalize(self,isforce=None):
		isassertcheck=True
		if self.globalvars.istrue('_noassert'): isassertcheck=False
		if isforce: isassertcheck=not isforce
		escapesmode=self.globalvars.getstring('_escapesmode')
		escapes=Escapes.find(escapesmode)
		rv=RuntimeVars()
		for w in self.words:
			if w.text: self.printout(escapes.filter(w.text)) ; continue
			if w.escape:
				if w.escape=='t': self.printout('\t')
				elif w.escape=='n': self.printout('\n')
#				elif w.escape=='space': print(escapes.filter(' '),end='',file=fout)
				else: self.printout(escapes.process(w.escape))
			elif w.cmd:
				if w.cmd in ('set','setstring','unset','sum','printvar'):
					rv.run(w)
				elif w.cmd=='assert':
					if isassertcheck: rv.run(w)
				else:
					raise ValueError('unhandled command: %s'%w)

def printusage():
	print('Usage: mset.py INFILE [+flag] [--option] [.nodename]')
	print('Options: --html, --xhtml --text --force --p0dump -gvdump --nodesdump --namesdump --debug')
	exit(0)

if False:
	text='._join(.a.b.c)'
	w=Word.loadword(text,None)
	print('text:',text,'w:',w)
	exit(0)

exports=[]
topsuppressions=[]
p0=Phase0()
p0.setvarcmd('._globalstring(_escapesmode,html)')
p0_dump=False
gv_dump=False
nodes_dump=False
names_dump=False
isforce=None

if 1==len(sys.argv): printusage()

for arg in sys.argv[1:]:
	if arg.startswith('--'):
		if arg=='--html': p0.setvarcmd('._globalstring(_escapesmode,html)')
		if arg=='--xhtml': p0.setvarcmd('._globalstring(_escapesmode,xhtml)')
		elif arg=='--text': p0.setvarcmd('._globalstring(_escapesmode,text)')
		elif arg=='--force': isforce=True
		elif arg=='--p0dump': p0_dump=True
		elif arg=='--gvdump': gv_dump=True
		elif arg=='--nodesdump': nodes_dump=True
		elif arg=='--namesdump': names_dump=True
		elif arg=='--debug': isdebug_global=True
		elif arg=='--help': printusage()
		else:
			raise ValueError("Unknown argument %s"%arg)
	elif arg.startswith('+'):
		p0.globalvars.setvarparse(arg[1:])
	elif arg.startswith('.'):
		if arg=='.': exports.append('_default')
		elif arg.startswith('.-'):
			topsuppressions.append(arg[2:])
		else: exports.append(arg[1:])
	else:
		p0.addfile(arg)
p0.collectvars()
p0.process()

if not exports: exports.append('mainmenu')

if p0_dump:
	p0.dump()
	exit(0)

# now all input is processed and conditional inclusion has been done

nodes=Nodes()
nodes.setglobalvars(p0.globalvars)
if gv_dump:
	print('Globalvars:',nodes.globalvars.vars)
	exit(0)
defaultnode=nodes.adddefaultnode()
nodes.addliteralnode()
for chunk in p0.chunks:
	if not chunk.isactive: continue
	node=nodes.lines_addnode(chunk.words,chunk.lines)
	if not node.ismarked:
		defaultnode.addcomponent(node)

if nodes_dump:
	nodes.nodes_dump()
	exit(0)

if names_dump:
	nodes.names_dump()
	exit(0)

po=PreOutput(nodes.globalvars,sys.stdout)

suppressions=Suppressions()
for path in topsuppressions:
	suppressions.addpath(nodes,path,False)
for path in exports:
	(node,relt)=nodes.path_findname(path,None,0)
	if relt==0:
		relt=3 if node.components else 1
	if relt==2:
		node.dump()
	else:
		node.export(nodes,suppressions,po,10,relt)
po.finalize(isforce)
if po.isbrokenline: print()
