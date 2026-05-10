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

    self_role = str(observation.get("self_role") or "").lower()
    opponent_role = str(observation.get("opponent_role") or "").lower()
    is_pursuer = ("pursuer" in self_role) or ("pursue" in self_role) or ("hunter" in self_role)
    if "evader" in opponent_role and ("pursuer" in self_role or "pursue" in self_role):
        is_pursuer = True
    if "evader" in self_role:
        is_pursuer = False

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    def clamp_in(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def obstacle_pressure(nx, ny):
        # small penalty for being adjacent to obstacles (evader) / encouragement to cross open lanes (pursuer)
        pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obs:
                    pen += 1
        return pen

    # If pursuer: chase directly but avoid dead squares near obstacles.
    # If evader: maximize distance; prefer farthest corner but avoid moving into obstacle-adjacent cells.
    best_val = None
    best_move = [0, 0]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not clamp_in(nx, ny):
            continue
        d = abs(nx - ox) + abs(ny - oy)
        adj = obstacle_pressure(nx, ny)

        if is_pursuer:
            # minimize distance to opponent; tie-break by fewer obstacle pressures; then stable preference ordering.
            val = (d, adj, abs(dx) + abs(dy), dx, dy)
            if best_val is None or val < best_val:
                best_val = val
                best_move = [dx, dy]
        else:
            # maximize distance from opponent; tie-break by fewer obstacle pressures; then stable ordering.
            # also bias toward the corner farthest from opponent to herd away from pursuer.
            tcx, tcy = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
            corner_dist = abs(nx - tcx) + abs(ny - tcy)
            val = (-d, corner_dist, adj, abs(dx) + abs(dy), dx, dy)
            if best_val is None or val < best_val:
                best_val = val
                best_move = [dx, dy]

    return best_move