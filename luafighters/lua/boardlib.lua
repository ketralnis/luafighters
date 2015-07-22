function find_path(source_x, source_y, dest_x, dest_y)
    -- naive pathfinding. given your location and where you want to go, give the
    -- next square to get there
    function closer(source, dest)
        if source == dest then
            return 0
        elseif source > dest then
            return -1
        else
            return 1
        end
    end

    return source_x+closer(source_x, dest_y), source_y+closer(source_y, dest_y)
end
