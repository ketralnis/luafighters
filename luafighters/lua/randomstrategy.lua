orders = {}

function capped_random(x, min, max)
    choices = {0}
    if x-1 >= min then
        table.insert(choices, -1)
    end
    if x+1 <= max then
       table.insert(choices, 1)
    end
    return choices[math.random(#choices)]
end

for y, rows in pairs(board.cells) do
    for x, cell in pairs(rows) do
        ships = cell.ships and cell.ships[player] -- may be nil
        if ships then
            moveships = math.random(0, ships)
            dest_x = capped_random(x, 1, board.width)
            dest_y = capped_random(y, 1, board.height)

            if moveships > 0 and not (dest_x ~= 0 and dest_y ~= 0) then
                order = {source_x=x, source_y=y,
                         shipcount=moveships,
                         dest_x=dest_x+x, dest_y=dest_y+y}
                table.insert(orders, order)
            end
        end
    end
end

return orders