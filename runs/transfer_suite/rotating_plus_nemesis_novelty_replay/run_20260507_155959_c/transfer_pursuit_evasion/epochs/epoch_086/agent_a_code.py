def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    self_evader = ("evad" in self_role) or ("runner" in self_role) or ("evasion" in self_role) or (self_role == "evader")
    opp_evader = ("evad" in opp_role) or ("runner" in opp_role) or ("evasion" in opp_role) or (opp_role == "evader")
    chase = (not self_evader) or opp_evader  # pursue unless we are clearly evading while opponent is also evading

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def score(nx, ny):
        dx, dy = nx - ox, ny - oy
        d2 = dx * dx + dy * dy
        md = abs(dx) + abs(dy)
        # prefer approaching line-of-sight to opponent and center stability; deterministic tie-breaks
        center_pen = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
        # also avoid staying near obstacles by counting free neighbors
        free = 0
        for a, b in moves:
            tx, ty = nx + a, ny + b
            if ok(tx, ty):
                free += 1
        # chase: minimize distance, maximize free, then minimize md and center_pen
        if chase:
            return (d2, -free, md, center_pen)
        else:
            # evader: maximize distance, then maximize center, then minimize free (deterministic)
            return (-d2, -center_pen, md, -free)

    best_move = [0, 0]
    best_key = None
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not ok(nx, ny):
            continue
        k = score(nx, ny)
        if best_key is None or k < best_key:
            best_key = k
            best_move = [dxm, dym]
    return best_move