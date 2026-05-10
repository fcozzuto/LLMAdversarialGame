def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for it in observation.get("obstacles") or []:
        try:
            if isinstance(it, dict):
                x, y = it.get("x"), it.get("y")
            else:
                x, y = it[0], it[1]
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    def is_free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    self_role = (observation.get("self_role") or "").lower()
    opponent_role = (observation.get("opponent_role") or "").lower()
    pursuit = ("pursuer" in self_role) or ("chaser" in self_role) or ("pursuit" in self_role) or (opponent_role and "evader" in opponent_role and "pursuer" in self_role)

    # Moves: 8-neighborhood + stay, deterministic order
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    dirs.sort(key=lambda t: (abs(t[0]) + abs(t[1]), t[0], t[1]))

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    best = None
    best_val = None

    # Avoid stepping into "dead" corners if possible (small bias)
    corners = {(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)}

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not is_free(nx, ny):
            nx, ny = sx, sy
        d = dist2(nx, ny, ox, oy)
        corner_pen = 1 if (nx, ny) in corners else 0

        # Pursuer: minimize distance; Evader: maximize distance
        if pursuit:
            val = d + 0.25 * corner_pen
            better = (best_val is None) or (val < best_val)
        else:
            val = -d + 0.25 * corner_pen  # maximize d <=> minimize -d
            better = (best_val is None) or (val < best_val)

        if better:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]