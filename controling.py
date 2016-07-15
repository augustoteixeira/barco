import urwid
palette = [
    ('banner', 'black', 'light gray'),
    ('streak', 'dark blue', 'dark red'),
    ('bg', 'black', 'dark blue'),]

se = urwid.ProgressBar('streak', 'bg', current=50)
sd = urwid.ProgressBar('streak', 'bg', current=50)
me = urwid.ProgressBar('streak', 'bg', current=50)
md = urwid.ProgressBar('streak', 'bg', current=50)

button = urwid.Button(u'Exit')
div = urwid.Divider()
pile = urwid.Pile([se, div, sd, div, me, div, md])
top = urwid.Filler(pile, valign='middle')

def on_change(edit, new_edit_text, whoami):
    whoami.set_completion(20)
    bar.set_completion(30)

def on_exit_clicked(button):
    raise urwid.ExitMainLoop()

urwid.connect_signal(se, 'change', on_change, user_arg=se)
urwid.connect_signal(button, 'click', on_exit_clicked)

urwid.MainLoop(top, palette).run()
