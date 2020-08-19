import gi
import os

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from module import utils


class DLLExplorer(Gtk.Window):
    dir_target = '/home/bitwalk/test/usr/local/bin'
    # CSS
    provider = Gtk.CssProvider()
    provider.load_from_path('./dllexplorer.css')

    def __init__(self):
        Gtk.Window.__init__(self, title='DLL Explorer')
        self.set_default_size(800, 600)

        grid = Gtk.Grid(column_spacing=5)
        self.add(grid)

        lab00 = Gtk.Label(label='Application root (source)')
        lab00.set_hexpand(False)
        lab00.set_halign(Gtk.Align.START)
        context = lab00.get_style_context()
        context.add_provider(self.provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        self.ent01 = Gtk.Entry()
        self.ent01.set_hexpand(True)

        but04 = Gtk.Button()
        but04.add(utils.img().get_image('folder'))
        but04.connect('clicked', self.on_get_app_root_dir)

        lab10 = Gtk.Label(label='Package root (destination)')
        lab10.set_hexpand(False)
        lab10.set_halign(Gtk.Align.START)
        context = lab10.get_style_context()
        context.add_provider(self.provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        self.ent11 = Gtk.Entry()
        self.ent11.set_hexpand(True)

        lab12 = Gtk.Label(label='/')
        lab12.set_hexpand(False)

        self.ent13 = Gtk.Entry()
        self.ent13.set_hexpand(False)
        self.ent13.set_width_chars(20)

        but14 = Gtk.Button()
        but14.add(utils.img().get_image('folder'))
        but14.connect('clicked', self.on_get_pkg_root_dir)

        paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        paned.set_vexpand(True)

        but_start = Gtk.Button(label='START')
        but_start.connect('clicked', self.on_start)

        grid.attach(lab00, 0, 0, 1, 1)
        grid.attach(self.ent01, 1, 0, 3, 1)
        grid.attach(but04, 4, 0, 1, 1)
        grid.attach(lab10, 0, 1, 1, 1)
        grid.attach(self.ent11, 1, 1, 1, 1)
        grid.attach(lab12, 2, 1, 1, 1)
        grid.attach(self.ent13, 3, 1, 1, 1)
        grid.attach(but14, 4, 1, 1, 1)
        grid.attach(paned, 0, 2, 5, 1)
        grid.attach(but_start, 0, 3, 5, 1)

        # Trees
        store1 = Gtk.TreeStore.new([str])
        tree1 = Gtk.TreeView(model=store1)


        cell1 = Gtk.CellRendererText()
        column1 = Gtk.TreeViewColumn()
        column1.pack_start(cell1, True)
        column1.add_attribute(cell1, 'text', 0)
        column1.set_title('Application (source)')
        tree1.append_column(column1)

        #root1 = store1.append(None, ['root'])
        #child1 = store1.append(root1, ['child1'])
        #store1.append(root1, ['child2'])
        #store1.append(root1, ['child3'])
        #store1.append(child1, ['gtranchild1'])

        store2 = Gtk.TreeStore.new([str])
        tree2 = Gtk.TreeView(model=store2)

        cell2 = Gtk.CellRendererText()
        column2 = Gtk.TreeViewColumn()
        column2.pack_start(cell2, True)
        column2.add_attribute(cell2, 'text', 0)
        column2.set_title('Package (destination)')
        tree2.append_column(column2)

        #root2 = store2.append(None, ['root'])
        #child2 = store2.append(root2, ['child1'])
        #store2.append(root2, ['child2'])
        #store2.append(root2, ['child3'])
        #store2.append(child2, ['gtranchild1'])

        paned.add1(tree1)
        paned.add2(tree2)

    def on_start(self, button):
        print('START')
        obj = utils.RunTime(self.dir_target)
        obj.start()

    def on_get_app_root_dir(self, widget):
        dir = self.on_get_dir()
        if dir is not None:
            self.ent01.set_text(dir)
            self.ent13.set_text(os.path.basename(dir))

    def on_get_pkg_root_dir(self, widget):
        dir = self.on_get_dir()
        if dir is not None:
            self.ent11.set_text(dir)

    def on_get_dir(self):
        dir = None

        dialog = Gtk.FileChooserDialog(title="Select folder",
                                       parent=self,
                                       action=Gtk.FileChooserAction.SELECT_FOLDER)
        dialog.add_buttons(Gtk.STOCK_CANCEL,
                           Gtk.ResponseType.CANCEL,
                           "Select",
                           Gtk.ResponseType.OK)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            dir = dialog.get_filename()

        dialog.destroy()
        return dir


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
