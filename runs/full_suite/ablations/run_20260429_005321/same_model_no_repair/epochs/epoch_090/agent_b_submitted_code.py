def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obst_pen(x, y):
        t = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0: 
                    continue
                nx, ny = x + ddx, y + ddy
                if (nx, ny) in obst:
                    t += 2 if abs(ddx) + abs(ddy) == 2 else 1
        return t

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        # Pure defense: maximize distance from opponent while avoiding obstacles and staying in bounds
        best = None
        for dx, dy, nx, ny in legal:
            key = (-cheb(nx, ny, ox, oy), obst_pen(nx, ny), 0 if (dx == 0 and dy == 0) else 1)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]]

    # Choose a target resource where we are relatively closer than the opponent.
    best_res = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer: minimize (our distance - opponent distance), then closer to us, then lower coords
        key = (sd - od, sd, rx, ry)
        if best_res is None or key < best_res[0]:
            best_res = (key, rx, ry)
    _, tx, ty = best_res

    # Move evaluation: decrease our distance to target and increase opponent distance to same target.
    # Extra: if opponent is already closer, bias to blocking (increase their distance more).
    opp_ahead = cheb(ox, oy, tx, ty) < cheb(sx, sy, tx, ty)

    best = None
    for dx, dy, nx, ny in legal:
        ns = cheb(nx, ny, tx, ty)
        no = cheb(nx, ny, tx, ty)  # our position used only for move cost; compute opponent dist from current (next turn assumed)
        # Approx opponent best-response: assume opponent can move toward target; upper bound their next distance by 1-step improvement.
        cur_opp = cheb(ox, oy, tx, ty)
        # If they move optimally, their distance can drop by at most 1 (Chebyshev metric).
        next_opp = cur_opp - 1 if cur_opp > 0 else 0

        # Our score: lower our distance strongly; increase opponent distance relative.
        # Deterministic tie-breakers: obstacle penalty, then prefer non-still if equal.
        if opp_ahead:
            key = (ns, -(next_opp - ns), obst_pen(nx, ny), 0 if (dx != 0 or dy != 0) else 1, tx, ty, dx, dy)
        else:
            key = (ns, -(cur_opp - ns), obst_pen(nx, ny), 0 if (dx != 0 or dy != 0) else 1