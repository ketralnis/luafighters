-- Strategy: like opportunisticstrategy, find the highest reward per risk planet
-- (size/enemyships) and send everyone there. But this one remembers the current
-- selection between runs until it is conquered to prevent us from oscillating
-- between attacking two enemies

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

            table.insert(enemy_planets, {x=x, y=y,
                                         strategery=cell.planet.size/enemy_ships})
        end
    end
end

if #enemy_planets == 0 then
    -- there's nobody to attack
    return {}
end

if state.best_planet then
    if board.cells[state.best_planet.y][state.best_planet.x].planet.owner == player then
        -- if we already own the planet we've selected, invalidate it
        state.best_planet = nil
    end
end

if not state.best_planet then
    -- figure out which is the most strategic
    table.sort(enemy_planets,
               function(p1, p2)
                   return p1.strategery < p2.strategery
               end)

    state.best_planet = enemy_planets[#enemy_planets]
    log("Selected %d,%d as best option (%f)",
        state.best_planet.x, state.best_planet.y, state.best_planet.strategery)
end


-- now send all of our attack ships to that planet

for y, rows in pairs(board.cells) do
    for x, cell in pairs(rows) do
        my_ships = cell.ships and cell.ships[player] -- may be nil
        if my_ships then
            -- figure out how many ships to send
            if cell.planet and cell.planet.owner == player then
                -- if this is one of my planets, try to keep some reserves
                -- around
                reserve = cell.planet.size*5
                if my_ships > reserve then
                    send_ships = my_ships - reserve
                else
                    send_ships = 0
                end
            else
                -- all other ships are already in transit, continue them on their way
                send_ships = my_ships
            end

            dest_x, dest_y = find_path(x, y, state.best_planet.x, state.best_planet.y)

            log("Sending %d of %d ships from %d,%d to %d,%d via %d,%d",
                send_ships, my_ships,
                x,y,
                state.best_planet.x, state.best_planet.y,
                dest_x,dest_y)

            if send_ships > 0 and not (dest_x == x and dest_y == y) then
                order = {
                    source_x=x, source_y=y,
                    dest_x=dest_x, dest_y=dest_y,
                    shipcount=send_ships,
                }

                table.insert(orders, order)
            end
        end
    end
end

return orders, state, logs
