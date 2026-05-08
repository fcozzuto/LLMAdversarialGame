def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)
    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except:
            pass
    self_t = set()
    for p in observation.get("self_territory") or []:
        try:
            self_t.add((int(p[0]), int(p[1])))
        except:
            pass
    opp_t = set()
    for p in observation.get("opponent_territory") or []:
        try:
            opp_t.add((int(p[0]), int(p[1])))
        except:
            pass
    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        try:
            unclaimed.add((int(p[0]), int(p[1])))
        except:
            pass
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    ox, oy = int(ox), int(oy)

    moves = [(-1, 0), (0, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best = None
    best_dxdy = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # base preference: move toward center
        dist_center = abs(nx - cx) + abs(ny - cy)
        value = -0.9 * dist_center

        # territory interaction
        if (nx, ny) in opp_t:
            value += 30.0  # flip/steal priority
        elif (nx, ny) in unclaimed:
            value += 14.0  # expand territory
        elif (nx, ny) in self_t:
            value -= 3.0     # avoid wasting steps

        # deny opponent: prefer cells closer to us than opponent is
        opp_dist = abs(nx - ox) + abs(ny - oy)
        self_dist = abs(nx - sx) + abs(ny - sy)
        value += 0.6 * (opp_dist - self_dist)  # larger means opponent worse off

        # slight tie-break: deterministic scan order already; add stable bias by coordinates
        value += -0.001 * (nx * 17 + ny * 31)

        if best is None or value > best:
            best = value
            best_dxdy = (dx, dy)

    dx, dy = best_dxdy
    if not (-1 <= dx <= 1 and -1 <= dy <= 1):
        return [0, 0]
    return [int(dx), int(dy)]