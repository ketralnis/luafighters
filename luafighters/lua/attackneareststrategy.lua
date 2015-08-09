-- Strategy: send every ship to the nearest enemy planet

-- build up the list of enemy planets
enemy_planets = {}
for x, y, cell in board:planets() do
    if cell.planet.owner ~= player then
        table.insert(enemy_planets, {x=x, y=y, cell=cell})
    end
end

if #enemy_planets == 0 then
    return -- nothing to do if we have no enemies
end

for x, y, cell in board:iterate() do
    my_ships = cell.ships and cell.ships[player] -- may be nil
    if my_ships then
        -- find the nearest planet

        table.sort(enemy_planets, function(p1, p2)
                       return distance(x,y,p1.x,p1.y)<distance(x,y,p2.x,p2.y)
                   end)

        nearest = enemy_planets[1]

        if x~=nearest.x or y~=nearest.y then
            dest_x, dest_y = find_path(x, y, nearest.x, nearest.y)

            orders:create(x,y, dest_x,dest_y, my_ships)
        end
    end
end
