-- Strategy: send every ship to the nearest enemy planet

orders = {}

-- build up the list of enemy planets
enemy_planets = {}
for y, rows in pairs(board.cells) do
    for x, cell in pairs(rows) do
        if cell.planet and cell.planet.owner ~= player then
            enemy_ships = 0

            for shipsowner, ships in pairs(cell.ships or {}) do
                if shipsowner ~= player then
                    enemy_ships = enemy_ships + ships
                end
            end

            table.insert(enemy_planets, {x=x, y=y})
        end
    end
end

if #enemy_planets == 0 then
    return {}
end

for y, rows in pairs(board.cells) do
    for x, cell in pairs(rows) do
        my_ships = cell.ships and cell.ships[player] -- may be nil
        if my_ships then
            -- find the nearest planet

            table.sort(enemy_planets, function(p1, p2)
                           return distance(x,y,p1.x,p1.y)<distance(x,y,p2.x,p2.y)
                       end)

            nearest = enemy_planets[1]

            if x~=nearest.x or y~=nearest.y then
                dest_x, dest_y = find_path(x, y, nearest.x, nearest.y)

                order = {
                    source_x=x, source_y=y,
                    dest_x=dest_x, dest_y=dest_y,
                    shipcount=my_ships,
                }
                table.insert(orders, order)
            end
        end
    end
end

return orders, {}, logs
