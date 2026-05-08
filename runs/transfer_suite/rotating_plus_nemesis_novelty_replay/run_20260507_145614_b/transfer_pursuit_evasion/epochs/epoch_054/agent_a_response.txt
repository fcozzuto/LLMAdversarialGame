def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    srole = (observation.get("self_role") or "").lower()
    orole = (observation.get("opponent_role") or "").lower()
    # Assume evader role contains "evader" or "evasion"; otherwise we act as pursuer.
    is_evader = ("evader" in srole) or ("evasion" in srole) or (orole and ("pursuer" in srole) and ("evader" in orole) == False and False)

    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    # Deterministic tie-break order with slight turn dependence.
    phase = int(observation.get("turn_index", 0) or 0) & 1
    if phase:
        dirs = dirs[3:] + dirs[:3]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    best_mv = (0, 0)
    best_val = None
    # Secondary preference: for evader, prefer moving toward farthest corner; for pursuer, toward nearest corner.
    corners = [(0,0),(w-1,0),(0,h-1),(w-1,h-1)]
    def corner_score(nx, ny):
        if is_evader:
            return max((nx-cx)*(nx-cx)+(ny-cy)*(ny-cy) for cx, cy in corners)
        else:
            return min((nx-cx)*(nx-cx)+(ny-cy)*(ny-cy) for cx, cy in corners)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dd = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        cs = corner_score(nx, ny)
        # Primary: minimize distance if pursuer, maximize if evader.
        # Ties: also use corner_score for stability/strategic bias.
        if best_val is None:
            best_val = dd, cs
            best_mv = (dx, dy)
        else:
            if is_evader:
                if dd > best_val[0] or (dd == best_val[0] and cs > best_val[1]):
                    best_val = (dd, cs)
                    best_mv = (dx, dy)
            else:
                if dd < best_val[0] or (dd == best_val[0] and cs > best_val[1]):
                    best_val = (dd, cs)
                    best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]