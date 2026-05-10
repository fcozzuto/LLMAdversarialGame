def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)

    unclaimed = observation.get("unclaimed_cells") or []
    un = [(p[0], p[1]) for p in unclaimed]
    opps = [(ox, oy)]
    has_un = len(un) > 0

    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    best = None
    bestv = None

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        oppd = md(nx, ny, ox, oy)
        if has_un:
            mind = 10**9
            for ux, uy in un:
                d = md(nx, ny, ux, uy)
                if d < mind:
                    mind = d
            v = mind - 0.4 * oppd
        else:
            v = -oppd
        if bestv is None or v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    if best is None:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]
    return [best[0], best[1]]