import unittest

from logally.lib import utils


class Model(utils.Sender):
  def __init__(self):
    super(Model, self).__init__()

  def launchModelChanged(self):
    self.signal("modelChanged", "a lot")


class Presenter(object):
  def __init__(self, model=None, view=None):
    super(Presenter, self).__init__()
    self.model = model
    self.view = view
    self.view_changed = False
    model.connect("modelChanged", self.onModelChanged)
    view.connect("viewChanged", self.onViewChanged)

  def onModelChanged(self, how):
    self.view.doModelChanged(how)

  def onViewChanged(self):
    self.view_changed = True


class View(utils.Sender):
  def __init__(self):
    super(View, self).__init__()
    self.model_value = "start"

  def doModelChanged(self, how):
    self.model_value = how
    self.signal("viewChanged")


class SenderTest(unittest.TestCase):
  def setUp(self):
    self.model = Model()
    self.view = View()
    self.presenter = Presenter(model=self.model, view=self.view)

  def testSignal(self):
    self.model.launchModelChanged()
    self.assertEqual(self.view.model_value, "a lot")
    self.assertEqual(self.presenter.view_changed, True)
