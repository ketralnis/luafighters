import luafighters.helloc

luacode = """
x = 0
for i = 1, #foo do
  -- print(i, foo[i])
  x = x + foo[i]
end
-- io.write("lua: Returning data back to C\n");
return x
"""

def main():
    print 'python: executing c'
    ret = luafighters.helloc.say_hello()
    print 'python: got', ret

if __name__ == '__main__':
    main()

