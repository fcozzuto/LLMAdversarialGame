def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def clamp_move(nx, ny):
        if not inb(nx, ny): 
            return sx, sy
        if (nx, ny) in obs:
            return sx, sy
        return nx, ny

    self_role = str(observation.get("self_role", "")).lower()
    opponent_role = str(observation.get("opponent_role", "")).lower()
    is_evader = ("evader" in self_role) or ("pursuer" in opponent_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = clamp_move(sx + dx, sy + dy)
        # distance with king-metric
        ddx = nx - ox
        if ddx < 0: ddx = -ddx
        ddy = ny - oy
        if ddy < 0: ddy = -ddy
        dist = ddx + ddy

        # if capture, avoid when evader; seek when pursuer
        if is_evader:
            val = dist
        else:
            val = -dist

        # break ties deterministically with a mild directional bias away/toward center
        cx = w // 2
        cy = h // 2
        dcx = nx - cx
        if dcx < 0: dcx = -dcx
        dcy = ny - cy
        if dcy < 0: dcy = -dcy
        center_pen = dcx + dcy
        val = val - (0.01 * center_pen if is_evader else -0.01 * center_pen)

        # and slight obstacle-avoidance already handled by staying in place; tie-break by lexicographic move
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]