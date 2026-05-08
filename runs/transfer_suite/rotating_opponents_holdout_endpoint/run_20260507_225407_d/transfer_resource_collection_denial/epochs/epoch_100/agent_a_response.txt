def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def kingdist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    opp_dx = ox - sx
    opp_dy = oy - sy
    opp_sgn_y = 0
    if opp_dy > 0:
        opp_sgn_y = 1
    elif opp_dy < 0:
        opp_sgn_y = -1

    best = None
    best_key = None
    for rx, ry in resources:
        d_me = kingdist(sx, sy, rx, ry)
        d_op = kingdist(ox, oy, rx, ry)
        contest = d_op - d_me
        away_from_opp_sweep = -opp_sgn_y * (ry - oy)
        # Prefer mid-ish y when contest is small; discourages predictable denier blocking lines.
        y_prefer = -abs(ry - (h - 1) / 2)
        # Obstacle proximity penalty (cheap): count obstacles in 1-neighborhood.
        neigh = 0
        for nx in (rx - 1, rx, rx + 1):
            for ny in (ry - 1, ry, ry + 1):
                if (nx, ny) in obstacles:
                    neigh += 1
        key = (contest * 1000) + (away_from_opp_sweep * 50) + (y_prefer) - (neigh * 30) - d_me
        if best_key is None or key > best_key or (key == best_key and (rx, ry) < best):
            best_key = key
            best = (rx, ry)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # If direct target step would land on obstacle, try alternatives (deterministic order).
    nx, ny = sx + dx, sy + dy
    if inb(nx, ny) and (nx, ny) not in obstacles:
        return [dx, dy]

    candidates = []
    for adx in (dx, 0, -dx):
        for ady in (dy, 0, -dy):
            if adx == 0 and ady == 0:
                pass
            nx2, ny2 = sx + adx, sy + ady
            if adx in (-1, 0, 1) and ady in (-1, 0, 1) and inb(nx2, ny2) and (nx2, ny2) not in obstacles:
                # choose candidate minimizing king distance to target
                candidates.append(((kingdist(nx2, ny2, tx, ty)), nx2, ny2))
    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda z: (z[0], z[1], z[2]))
    _, nx, ny = candidates[0]
    return [nx - sx, ny - sy]