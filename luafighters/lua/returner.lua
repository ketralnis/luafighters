-- they are expected to have mutated these values

-- this may be a rich object, remove the non-array entries
local _orders = {}
for i, order in ipairs(orders) do
    table.insert(_orders, order)
end

return _orders, state, logs