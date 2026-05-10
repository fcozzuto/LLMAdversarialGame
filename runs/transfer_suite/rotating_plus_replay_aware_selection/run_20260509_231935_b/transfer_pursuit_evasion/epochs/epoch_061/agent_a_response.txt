def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    i_am_pursuer = ("pursuer" in self_role) or ("evader" not in self_role and "pursuer" not in opp_role)

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def score_pursuer(nx, ny):
        dx, dy = nx - ox, ny - oy
        d2 = dx*dx + dy*dy
        return d2

    def score_evader(nx, ny):
        dx, dy = nx - ox, ny - oy
        d2 = dx*dx + dy*dy
        # keep away from corners a bit to avoid being funneled around obstacles
        corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]
        cb = min(abs(nx-cx)+abs(ny-cy) for cx, cy in corners)
        return -(d2) + 0.05 * cb

    # deterministic tie-break: prefer higher lexicographic stability around a computed bias
    cxm = (w - 1) / 2.0
    cym = (h - 1) / 2.0
    def center_dist(nx, ny):
        return (nx - cxm) * (nx - cxm) + (ny - cym) * (ny - cym)

    best = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        if i_am_pursuer:
            val = (score_pursuer(nx, ny), center_dist(nx, ny), dx, dy)
        else:
            val = (score_evader(nx, ny), -center_dist(nx, ny), -dx, -dy)
        if best is None or val < best:
            best = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]