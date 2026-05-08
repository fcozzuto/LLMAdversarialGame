def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role") or "").lower()
    self_is_evader = "evader" in role

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def mobility(x, y):
        m = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if ok(nx, ny):
                m += 1
        return m

    def corner_escape_score(x, y):
        # Prefer staying away from immediate corner traps when evading.
        tx = min(x, w - 1 - x)
        ty = min(y, h - 1 - y)
        return tx + ty  # larger => more central

    best = (0, 0)
    best_val = None

    # If evading, strongly prioritize increasing distance; if pursued, also avoid low-mobility states.
    # If pursuing, strongly prioritize decreasing distance; break ties by higher mobility to avoid obstacle trapping.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dist2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        mob = mobility(nx, ny)
        cen = corner_escape_score(nx, ny)

        if self_is_evader:
            # Maximize distance; penalize low mobility; slightly reward centrality.
            val = dist2 * 4.0 + mob * 2.0 + cen * 0.5
            # Extra deterrent for moving into "near-corner" positions when opponent is near our corner.
            if nx in (0, w - 1) or ny in (0, h - 1):
                val -= (2.5 - cen * 0.5) * (w + h) * 0.05
        else:
            # Minimize distance; penalize low mobility; also avoid moving into corners unless it reduces distance.
            val = -dist2 * 4.0 + mob * 2.0 + cen * 0.2

        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)
        elif val == best_val:
            # Deterministic tie-break: prefer non-still, then lexicographic.
            cand = (dx, dy)
            cur = best
            if cur == (0, 0) and cand != (0, 0):
                best = cand

    if best == (0, 0):
        # Deterministic fallback: if all else equal, move towards/away diagonally if possible.
        tx = 1 if ox > sx else (-1 if ox < sx else 0)
        ty = 1 if oy > sy else (-1 if oy < sy else 0)
        if self_is_evader:
            tx, ty = -tx, -ty
        for dx, dy in [(tx, ty), (tx, 0), (0, ty)]:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [int(dx), int(dy)]

    return [int(best[0]), int(best[1])]