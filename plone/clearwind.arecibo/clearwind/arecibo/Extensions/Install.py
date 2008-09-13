import transaction
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.DirectoryView import createDirectoryView

EXTENSION_PROFILES = ('clearwind.arecibo:default',)

def uninstall(self):
    def remove(portal, name):
        portal_skins = getToolByName(portal, "portal_skins")
        skins = portal_skins.getSkinSelections()
        for skin in skins:
            path = portal_skins.getSkinPath(skin)
            path = [ p.strip() for p in path.split(',') ]
            try:
                del path[path.index(name)]
                path = ", ".join(path)
                portal_skins.addSkinSelection(skin, path)
            except ValueError:
                pass
    
    remove(self, "arecibo")

def install(self, reinstall=False):
    """ We still have to do this? """
    
    portal_quickinstaller = getToolByName(self, 'portal_quickinstaller')
    portal_setup = getToolByName(self, 'portal_setup')

    def add(portal, name, location):
        portal_skins = getToolByName(portal, "portal_skins")
        if name not in portal_skins.objectIds():
            createDirectoryView(portal_skins, location, name)
    
        skins = portal_skins.getSkinSelections()
        for skin in skins:
            path = portal_skins.getSkinPath(skin)
            path = [ p.strip() for p in path.split(',') ]
            if name not in path:
                if 'custom' in path:
                    pos = path.index('custom') + 1
                else:
                    pos = 0
                path.insert(pos, name)
                path = ", ".join(path)
                portal_skins.addSkinSelection(skin, path)
    
    add(self, "arecibo", "clearwind.arecibo:skins")

    for extension_id in EXTENSION_PROFILES:
        portal_setup.runAllImportStepsFromProfile('profile-%s' % extension_id, purge_old=False)
        product_name = extension_id.split(':')[0]
        portal_quickinstaller.notifyInstalled(product_name)
        transaction.savepoint()