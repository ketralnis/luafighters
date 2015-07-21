-- save a pointer to globals that would be unreachable in sandbox
local e=_ENV

function make_sandbox()
    -- sample sandbox environment
    sandbox_env = {
        ipairs = ipairs,
        next = next,
        pairs = pairs,
        pcall = pcall,
        tonumber = tonumber,
        tostring = tostring,
        type = type,
        unpack = unpack,
        coroutine = {
            create = coroutine.create, resume = coroutine.resume,
            running = coroutine.running, status = coroutine.status,
            wrap = coroutine.wrap
        },
        string = {
            byte = string.byte, char = string.char, format = string.format,
            len = string.len, lower = string.lower, rep = string.rep,
            reverse = string.reverse, upper = string.upper
        },
        table = {
            insert = table.insert, maxn = table.maxn, remove = table.remove,
            sort = table.sort
        },
        math = {
            abs = math.abs, acos = math.acos, asin = math.asin,
            atan = math.atan, atan2 = math.atan2, ceil = math.ceil, cos = math.cos,
            cosh = math.cosh, deg = math.deg, exp = math.exp, floor = math.floor,
            fmod = math.fmod, frexp = math.frexp, huge = math.huge,
            ldexp = math.ldexp, log = math.log, log10 = math.log10, max = math.max,
            min = math.min, modf = math.modf, pi = math.pi, pow = math.pow,
            rad = math.rad, random = math.random, sin = math.sin, sinh = math.sinh,
            sqrt = math.sqrt, tan = math.tan, tanh = math.tanh
        },
        os = {
            clock = os.clock, difftime = os.difftime, time = os.time
        },
    }

    -- these are blocked for now but bookmarked in case I change my mind
    blocked = {
        string = {
            find = string.find, gmatch = string.gmatch, gsub = string.gsub,
            match = string.match,  sub = string.sub,
        }
    }

    return sandbox_env
end

function run_sandbox(globals, sb_func)
    local sandbox_env = make_sandbox()

    for k,v in pairs(globals) do
        sandbox_env[k] = v
    end

    local chunk = load(sb_func, "userbuff", "t", sandbox_env)
    return chunk()
end

return run_sandbox(env, user_code)
