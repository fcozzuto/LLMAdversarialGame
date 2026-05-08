def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set(tuple(o) for o in (observation.get("obstacles") or []))
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    ox, oy = int(ox), int(oy)

    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    unclaimed = observation.get("unclaimed_cells") or []

    self_cnt = int(observation.get("self_territory_count", 0) or 0)
    opp_cnt = int(observation.get("opponent_territory_count", 0) or 0)

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    cx, cy = w // 2, h // 2

    attack = self_cnt < opp_cnt
    if attack:
        # target nearest opponent-claimed cell to flip on entry
        if opp_terr:
            tx, ty = min(opp_terr, key=lambda p: man(sx, sy, p[0], p[1]))
        else:
            tx, ty = ox, oy
    else:
        # target unclaimed near center (maximize centrality, minimize distance)
        if unclaimed:
            tx, ty = min(
                ((int(x), int(y)) for x, y in unclaimed),
                key=lambda p: (-(abs(p[0] - cx) + abs(p[1] - cy)), man(sx, sy, p[0], p[1]), p[0], p[1])
            )
        else:
            tx, ty = ox, oy

    best = (0, 0)
    best_s = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        d_t = man(nx, ny, tx, ty)
        d_o = man(nx, ny, ox, oy)
        base = -1.6 * d_t + 0.35 * d_o

        if (nx, ny) in self_terr:
            base += 0.15
        elif (nx, ny) in opp_terr:
            base += 1.25 if attack else 0.6
        else:
            base += 0.55
            if unclaimed:
                if (nx, ny) in set(map(tuple, unclaimed)):
                    base += 0.35
            # slight preference to grab boundary/edge while safe
            if nx in (0, w - 1) or ny in (0, h - 1):
                base += 0.08

        if d_t == 0 and (nx, ny) in opp_terr and attack:
            base += 2.0

        if base > best_s:
            best_s = base
            best = (dx, dy)

    return [int(best[0]), int(best[1])]