def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_t = set()
    for p in observation.get("self_territory") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                self_t.add((x, y))

    opp_t = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                opp_t.add((x, y))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                unclaimed.add((x, y))

    def inside(x, y): 
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = -10**18

    def score(nx, ny):
        if (nx, ny) in obstacles or not inside(nx, ny):
            return -10**18
        into_opp = 1 if (nx, ny) in opp_t else 0
        onto_un = 1 if (nx, ny) in unclaimed else 0
        closer_op = - (abs(nx - ox) + abs(ny - oy))
        dist_self = abs(nx - sx) + abs(ny - sy)
        frontier = 0
        if self_t:
            for dx, dy in dirs:
                ax, ay = nx + dx, ny + dy
                if (ax, ay) in self_t:
                    frontier = 1
                    break
        return (into_opp * 10**6) + (onto_un * 10**4) + (closer_op * 10) + (frontier * 5) - dist_self

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        v = score(nx, ny)
        if v > best_val:
            best_val = v
            best = [dx, dy]

    if best is not None:
        return best
    return [0, 0]