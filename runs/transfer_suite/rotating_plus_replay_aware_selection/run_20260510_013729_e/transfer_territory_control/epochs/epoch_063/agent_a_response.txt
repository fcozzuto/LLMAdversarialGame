def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    x, y = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))

    self_t = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            self_t.add((int(p[0]), int(p[1])))

    opp_t = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_t.add((int(p[0]), int(p[1])))

    unq_list = list(unclaimed)
    # If everything seems claimed, bias toward opponent and center.
    target_mode = 1 if unq_list else 0

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_key = None

    def inb(px, py):
        return 0 <= px < w and 0 <= py < h

    def cell_value(px, py):
        if (px, py) in obstacles:
            return -10**9
        if (px, py) in opp_t:
            return 2.5
        if (px, py) in unclaimed:
            return 1.5
        if (px, py) in self_t:
            return 0.5
        return 0.2

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        base = cell_value(nx, ny)

        # Frontier pressure: count advantageous neighbors
        nbrs = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                tx, ty = nx + ddx, ny + ddy
                if not inb(tx, ty):
                    continue
                if (tx, ty) in opp_t or (tx, ty) in unclaimed:
                    nbrs += 1
        # Drive toward/away depending on whether unclaimed exists
        dist_to_op = abs(nx - ox) + abs(ny - oy)
        dist_bias = (-0.1 * dist_to_op) if target_mode else (0.05 * (-dist_to_op))

        # Prefer reducing distance to nearest unclaimed if available
        if target_mode:
            nearest = 10**9
            for cx, cy in unq_list:
                d = abs(nx - cx) + abs(ny - cy)
                if d < nearest:
                    nearest = d
            dist_bias += -0.35 * nearest

        # Tie-breaker: deterministic, prefer diagonal/forward-like ordering via key
        key = (base + 0.3 * nbrs + dist_bias, -dx, -dy)
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]