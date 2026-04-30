def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    cheb = lambda x1, y1, x2, y2: (abs(x1 - x2) if abs(x1 - x2) > abs(y1 - y2) else abs(y1 - y2))
    def near_obst(x, y):
        t = 0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obst:
                t += 1
        return t

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # If no resources, run away while avoiding obstacles; otherwise keep distance from opponent.
    if not resources:
        best = None
        for dx, dy, nx, ny in legal:
            dop = cheb(nx, ny, ox, oy)
            key = (-dop, near_obst(nx, ny), 0 if (dx == 0 and dy == 0) else 1, dx, dy)
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]]

    resset = {(r[0], r[1]) for r in resources}
    best = None
    for dx, dy, nx, ny in legal:
        hit = 1 if (nx, ny) in resset else 0
        dop_now = cheb(nx, ny, ox, oy)
        # Compete for resources: prefer moves where we are closer than opponent (and avoid giving them easy steals).
        best_rel = None
        for rx, ry in resources:
            our_d = cheb(nx, ny, rx, ry)
            op_d = cheb(ox, oy, rx, ry)
            # Lower is better: big reward for being closer than opponent; also keep our absolute distance small.
            rel = our_d - (0.85 * op_d)
            if best_rel is None or rel < best_rel:
                best_rel = rel
        key = (0 if hit else 1, best_rel, -dop_now, near_obst(nx, ny), 0 if (dx == 0 and dy == 0) else 1, dx, dy)
        if best is None or key < best[0]:
            best = (key, (dx, dy))
    return [best[1][0], best[1][1]]