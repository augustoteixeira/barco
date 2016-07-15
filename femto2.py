import serial
import sys
import pprint
import cmd
import time
import urwid

ser = serial.Serial(sys.argv[1], 9600, timeout=1)

pp = pprint.PrettyPrinter(indent=4)

bytesToRead = ser.inWaiting()
try:
    output = ser.read(bytesToRead)
except ValueError:
    print 'Nothing to read at start...'

def question():
    return urwid.Pile([urwid.Edit(('I say', u"Enter command:\n"))])

def answer(name):
    ser.write(name + '\n')
    time.sleep(.4)
    bytesToRead = ser.inWaiting()
    try:
        output = ser.read(bytesToRead)
    except ValueError:
        print 'Did not manage to read output'
    return urwid.Text(('I say', output))

class ConversationListBox(urwid.ListBox):
    def __init__(self):
        body = urwid.SimpleFocusListWalker([question()])
        super(ConversationListBox, self).__init__(body)

    def keypress(self, size, key):
        key = super(ConversationListBox, self).keypress(size, key)
        if key != 'enter':
            return key
        name = self.focus[0].edit_text
        if not name:
            raise urwid.ExitMainLoop()
        # replace or add response
        self.focus.contents[1:] = [(answer(name), self.focus.options())]
        pos = self.focus_position
        # add a new question
        self.body.insert(pos + 1, question())
        self.focus_position = pos + 1

palette = [('I say', 'default,bold', 'default'),]
urwid.MainLoop(ConversationListBox(), palette).run()

ser.close()





