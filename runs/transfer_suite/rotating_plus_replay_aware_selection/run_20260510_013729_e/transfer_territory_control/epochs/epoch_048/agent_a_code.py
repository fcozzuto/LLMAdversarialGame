def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    xp, yp = int(sp[0]), int(sp[1])
    op = observation.get("opponent_position") or [0, 0]
    xo, yo = int(op[0]), int(op[1])

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) == 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = to_set("obstacles")
    unclaimed = to_set("unclaimed_cells")
    myt = to_set("self_territory")
    opt = to_set("opponent_territory")

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if (0, 0) not in moves:
        moves.append((0, 0))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj_unclaimed(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) in unclaimed:
                    c += 1
        return c

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    opp_dist = abs(xp - xo) + abs(yp - yo)

    best = None
    for dx, dy in moves:
        nx, ny = xp + dx, yp + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = xp, yp
        val = 0.0
        if (nx, ny) in unclaimed:
            val += 70.0
        if (nx, ny) in myt:
            val += 12.0
        if (nx, ny) in opt:
            val -= 55.0
        val += adj_unclaimed(nx, ny) * 6.0
        val -= (abs(nx - xo) + abs(ny - yo)) * 0.6
        val -= (abs(nx - cx) + abs(ny - cy)) * 0.08
        if (nx, ny) == (xp, yp):
            val -= 2.0
        if opp_dist <= 3 and (nx, ny) in opt:
            val -= 20.0

        key = (val, -dx, -dy)  # deterministic tie-break
        if best is None or key > best[0]:
            best = (key, dx, dy)

    return [int(best[1]), int(best[2])]