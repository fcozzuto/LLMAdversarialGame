def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    srole = (observation.get("self_role") or "").lower()
    orole = (observation.get("opponent_role") or "").lower()
    self_is_evader = ("evader" in srole) or ("evasion" in srole) or ("evader" in orole and "pursuer" in srole)
    self_is_pursuer = not self_is_evader

    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def legal(pos):
        x, y = pos
        out = []
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                out.append((nx, ny, dx, dy))
        return out

    # Predict opponent next step assuming evader-like behavior (max distance from us)
    opp_legal = legal((ox, oy))
    best_opp = (ox, oy)
    best_dist = -1
    for nx, ny, _, _ in opp_legal:
        d2 = (nx - sx) * (nx - sx) + (ny - sy) * (ny - sy)
        if d2 > best_dist:
            best_dist = d2
            best_opp = (nx, ny)
    px, py = best_opp

    # Choose our move
    my_legal = legal((sx, sy))
    best = None
    if self_is_pursuer:
        best_val = 10**18
        for nx, ny, dx, dy in my_legal:
            # Prefer cutting off predicted position; slight bias toward moving closer to opponent directly too.
            d2_pred = (nx - px) * (nx - px) + (ny - py) * (ny - py)
            d2_curr = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            val = d2_pred * 3 + d2_curr
            if val < best_val:
                best_val = val
                best = (dx, dy)
    else:
        best_val = -10**18
        for nx, ny, dx, dy in my_legal:
            # Maximize distance from predicted opponent; wall-run bias; avoid staying in corners only if blocked by obstacles already handled.
            d2_pred = (nx - px) * (nx - px) + (ny - py) * (ny - py)
            boundary_bonus = 2 if (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1) else 0
            val = d2_pred * 3 + boundary_bonus
            if val > best_val:
                best_val = val
                best = (dx, dy)

    return [int(best[0]), int(best[1])] if best is not None else [0, 0]