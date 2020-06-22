from __future__ import print_function
from enigma import eConsoleAppContainer
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.ScrollLabel import ScrollLabel

class MQBAction(Screen):
	#TODO move this to skin.xml
	skin = """
		<screen position="0,0" size="1,1" title=" " flags="wfNoBorder">		
                </screen>"""
		
	def __init__(self, session, title = "Console", cmdlist = None, finishedCallback = None, closeOnSuccess = True):
		Screen.__init__(self, session)

		self.finishedCallback = finishedCallback
		self.closeOnSuccess = closeOnSuccess

		self["text"] = ScrollLabel("")
		self["actions"] = ActionMap(["WizardActions", "DirectionActions"], 
		{
			"ok": self.cancel,
			"back": self.cancel,
			"up": self["text"].pageUp,
			"down": self["text"].pageDown
		}, -1)
		
		self.cmdlist = cmdlist
		self.newtitle = title
		
		self.onShown.append(self.updateTitle)
		
		self.container = eConsoleAppContainer()
		self.run = 0
		self.container.appClosed.append(self.runFinished)
		self.container.dataAvail.append(self.dataAvail)
		self.onLayoutFinish.append(self.startRun) # dont start before gui is finished

	def updateTitle(self):
		self.setTitle(self.newtitle)

	def startRun(self):
		self["text"].setText(_("Execution Progress:") + "\n\n")
		print("Console: executing in run", self.run, " the command:", self.cmdlist[self.run])
		if self.container.execute(self.cmdlist[self.run]): #start of container application failed...
			self.runFinished(-1) # so we must call runFinished manual

	def runFinished(self, retval):
		self.run += 1
		if self.run != len(self.cmdlist):
			if self.container.execute(self.cmdlist[self.run]): #start of container application failed...
				self.runFinished(-1) # so we must call runFinished manual
		else:
			lastpage = self["text"].isAtLastPage()
			str = self["text"].getText()
			str += _("Execution finished!!");
			self["text"].setText(str)
			if lastpage:
				self["text"].lastPage()
			if self.finishedCallback is not None:
				self.finishedCallback()
			if not retval and self.closeOnSuccess:
				self.cancel()

	def cancel(self):
		if self.run == len(self.cmdlist):
			self.close()
			self.container.appClosed.remove(self.runFinished)
			self.container.dataAvail.remove(self.dataAvail)

	def dataAvail(self, str):
		lastpage = self["text"].isAtLastPage()
		self["text"].setText(self["text"].getText() + str)
		if lastpage:
			self["text"].lastPage()
