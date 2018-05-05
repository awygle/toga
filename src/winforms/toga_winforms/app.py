import asyncio
import sys

import toga

from .libs import Threading, WinForms, add_handler
from .window import Window


class MainWindow(Window):
    def on_close(self):
        pass

async def _tick_windows(loop, form):
    WinForms.Application.RegisterMessageLoop(WinForms.Application.MessageLoopCallback(loop.is_running))
    form.Visible = True
    while not form.IsDisposed:
        WinForms.Application.DoEvents()
        await asyncio.sleep(0)
    loop.stop()

class App:
    _MAIN_WINDOW_CLASS = MainWindow

    def __init__(self, interface):
        self.interface = interface
        self.interface._impl = self

        self.loop = asyncio.get_event_loop()

        self.create()

    def create(self):
        self.native = WinForms.Application

        self.interface.commands.add(
            toga.Command(None, 'About ' + self.interface.name, group=toga.Group.HELP),
            toga.Command(None, 'Preferences', group=toga.Group.FILE),
            # Quit should always be the last item, in a section on it's own
            toga.Command(lambda s: self.exit(), 'Exit ' + self.interface.name, shortcut='q', group=toga.Group.FILE,
                         section=sys.maxsize),
            toga.Command(None, 'Visit homepage', group=toga.Group.HELP)
        )

        # Call user code to populate the main window
        self.interface.startup()
        self.loop.create_task(_tick_windows(self.loop, self.interface.main_window._impl.native))
        self._menu_items = {}
        self.create_menus()
        self.interface.main_window._impl.native.Icon = \
            self.interface.icon.bind(self.interface.factory).native

    def create_menus(self):
        toga.Group.FILE.order = 0
        # Only create the menu if the menu item index has been created.
        if hasattr(self, '_menu_items'):
            menubar = WinForms.MenuStrip()
            submenu = None
            for cmd in self.interface.commands:
                if cmd == toga.GROUP_BREAK:
                    menubar.Items.Add(submenu)
                    submenu = None
                elif cmd == toga.SECTION_BREAK:
                    submenu.DropDownItems.Add('-')
                else:
                    if submenu is None:
                        submenu = WinForms.ToolStripMenuItem(cmd.group.label)
                    item = WinForms.ToolStripMenuItem(cmd.label)
                    if cmd.action:
                        item.Click += add_handler(cmd)
                    else:
                        item.Enabled = False
                    cmd._widgets.append(item)
                    self._menu_items[item] = cmd
                    submenu.DropDownItems.Add(item)
            if submenu:
                menubar.Items.Add(submenu)
            self.interface.main_window._impl.native.Controls.Add(menubar)
            self.interface.main_window._impl.native.MainMenuStrip = menubar
        self.interface.main_window.content.refresh()

    def open_document(self, fileURL):
        '''Add a new document to this app.'''
        print("STUB: If you want to handle opening documents, implement App.open_document(fileURL)")

    def main_loop(self):
        self.loop.run_forever()

    def exit(self):
        self.loop.close()
