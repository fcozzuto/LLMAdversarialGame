def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs_set = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    self_role = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in self_role) or ("evade" in self_role) or ("escape" in self_role)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if is_evader:
        target_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
        tx, ty = target_corner
        best = None
        best_val = None
        # Prefer moves that get closer to the chosen corner while increasing distance from pursuer
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            d_corner = abs(nx - tx) + abs(ny - ty)
            d_purs = abs(nx - ox) + abs(ny - oy)
            val = (d_purs, -d_corner)  # maximize pursuer distance, then minimize corner distance
            if best is None or val > best_val or (val == best_val and (dx, dy) < best):
                best, best_val = (dx, dy), val
        if best is None:
            return [0, 0]
        return [best[0], best[1]]
    else:
        best = None
        best_val = None
        # Chase: minimize distance to evader, with obstacle-aware "stickiness"
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            d = abs(nx - ox) + abs(ny - oy)
            # Encourage progress over oscillation; slight penalty for staying still unless forced
            stay_pen = 0 if (dx != 0 or dy != 0) else 1
            val = (-d, -stay_pen)  # maximize -distance, then prefer moving
            # Deterministic tie-break: favor [0,0] last, then +x/+y/diagonals via tuple order
            tie = (dx, dy)
            if best is None or val > best_val or (val == best_val and (dx, dy) > best):
                best, best_val = (dx, dy), val
        if best is None:
            return [0, 0]
        return [best[0], best[1]]