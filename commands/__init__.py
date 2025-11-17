from .csvExport3D import entry as csvExport3D
from .csvExport2D import entry as csvExport2D
from .folderExport3D import entry as folderExport3D
from .folderExport2D import entry as folderExport2D

commands = [
    csvExport3D,
    csvExport2D,
    folderExport3D,
    folderExport2D
]

def start():
    for command in commands:
        command.start()

def stop():
    for command in commands:
        command.stop()
