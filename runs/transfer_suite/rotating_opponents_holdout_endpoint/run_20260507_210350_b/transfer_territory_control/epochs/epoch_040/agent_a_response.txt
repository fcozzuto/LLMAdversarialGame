def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        obstacles.add((int(p[0]), int(p[1])))

    self_terr = set()
    for c in observation.get("self_territory", []) or []:
        self_terr.add((int(c[0]), int(c[1])))

    opp_terr = set()
    for c in observation.get("opponent_territory", []) or []:
        opp_terr.add((int(c[0]), int(c[1])))

    unclaimed = set()
    for c in observation.get("unclaimed_cells", []) or []:
        unclaimed.add((int(c[0]), int(c[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    stay_bias = 0

    best = None
    best_sc = -10**18
    cur_dist = man(sx, sy, ox, oy)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        sc = 0
        if (nx, ny) in self_terr:
            sc += 1
        elif (nx, ny) in opp_terr:
            sc += 12
        elif (nx, ny) in unclaimed:
            sc += 8
        else:
            sc += 3

        nd = man(nx, ny, ox, oy)
        sc += (cur_dist - nd) * 4

        adj_unclaimed = 0
        adj_opp = 0
        for ax, ay in [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
            tx, ty = nx + ax, ny + ay
            if not inb(tx, ty) or (tx, ty) in obstacles:
                continue
            if (tx, ty) in unclaimed:
                adj_unclaimed += 1
            elif (tx, ty) in opp_terr:
                adj_opp += 1
        sc += adj_unclaimed * 1.5 + adj_opp * 2.0

        if dx == 0 and dy == 0:
            sc -= stay_bias

        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]