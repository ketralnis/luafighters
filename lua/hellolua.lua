-- Receives a table, returns the sum of its components.
-- io.write("lua: The table the script received has:\n");

while 1 do
    foo[#foo+1] = 1
end

x = 0
for i = 1, #foo do
  -- print(i, foo[i])
  x = x + foo[i]
end
-- io.write("lua: Returning data back to C\n");
return x
