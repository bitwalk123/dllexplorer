import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from module import utils


class DLLExplorer(Gtk.Window):
    dir_target = '/home/bitwalk/test/usr/local/bin'

    def __init__(self):
        Gtk.Window.__init__(self, title='DLL Explorer')
        self.set_default_size(600, 0)

        grid = Gtk.Grid(column_spacing=5)
        self.add(grid)

        lab0 = Gtk.Label(label='app root')
        lab0.set_hexpand(False)
        lab0.set_halign(Gtk.Align.END)

        ent0 = Gtk.Entry()
        ent0.set_hexpand(True)
        ent0.set_editable(False)
        ent0.set_can_focus(False)

        but0 = Gtk.Button()
        but0.add(utils.img().get_image('folder'))
        but0.connect('clicked', self.on_folder_clicked, ent0, self.dir_target)

        lab1 = Gtk.Label(label='pkg root')
        lab1.set_hexpand(False)
        lab1.set_halign(Gtk.Align.END)

        ent1 = Gtk.Entry()
        ent1.set_hexpand(True)
        ent1.set_editable(False)
        ent1.set_can_focus(False)

        but1 = Gtk.Button()
        but1.add(utils.img().get_image('folder'))

        but_start = Gtk.Button(label='START')
        but_start.connect('clicked', self.on_start, self.dir_target)

        grid.attach(lab0, 0, 0, 1, 1)
        grid.attach(ent0, 1, 0, 1, 1)
        grid.attach(but0, 2, 0, 1, 1)
        grid.attach(lab1, 0, 1, 1, 1)
        grid.attach(ent1, 1, 1, 1, 1)
        grid.attach(but1, 2, 1, 1, 1)
        grid.attach(but_start, 0, 2, 3, 1)

    def on_start(self, button, dir):
        print('START')
        obj = utils.RunTime(dir)
        obj.start()

    def on_folder_clicked(self, widget, entry, dir):
        dialog = Gtk.FileChooserDialog(title="Select folder",
                                       parent=self,
                                       action=Gtk.FileChooserAction.SELECT_FOLDER)
        dialog.add_buttons(Gtk.STOCK_CANCEL,
                           Gtk.ResponseType.CANCEL,
                           "Select",
                           Gtk.ResponseType.OK)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print('Select button is selected')
            print('Selected ' + dialog.get_filename())
            entry.set_text(dialog.get_filename())
            dir = dialog.get_filename()
        elif response == Gtk.ResponseType.CANCEL:
            print('Cancel button is selected')

        dialog.destroy()


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
