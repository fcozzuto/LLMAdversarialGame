def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def val(x, y):
        if (x, y) in obstacles:
            return -10**9
        base = 0
        if (x, y) in unclaimed:
            base += 200
        if (x, y) in self_t:
            base += 40
        if (x, y) in opp_t:
            base -= 400
        d = abs(x - ox) + abs(y - oy)
        sd = abs(sx - ox) + abs(sy - oy)
        base += 6 * (d - sd)
        if (x, y) == (sx, sy):
            base -= 5
        return base

    best = (0, 0)
    best_v = -10**12
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            v = val(nx, ny)
            if v > best_v:
                best_v = v
                best = [dx, dy]
    if best_v == -10**12:
        for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]
    return best