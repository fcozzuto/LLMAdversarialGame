def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    obstacles = {tuple(p) for p in (observation.get("obstacles") or [])}
    self_set = {tuple(p) for p in (observation.get("self_territory") or [])}
    opp_set = {tuple(p) for p in (observation.get("opponent_territory") or [])}
    un_set = {tuple(p) for p in (observation.get("unclaimed_cells") or [])}

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    op = observation.get("opponent_position") or [w - 1, h - 1]
    ox, oy = op[0], op[1]
    if opp_set:
        sxp = 0
        syp = 0
        n = len(opp_set)
        for x, y in opp_set:
            sxp += x
            syp += y
        ox, oy = sxp / n, syp / n

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def neigh8(x, y):
        c1 = c2 = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        if (nx, ny) in self_set:
                            c1 += 1
                        elif (nx, ny) in opp_set:
                            c2 += 1
        return c1, c2

    def cell_val(x, y):
        v = 0.0
        if (x, y) in self_set:
            v += 1.0
        elif (x, y) in opp_set:
            v += 9.0  # flip opponent-owned on entry
        elif (x, y) in un_set:
            v += 6.0
        else:
            v += 0.2

        own_adj, opp_adj = neigh8(x, y)
        v += 0.9 * own_adj - 1.1 * opp_adj

        # Center pressure: prefer occupying toward the central region
        dc = abs(x - cx) + abs(y - cy)
        v += (16.0 - 2.2 * dc) * 0.1

        # Interception pressure: if opponent controls center, prefer expanding toward their centroid
        dopy = abs(x - ox) + abs(y - oy)
        v += (18.0 - 2.0 * dopy) * 0.08

        # Safety: avoid stepping adjacent only to opponent without nearby own support
        if (x, y) in opp_set and own_adj == 0:
            v -= 2.0

        # Slight move cost to reduce dithering
        v -= 0.15 * (abs(x - sx) + abs(y - sy))

        return v

    best = None
    bestv = -1e18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        v = cell_val(nx, ny)
        if v > bestv:
            bestv = v
            best = (dx, dy)
    return [int(best[0]), int(best[1])]