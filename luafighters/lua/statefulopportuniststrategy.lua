-- Strategy: like opportunisticstrategy, find the highest reward per risk planet
-- (size/enemyships) and send everyone there. But this one remembers the current
-- selection for a few runs until it is conquered to prevent us from oscillating
-- between attacking two enemies

-- build up the list of enemy planets
enemy_planets = {}
for x, y, cell in planets() do
    if cell.planet.owner ~= player then
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

if #enemy_planets == 0 then
    -- there's nobody to attack
    return
end

-- recalculate every 100 turns, or every time we conquer the one we're after
if (board.turn_count%100==0
    or (state.target
        and cell_at(state.target.x, state.target.y).planet.owner == player)) then
    state.target = nil
end

if not state.target then
    -- figure out which is the most strategic
    table.sort(enemy_planets,
               function(p1, p2)
                   return p1.strategery < p2.strategery
               end)

    state.target = enemy_planets[#enemy_planets]
    log("Selected %d,%d as best option (%f)",
        state.target.x, state.target.y, state.target.strategery)
end


-- now send all of our attack ships to that planet

for x, y, cell in iterate() do
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

        dest_x, dest_y = find_path(x,y, state.target.x,state.target.y)

        log("Sending %d of %d ships from %d,%d to %d,%d via %d,%d",
            send_ships, my_ships,
            x,y,
            state.target.x, state.target.y,
            dest_x,dest_y)

        if send_ships > 0 and not (dest_x == x and dest_y == y) then
            order(x,y, dest_x,dest_y, send_ships)
        end
    end
end
