#=======================================================================================
# Imports
#=======================================================================================

import os
import time
from .debugging import dprint

#=======================================================================================
# Library
#=======================================================================================

#==========================================================
class BaseFile(object):
	
	#=============================
	"""Base Class for various types of fileobjects as recognized by filesystems."""
	#=============================
	
	def __init__(self, path):
		self.path = path
		self.existed = self.exists # Determines whether this file existed at the time of instantiation.
		
	@property
	def parentDir(self):
		return Dir(os.path.dirname(self.path))

	@property
	def lastModified(self):
		return int(os.path.getmtime(self.path))

	@property
	def secondsSinceLastModification(self):
		return int(time.time()) - int(self.lastModified)

	@property
	def exists(self):
		return os.path.exists(self.path)
	
	@property
	def writable(self):
		return os.access(self.path, os.W_OK)
	
class MakeableFile(BaseFile):
	
	#=============================
	"""Extension of BaseFile with file making checks and 'make' as an interface stub. For subclassing."""
	#=============================
	
	def __init__(self, path, make=False, makeDirs=False):
		super().__init__(path)
		if makeDirs: # Prevent recursion, but it isn't obvious. Perhaps introduce something like 'stop='.
			if not self.parentDir.exists:
				self.makeDirs()
		if not self.exists and make:
			self.make()
	def make(self):
		# Should probably throw UnimplementedError or something.
		pass#OVERRIDE
	def makeDirs(self):
		os.makedirs(self.parentDir.path)

#==========================================================
class File(MakeableFile):
	
	#=============================
	"""Basic file wrapper.
	Abstracts away basic operations such as read, write, etc."""
	#TODO: Make file operations safer and failures more verbose with some checks & exceptions.
	#=============================
	
	def __init__(self, path, make=False, makeDirs=False):
		super().__init__(path, make=make, makeDirs=makeDirs)
	
	def write(self, data):
		with open(self.path, "w") as fileHandler:
			fileHandler.write(data)

	def read(self):
		with open(self.path, "r") as fileHandler:
			return fileHandler.read()

	def remove(self):
			os.remove(self.path)

	def make(self):
		"""Write empty file to make sure it exists."""
		self.write("")

#==========================================================
class Dir(MakeableFile):
	
	#=============================
	"""Represents a directory on the filesystem."""
	#=============================
	
	def __init__(self, path, make=False, makeDirs=False):
		super().__init__(path, make=make, makeDirs=makeDirs)
	
	def remove(self, nonEmpty=False):
		"""Remove directory from the filesystem. Only supports empty directories as of now."""
		if nonEmpty:
			pass#NOTE: Not implemented yet, as this part needs some careful deliberation first.
			#shutil.rmtree(self.path)
		else:
			os.rmdir(self.path)
	
	@property
	def allNames(self):
		"""Returns a list of the names of all items in the directory.
		That doesn't include self and parent reference items, such as '.' or '..'."""
		return os.listdir(self.path)
	
	@property
	def fileNames(self):
		"""Returns a list of names of all (normal) files in the directory (e.g. no directories)."""
		return [os.path.basename(path) for path in self.filePaths]
	
	@property
	def allPaths(self):
		"""Returns a list of absolute paths of all items in the directory.
		That doesn't include self and parent reference items, such as '.' or '..'."""
		return [os.path.join(self.path, name) for name in self.allNames]
		
	@property
	def filePaths(self):
		"""Returns a list of absoute paths of all (normal) files in the directory (e.g. no directories)."""
		return [path for path in self.allPaths if os.path.isfile(path)]
	
	@property
	def dirPaths(self):
		"""Returns a list of absolute paths of all directories in the directory."""
		return [path for path in self.allPaths if os.path.isdir(path)]
	
	@property
	def all(self):
		"""Returns a list of File or Dir objects of all files or dirs in the directory."""
		items = []
		for path in self.allPaths:
			if os.path.isdir(path):
				items.append(Dir(path))
			else:
				items.append(File(path))
		return items
	
	def make(self):
		os.mkdir(self.path)