# This file is part of Fail2Ban.
#
# Fail2Ban is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Fail2Ban is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Fail2Ban; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

# Author: Cyril Jaquier
# 
# $Revision$

__author__ = "Cyril Jaquier"
__version__ = "$Revision$"
__date__ = "$Date$"
__copyright__ = "Copyright (c) 2004 Cyril Jaquier"
__license__ = "GPL"

from jail import Jail
from transmitter import Transmitter
import locale, logging, sys, os, signal

# Gets the instance of the logger.
logSys = logging.getLogger("fail2ban.server")

class Server:
	
	def __init__(self, daemon = False):
		self.jails = dict()
		self.daemon = daemon
		self.transm = Transmitter(self)
		self.logLevel = 3
		self.logTarget = "STDERR"
		# Set logging level
		self.setLogLevel(self.logLevel)
		self.setLogTarget(self.logTarget)
	
	def start(self, force):
		logSys.info("Starting Fail2ban")
		if self.daemon:
			ret = self.createDaemon()
			if ret:
				logSys.info("Daemon started")
			else:
				logSys.error("Could not create daemon")
				raise ServerInitializationError("Could not create daemon")
		# Start the communication
		logSys.debug("Starting communication")
		self.transm.start(force)
		logSys.info("Exiting Fail2ban")
	
	def quit(self):
		self.stopAllJail()
		self.transm.stop()
	
	def addJail(self, name):
		self.jails[name] = Jail(name)
		
	def delJail(self, name):
		if self.jails.has_key(name):
			del self.jails[name]
		else:
			raise ServerUnknownJail(name)
	
	def startJail(self, name):
		if self.jails.has_key(name):
			self.jails[name].start()
		else:
			raise ServerUnknownJail(name)
	
	def stopJail(self, name):
		if self.jails.has_key(name):
			if self.isActive(name):
				self.jails[name].stop()
				self.delJail(name)
		else:
			raise ServerUnknownJail(name)
	
	def stopAllJail(self):
		for jail in self.jails.copy():
			self.stopJail(jail)
			
	def isActive(self, name):
		if self.jails.has_key(name):
			return self.jails[name].isActive()
		else:
			raise ServerUnknownJail(name)
	
	def setIdleJail(self, name, value):
		if self.jails.has_key(name):
			self.jails[name].setIdle(value)
			return True
		else:
			raise ServerUnknownJail(name)

	def getIdleJail(self, name):
		if self.jails.has_key(name):
			return self.jails[name].getIdle()
		else:
			raise ServerUnknownJail(name)
	
	# Filter
	def setLogPath(self, name, file):
		if self.jails.has_key(name):
			self.jails[name].getFilter().setLogPath(file)
	
	def getLogPath(self, name):
		if self.jails.has_key(name):
			return self.jails[name].getFilter().getLogPath()
		else:
			raise ServerUnknownJail(name)
	
	def setTimeRegex(self, name, value):
		if self.jails.has_key(name):
			self.jails[name].getFilter().setTimeRegex(value)
		else:
			raise ServerUnknownJail(name)
	
	def getTimeRegex(self, name):
		if self.jails.has_key(name):
			return self.jails[name].getFilter().getTimeRegex()
		else:
			raise ServerUnknownJail(name)
	
	def setTimePattern(self, name, value):
		if self.jails.has_key(name):
			self.jails[name].getFilter().setTimePattern(value)
		else:
			raise ServerUnknownJail(name)
	
	def getTimePattern(self, name):
		if self.jails.has_key(name):
			return self.jails[name].getFilter().getTimePattern()
		else:
			raise ServerUnknownJail(name)

	def setFailRegex(self, name, value):
		if self.jails.has_key(name):
			self.jails[name].getFilter().setFailRegex(value)
		else:
			raise ServerUnknownJail(name)
	
	def getFailRegex(self, name):
		if self.jails.has_key(name):
			return self.jails[name].getFilter().getFailRegex()
		else:
			raise ServerUnknownJail(name)
	
	def setMaxRetry(self, name, value):
		if self.jails.has_key(name):
			self.jails[name].getFilter().setMaxRetry(value)
		else:
			raise ServerUnknownJail(name)
	
	def getMaxRetry(self, name):
		if self.jails.has_key(name):
			return self.jails[name].getFilter().getMaxRetry()
		else:
			raise ServerUnknownJail(name)
	
	def setMaxTime(self, name, value):
		if self.jails.has_key(name):
			self.jails[name].getFilter().setMaxTime(value)
		else:
			raise ServerUnknownJail(name)
	
	def getMaxTime(self, name):
		if self.jails.has_key(name):
			return self.jails[name].getFilter().getMaxTime()
		else:
			raise ServerUnknownJail(name)
	
	# Action
	def addAction(self, name, value):
		if self.jails.has_key(name):
			self.jails[name].getAction().addAction(value)
		else:
			raise ServerUnknownJail(name)
	
	def getLastAction(self, name):
		if self.jails.has_key(name):
			return self.jails[name].getAction().getLastAction()
		else:
			raise ServerUnknownJail(name)
	
	def delAction(self, name, value):
		if self.jails.has_key(name):
			self.jails[name].getAction().delAction(value)
		else:
			raise ServerUnknownJail(name)
	
	def setCInfo(self, name, action, key, value):
		if self.jails.has_key(name):
			self.jails[name].getAction().getAction(action).setCInfo(key, value)
		else:
			raise ServerUnknownJail(name)
	
	def getCInfo(self, name, action, key):
		if self.jails.has_key(name):
			return self.jails[name].getAction().getAction(action).getCInfo(key)
		else:
			raise ServerUnknownJail(name)
	
	def delCInfo(self, name, action, key):
		if self.jails.has_key(name):
			self.jails[name].getAction().getAction(action).delCInfo(key)
		else:
			raise ServerUnknownJail(name)
	
	def setBanTime(self, name, value):
		if self.jails.has_key(name):
			self.jails[name].getAction().setBanTime(value)
		else:
			raise ServerUnknownJail(name)
	
	def getBanTime(self, name):
		if self.jails.has_key(name):
			return self.jails[name].getAction().getBanTime()
		else:
			raise ServerUnknownJail(name)
	
	def setActionStart(self, name, action, value):
		if self.jails.has_key(name):
			self.jails[name].getAction().getAction(action).setActionStart(value)
		else:
			raise ServerUnknownJail(name)
	
	def getActionStart(self, name, action):
		if self.jails.has_key(name):
			return self.jails[name].getAction().getAction(action).getActionStart()
		else:
			raise ServerUnknownJail(name)
		
	def setActionStop(self, name, action, value):
		if self.jails.has_key(name):
			self.jails[name].getAction().getAction(action).setActionStop(value)
		else:
			raise ServerUnknownJail(name)
	
	def getActionStop(self, name, action):
		if self.jails.has_key(name):
			return self.jails[name].getAction().getAction(action).getActionStop()
		else:
			raise ServerUnknownJail(name)
	
	def setActionCheck(self, name, action, value):
		if self.jails.has_key(name):
			self.jails[name].getAction().getAction(action).setActionCheck(value)
		else:
			raise ServerUnknownJail(name)
	
	def getActionCheck(self, name, action):
		if self.jails.has_key(name):
			return self.jails[name].getAction().getAction(action).getActionCheck()
		else:
			raise ServerUnknownJail(name)
	
	def setActionBan(self, name, action, value):
		if self.jails.has_key(name):
			self.jails[name].getAction().getAction(action).setActionBan(value)
		else:
			raise ServerUnknownJail(name)
	
	def getActionBan(self, name, action):
		if self.jails.has_key(name):
			return self.jails[name].getAction().getAction(action).getActionBan()
		else:
			raise ServerUnknownJail(name)
	
	def setActionUnban(self, name, action, value):
		if self.jails.has_key(name):
			self.jails[name].getAction().getAction(action).setActionUnban(value)
		else:
			raise ServerUnknownJail(name)
	
	def getActionUnban(self, name, action):
		if self.jails.has_key(name):
			return self.jails[name].getAction().getAction(action).getActionUnban()
		else:
			raise ServerUnknownJail(name)
		
	# Status
	def status(self):
		jailList = ''
		for jail in self.jails:
			jailList += jail + ', '
		length = len(jailList)
		if not length == 0:
			jailList = jailList[:length-2]
		ret = [("Number of jail", len(self.jails)),
			   ("Jail list", jailList)]
		return ret
	
	def statusJail(self, name):
		if self.jails.has_key(name):
			return self.jails[name].getStatus()
		raise ServerUnknownJail(name)
	
	# Logging
	
	##
	# Set the logging level.
	#
	# Incrementing the value gives more messages.
	# 0 = FATAL
	# 1 = ERROR
	# 2 = WARNING
	# 3 = INFO
	# 4 = DEBUG
	# @param value the level
	
	def setLogLevel(self, value):
		self.logLevel = value
		logLevel = logging.DEBUG
		if value == 0:
			logLevel = logging.FATAL
		elif value == 1:
			logLevel = logging.ERROR
		elif value == 2:
			logLevel = logging.WARNING
		elif value == 3:
			logLevel = logging.INFO
		logging.getLogger("fail2ban").setLevel(logLevel)
	
	##
	# Get the logging level.
	#
	# @see setLogLevel
	# @return the log level
	
	def getLogLevel(self):
		return self.logLevel
	
	def setLogTarget(self, target):
		# Remove previous handler
		logging.getLogger("fail2ban").handlers = []
		self.logTarget = target
		if target == "SYSLOG":
			logSys.error("Not yet implemented")
			return False
		elif target == "STDERR":
			hdlr = logging.StreamHandler(sys.stderr)
		else:
			# Target should be a file
			try:
				open(target, "a")
				hdlr = logging.FileHandler(target)
			except IOError:
				logSys.error("Unable to log to " + target)
				return False
		# set a format which is simpler for console use
		formatter = logging.Formatter('%(name)-16s: %(levelname)-6s %(message)s')
		# tell the handler to use this format
		hdlr.setFormatter(formatter)
		logging.getLogger("fail2ban").addHandler(hdlr)
		return True
	
	def getLogTarget(self):
		return self.logTarget
	
	def createDaemon(self):
		""" Detach a process from the controlling terminal and run it in the
			background as a daemon.
		
			http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/278731
		"""
	
		try:
			# Fork a child process so the parent can exit.  This will return control
			# to the command line or shell.  This is required so that the new process
			# is guaranteed not to be a process group leader.  We have this guarantee
			# because the process GID of the parent is inherited by the child, but
			# the child gets a new PID, making it impossible for its PID to equal its
			# PGID.
			pid = os.fork()
		except OSError, e:
			return((e.errno, e.strerror))	 # ERROR (return a tuple)
		
		if pid == 0:	   # The first child.
	
			# Next we call os.setsid() to become the session leader of this new
			# session.  The process also becomes the process group leader of the
			# new process group.  Since a controlling terminal is associated with a
			# session, and this new session has not yet acquired a controlling
			# terminal our process now has no controlling terminal.  This shouldn't
			# fail, since we're guaranteed that the child is not a process group
			# leader.
			os.setsid()
		
			# When the first child terminates, all processes in the second child
			# are sent a SIGHUP, so it's ignored.
			signal.signal(signal.SIGHUP, signal.SIG_IGN)
		
			try:
				# Fork a second child to prevent zombies.  Since the first child is
				# a session leader without a controlling terminal, it's possible for
				# it to acquire one by opening a terminal in the future.  This second
				# fork guarantees that the child is no longer a session leader, thus
				# preventing the daemon from ever acquiring a controlling terminal.
				pid = os.fork()		# Fork a second child.
			except OSError, e:
				return((e.errno, e.strerror))  # ERROR (return a tuple)
		
			if (pid == 0):	  # The second child.
				# Ensure that the daemon doesn't keep any directory in use.  Failure
				# to do this could make a filesystem unmountable.
				os.chdir("/")
			else:
				os._exit(0)	  # Exit parent (the first child) of the second child.
		else:
			os._exit(0)		 # Exit parent of the first child.
		
		# Close all open files.  Try the system configuration variable, SC_OPEN_MAX,
		# for the maximum number of open files to close.  If it doesn't exist, use
		# the default value (configurable).
		try:
			maxfd = os.sysconf("SC_OPEN_MAX")
		except (AttributeError, ValueError):
			maxfd = 256	   # default maximum
	
		for fd in range(0, maxfd):
			try:
				os.close(fd)
			except OSError:   # ERROR (ignore)
				pass
	
		# Redirect the standard file descriptors to /dev/null.
	   	os.open("/dev/null", os.O_RDONLY)	# standard input (0)
		os.open("/dev/null", os.O_RDWR)		# standard output (1)
		os.open("/dev/null", os.O_RDWR)		# standard error (2)
		return True


class ServerUnknownJail(Exception):
	pass

class ServerInitializationError(Exception):
	pass