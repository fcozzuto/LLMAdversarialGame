def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    resources = to_set("resources")
    unclaimed = to_set("unclaimed_cells")
    oppT = to_set("opponent_territory")
    selfT = to_set("self_territory")

    inside = lambda x, y: 0 <= x < w and 0 <= y < h
    neigh = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    if oppT:
        ax = sum(x for x, y in oppT) / max(1, len(oppT))
        ay = sum(y for x, y in oppT) / max(1, len(oppT))
    else:
        ax, ay = ox, oy

    def cell_value(nx, ny):
        if (nx, ny) in obstacles:
            return -10**9
        val = 0
        if (nx, ny) in resources:
            val += 120
        if (nx, ny) in unclaimed:
            val += 14
        if (nx, ny) in selfT:
            val += 6
        if (nx, ny) in oppT:
            # flip on entry: strongly prefer stealing cells; extra if near our frontier
            val += 55
            if resources and (nx, ny) in resources:
                val += 20
        # Move pressure: approach opponent territory centroid while avoiding risk of low gain
        dist_cent = abs(nx - ax) + abs(ny - ay)
        val += 10 - dist_cent * 0.6
        # If close to opponent, attempt counter-claim rather than just expand
        dist_op = abs(nx - ox) + abs(ny - oy)
        val += max(0, 8 - dist_op) * 1.5
        return val

    best = (cell_value(sx, sy), 0, 0)
    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        v = cell_value(nx, ny)
        if v > best[0] or (v == best[0] and (dx, dy) < (best[1], best[2])):
            best = (v, dx, dy)
    return [int(best[1]), int(best[2])]