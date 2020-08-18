import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from module import utils

class DLLExplorer(Gtk.Window):
    dir_target = '/home/bitwalk/test/usr/local/bin'

    def __init__(self):
        Gtk.Window.__init__(self, title='DLL Explorer')
        self.set_default_size(0, 0)

        but = Gtk.Button(label='START')
        but.connect('clicked', self.on_start, self.dir_target)
        self.add(but)

    def on_start(self, button, dir):
        print('START')
        obj = utils.RunTime(dir)
        obj.start()

# -----------------------------------------------------------------------------
#  MAIN
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    win = DLLExplorer()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
# ---
# PROGRAM END
