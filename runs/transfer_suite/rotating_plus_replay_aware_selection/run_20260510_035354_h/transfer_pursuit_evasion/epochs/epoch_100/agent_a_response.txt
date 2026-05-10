def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = str(observation.get("self_role") or "")
    opp_role = str(observation.get("opponent_role") or "")
    s = (self_role + " " + opp_role).lower()
    pursuer = ("pursuer" in self_role.lower()) or ("pursuer" in s and "evader" not in self_role.lower())

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best_mv = (0, 0)
    best_val = -10**18 if pursuer else 10**18

    # Deterministic tie-break: prefer smaller (dx,dy) lexicographically after score.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        ddx, ddy = nx - ox, ny - oy
        dist2 = ddx * ddx + ddy * ddy
        center2 = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)

        # Pursuer: minimize distance; bias toward center a bit to reduce corner-escape zigzags.
        # Evader: maximize distance; also keep moving to avoid getting funneled by edges/obstacles.
        if pursuer:
            val = -dist2 - 0.01 * center2
            if val > best_val + 1e-12 or (abs(val - best_val) <= 1e-12 and (dx, dy) < best_mv):
                best_val = val
                best_mv = (dx, dy)
        else:
            val = dist2 - 0.01 * center2
            if val < best_val - 1e-12 or (abs(val - best_val) <= 1e-12 and (dx, dy) < best_mv):
                best_val = val
                best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]