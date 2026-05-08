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
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    self_evader = ("evad" in self_role) or ("runner" in self_role) or ("evasion" in self_role) or (self_role == "evader")
    opp_evader = ("evad" in opp_role) or ("runner" in opp_role) or ("evasion" in opp_role) or (opp_role == "evader")
    pursue = (not self_evader) or opp_evader

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def corners():
        return [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    # If evading, bias toward the farthest corner; if pursuing, bias toward the closest corner.
    target_corner = None
    cs = corners()
    if pursue:
        bestc = None
        bestd = None
        for cx, cy in cs:
            d = abs(cx - ox) + abs(cy - oy)
            if bestd is None or d < bestd:
                bestd = d
                bestc = (cx, cy)
        target_corner = bestc
    else:
        bestc = None
        bestd = None
        for cx, cy in cs:
            d = abs(cx - ox) + abs(cy - oy)
            if bestd is None or d > bestd:
                bestd = d
                bestc = (cx, cy)
        target_corner = bestc

    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        dist = abs(nx - ox) + abs(ny - oy)
        # Obstacle proximity penalty (try to avoid getting trapped near obstacles).
        prox = 0
        for (ax, ay) in obs:
            md = abs(nx - ax) + abs(ny - ay)
            if md == 0:
                prox += 10
            elif md == 1:
                prox += 3
            elif md == 2:
                prox += 1

        # Corner bias to create consistent trajectories.
        tcx, tcy = target_corner
        corner_dist = abs(nx - tcx) + abs(ny - tcy)

        if pursue:
            val = (-dist, corner_dist, prox, nx, ny)
        else:
            val = (dist, -corner_dist, prox, -nx, -ny)

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]