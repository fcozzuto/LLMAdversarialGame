def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or sp
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def to_set(v):
        s = set()
        if not v:
            return s
        for p in v:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    self_ter = to_set(observation.get("self_territory"))
    opp_ter = to_set(observation.get("opponent_territory"))
    unclaimed = to_set(observation.get("unclaimed_cells"))
    obstacles = to_set(observation.get("obstacles"))

    if (sx, sy) in obstacles:
        obstacles.discard((sx, sy))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = None
    best_score = -10**18

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def score_cell(x, y):
        if (x, y) in obstacles:
            return -10**18
        if (x, y) in opp_ter:
            return 1000 - (abs(x - ox) + abs(y - oy))
        if (x, y) in self_ter:
            return 5 - (abs(x - sx) + abs(y - sy))
        if (x, y) in unclaimed:
            border = 0
            for dx, dy in dirs[:-1]:
                nx, ny = x + dx, y + dy
                if (nx, ny) in opp_ter:
                    border += 3
                if (nx, ny) in self_ter:
                    border += 1
            return 200 + border - (abs(x - ox) + abs(y - oy)) // 2
        dist_op = abs(x - ox) + abs(y - oy)
        dist_self = abs(x - sx) + abs(y - sy)
        return 10 - dist_op + (3 - dist_self)

    for dx, dy in dirs:
        x, y = sx + dx, sy + dy
        if not inb(x, y):
            continue
        sc = score_cell(x, y)
        if sc > best_score:
            best_score = sc
            best = [dx, dy]
    return best if best is not None else [0, 0]