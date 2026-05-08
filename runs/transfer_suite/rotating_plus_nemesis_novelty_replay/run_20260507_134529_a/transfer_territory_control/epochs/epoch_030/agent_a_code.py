def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (w - 1, h - 1)) or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    unclaimed = to_set("unclaimed_cells")
    opp_terr = to_set("opponent_territory")
    self_terr = to_set("self_territory")

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cell_score(x, y):
        if (x, y) in obstacles:
            return -10**9
        if (x, y) in self_terr:
            base = 4.0
        elif (x, y) in opp_terr:
            base = 2.0
        elif (x, y) in unclaimed:
            base = 3.0
        else:
            base = 1.0
        d_now = abs(sx - ox) + abs(sy - oy)
        d_after = abs(x - ox) + abs(y - oy)
        away = 0.25 * (d_after - d_now)
        return base + away

    best = None
    best_s = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h:
            s = cell_score(nx, ny)
            if s > best_s:
                best_s = s
                best = (dx, dy)
    return [best[0], best[1]] if best is not None else [0, 0]