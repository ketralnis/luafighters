orders = orders or {}
state = state or {}
logs = logs or {}

-- we should be passed a board, but it may be possible that we aren't if we're
-- called outside of an actual game, like during the tests
board = board or {}

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
    table.insert(logs, '#'..board.turn_count..': '..string.format(...))
end


function cell_at(x, y)
    return board.cells[y][x]
end

-- yields all cells on the board
function iterate()
    return coroutine.wrap(function()
        for y = 1, board.height do
            for x = 1, board.width do
                cell = cell_at(x,y)
                coroutine.yield(x, y, cell)
            end
        end
    end)
end

-- yields all cells containing planets
function planets()
    return coroutine.wrap(function()
        for x, y, cell in iterate() do
            if cell.planet then
                coroutine.yield(x, y, cell)
            end
        end
    end)
end

local function create_order(source_x, source_y, dest_x, dest_y, shipcount)
    return {source_x=source_x, source_y=source_y,
            dest_x=dest_x, dest_y=dest_y,
            shipcount=shipcount}
end


function order(...)
    local o = create_order(...)
    table.insert(orders, o)
end
