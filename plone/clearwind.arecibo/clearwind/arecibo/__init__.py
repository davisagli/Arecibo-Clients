from AccessControl import allow_module, allow_class, allow_type
from AccessControl import ModuleSecurityInfo, ClassSecurityInfo
from Products.CMFCore.DirectoryView import registerDirectory

registerDirectory('skins', globals())
ModuleSecurityInfo('clearwind.arecibo.wrapper').declarePublic('arecibo')

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
