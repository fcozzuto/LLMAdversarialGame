def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set((int(p[0]), int(p[1])) for p in obstacles if len(p) >= 2)

    resources = observation.get("resources") or []
    res = set((int(p[0]), int(p[1])) for p in resources if len(p) >= 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best = None
    best_val = -10**18

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        val = 0
        d_opp = manh(nx, ny, ox, oy)
        val -= 2 * d_opp
        if res:
            d_res = min(manh(nx, ny, rx, ry) for rx, ry in res)
            val -= d_res
            if (nx, ny) in res:
                val += 100000
        else:
            val -= manh(nx, ny, ox, oy)
        if best is None or val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    if best is None:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]
    return [best[0], best[1]]