from psychopy import visual, core

win = visual.Window()
msg = visual.TextStim(win, text = "Hola!!")

msg.draw()
win.flip()
core.wait(2)
win.close()
