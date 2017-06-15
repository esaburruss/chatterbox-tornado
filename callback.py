def test1():
    print 'Called Back'

def test2(callback):
    print 'Testing....'
    callback()

test2(test1)
