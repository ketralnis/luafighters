-- Strategy: total chaos. They can't guess our strategy because even we don't
-- know what it is

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

for x, y, cell in iterate() do
    my_ships = cell.ships and cell.ships[player] -- may be nil
    if my_ships then
        moveships = math.random(0, my_ships)
        dest_x = x+capped_random(x, 1, board.width)
        dest_y = y+capped_random(y, 1, board.height)

        if moveships > 0 and not (x==dest_x and x==dest_y) then
            order(x, y, dest_x, dest_y, moveships)
        end
    end
end
