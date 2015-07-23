state = state or {}
logs = {}

function find_path(source_x, source_y, dest_x, dest_y)
    -- naive pathfinding. given your location and where you want to go, give the
    -- next square to get there. walks in a diagonal line and then a straight
    -- one
    function closer(source, dest)
        if source == dest then
            return 0
        elseif source > dest then
            return -1
        else
            return 1
        end
    end

    return source_x+closer(source_x, dest_x), source_y+closer(source_y, dest_y)
end

function distance(source_x, source_y, dest_x, dest_y)
    return math.sqrt((source_y-dest_y)^2+(source_x-dest_x)^2)
end

function log(...)
    table.insert(logs, string.format(...))
end
