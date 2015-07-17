import luafighters.helloc

def main():
    print 'python: executing c'
    ret = luafighters.helloc.say_hello()
    print 'python: got', ret

if __name__ == '__main__':
    main()

