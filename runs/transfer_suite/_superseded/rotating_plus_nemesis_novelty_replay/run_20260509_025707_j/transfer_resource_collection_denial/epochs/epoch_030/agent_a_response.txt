def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))
    resources = observation.get("resources", []) or []
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Find target resources that are reachable
    rlist = []
    for r in resources:
        if r is not None and len(r) >= 2:
            rx, ry = r[0], r[1]
            if ok(rx, ry):
                rlist.append((rx, ry))
    if not rlist:
        return [0, 0]

    best = None
    bestmove = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # For each move, score by best advantage over opponent on any remaining resource
        best_adv = None
        best_self_d = None
        best_cell = None
        for rx, ry in rlist:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            adv = od - sd  # positive means we are closer than opponent
            if (best_adv is None or adv > best_adv or
                (adv == best_adv and (best_self_d is None or sd < best_self_d)) or
                (adv == best_adv and best_self_d == sd and (rx, ry) < best_cell)):
                best_adv = adv
                best_self_d = sd
                best_cell = (rx, ry)
        # Prefer moves that secure the nearest lead; if tie, prefer smaller self distance.
        # Also slightly prefer moves that reduce distance to the overall closest resource.
        overall_sd = min(md(nx, ny, rx, ry) for rx, ry in rlist)
        # Deterministic tuple ordering (maximize adv, then minimize distances, then dx,dy)
        cand = (-(best_adv), overall_sd, best_self_d, dx, dy, best_cell[0], best_cell[1])
        if best is None or cand < best:
            best = cand
            bestmove = (dx, dy)

    return [int(bestmove[0]), int(bestmove[1])]