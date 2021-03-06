import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

#
# GraphCutSegmentSelfTest
#

class GraphCutSegmentSelfTest(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "GraphCutSegmentSelfTest" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Testing.TestCases"]
    self.parent.dependencies = []
    self.parent.contributors = ["Danfeng Chen (Western University)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
    This is an example of scripted loadable module bundled in an extension.
    It performs a simple thresholding on the input volume and optionally captures a screenshot.
    """
    self.parent.acknowledgementText = """
    This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
    and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.

#
# GraphCutSegmentSelfTestWidget
#

class GraphCutSegmentSelfTestWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

   

#
# GraphCutSegmentSelfTestLogic
#

class GraphCutSegmentSelfTestLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def hasImageData(self,volumeNode):
    """This is an example logic method that
    returns true if the passed in volume
    node has valid image data
    """
    if not volumeNode:
      logging.debug('hasImageData failed: no volume node')
      return False
    if volumeNode.GetImageData() == None:
      logging.debug('hasImageData failed: no image data in volume node')
      return False
    return True

  def isValidInputOutputData(self, inputVolumeNode, outputVolumeNode):
    """Validates if the output is not the same as input
    """
    if not inputVolumeNode:
      logging.debug('isValidInputOutputData failed: no input volume node defined')
      return False
    if not outputVolumeNode:
      logging.debug('isValidInputOutputData failed: no output volume node defined')
      return False
    if inputVolumeNode.GetID()==outputVolumeNode.GetID():
      logging.debug('isValidInputOutputData failed: input and output volume is the same. Create a new volume for output to avoid this error.')
      return False
    return True

  def takeScreenshot(self,name,description,type=-1):
    # show the message even if not taking a screen shot
    slicer.util.delayDisplay('Take screenshot: '+description+'.\nResult is available in the Annotations module.', 3000)

    lm = slicer.app.layoutManager()
    # switch on the type to get the requested window
    widget = 0
    if type == slicer.qMRMLScreenShotDialog.FullLayout:
      # full layout
      widget = lm.viewport()
    elif type == slicer.qMRMLScreenShotDialog.ThreeD:
      # just the 3D window
      widget = lm.threeDWidget(0).threeDView()
    elif type == slicer.qMRMLScreenShotDialog.Red:
      # red slice window
      widget = lm.sliceWidget("Red")
    elif type == slicer.qMRMLScreenShotDialog.Yellow:
      # yellow slice window
      widget = lm.sliceWidget("Yellow")
    elif type == slicer.qMRMLScreenShotDialog.Green:
      # green slice window
      widget = lm.sliceWidget("Green")
    else:
      # default to using the full window
      widget = slicer.util.mainWindow()
      # reset the type so that the node is set correctly
      type = slicer.qMRMLScreenShotDialog.FullLayout

    # grab and convert to vtk image data
    qpixMap = qt.QPixmap().grabWidget(widget)
    qimage = qpixMap.toImage()
    imageData = vtk.vtkImageData()
    slicer.qMRMLUtils().qImageToVtkImageData(qimage,imageData)

    annotationLogic = slicer.modules.annotations.logic()
    annotationLogic.CreateSnapShot(name, description, type, 1, imageData)

  def run(self, inputVolume, outputVolume, imageThreshold, enableScreenshots=0):
    """
    Run the actual algorithm
    """

    if not self.isValidInputOutputData(inputVolume, outputVolume):
      slicer.util.errorDisplay('Input volume is the same as output volume. Choose a different output volume.')
      return False

    logging.info('Processing started')

    # Compute the thresholded output volume using the Threshold Scalar Volume CLI module
    cliParams = {'InputVolume': inputVolume.GetID(), 'OutputVolume': outputVolume.GetID(), 'ThresholdValue' : imageThreshold, 'ThresholdType' : 'Above'}
    cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True)

    # Capture screenshot
    if enableScreenshots:
      self.takeScreenshot('GraphCutSegmentSelfTestTest-Start','MyScreenshot',-1)

    logging.info('Processing completed')

    return True


class GraphCutSegmentSelfTestTest(ScriptedLoadableModuleLogic):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_GraphCutSegmentSelfTest1()

  def test_GraphCutSegmentSelfTest1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    
    #
    # first, get some data
    #
    # import urllib
	# downloads = (('http://www.slicer.org/slicerWiki/images/5/59/RegLib_C01_1.nrrd', 'Tumor.nrrd', slicer.util.loadVolume),)
	#export http_proxy=http://proxyhost:proxyport

    # for url,name,loader in downloads:
       # filePath = slicer.app.temporaryPath + '/' + name
       # if not os.path.exists(filePath) or os.stat(filePath).st_size == 0:
         # logging.info('Requesting download %s from %s...\n' % (name, url))
         # urllib.urlretrieve(url, filePath)
       # if loader:
         # logging.info('Loading %s...' % (name,))
         # loader(filePath)
    # self.delayDisplay('Finished with download and loading')
	
    self.delayDisplay("Starting the test")
    mainWindow = slicer.util.mainWindow()
    mainWindow.moduleSelector().selectModule('GraphCutInteravtiveSegmenter')
	
    volumeNode = self.downloadMRHead()
#    slicer.util.loadVolume(slicer.app.slicerHome+"/RegLib_C01_1.nrrd")
#   volumeNode = slicer.util.getNode('RegLib_C01_1')
	
    cropVolumeNode = slicer.vtkMRMLCropVolumeParametersNode()
    cropVolumeNode.SetScene(slicer.mrmlScene)
    slicer.mrmlScene.AddNode(cropVolumeNode)
	
    fiducial = slicer.vtkMRMLMarkupsFiducialNode()
    fiducial.SetScene(slicer.mrmlScene)
    fiducial.AddFiducial(-1.8,31.6,11.9)
    fiducial.AddFiducial(15.7,45.0,30.1)
    fiducial.AddFiducial(-18.5,12.0,30.1)
    fiducial.AddFiducial(-2.6,28.7,45.5)
    slicer.mrmlScene.AddNode(fiducial)
	 
    graphCutLogic = slicer.modules.graphcutinteractivesegmenter.logic()
    graphCutLogic.checkMarkups(volumeNode,fiducial)
    graphCutLogic.crop(volumeNode,cropVolumeNode)
		
    graphCutLogic.apply(slicer.mrmlScene.GetNodeByID(cropVolumeNode.GetOutputVolumeNodeID()),True,True)
    self.delayDisplay('Test passed!')
	
  def downloadMRHead(self):
    import SampleData
    sampleDataLogic = SampleData.SampleDataLogic()
    self.delayDisplay('Getting MR Head Volume')
    mrHeadVolume = sampleDataLogic.downloadMRBrainTumor1()
    return mrHeadVolume
