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

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    evader = ("evader" in self_role) or ("pursuer" in self_role and "evader" in opp_role)

    candidates = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic tie-break: center-ish then toward increasing x, then increasing y
    candidates.sort(key=lambda d: (0 if d == (0, 0) else 1, -d[0], -d[1]))

    def dist2(x, y):
        dx = x - ox
        dy = y - oy
        return dx * dx + dy * dy

    best = None
    best_score = -10**18 if evader else 10**18

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        d = dist2(nx, ny)
        if evader:
            # Maximize distance; if tied, also prefer staying away from borders a bit
            border_pen = (0 if 1 <= nx <= w - 2 else 2) + (0 if 1 <= ny <= h - 2 else 2)
            score = d - 0.01 * border_pen
            if score > best_score:
                best_score = score
                best = (dx, dy)
        else:
            # Pursuer: minimize distance; if tied, prefer reducing both axes
            axis_pen = abs(nx - ox) + abs(ny - oy)
            score = d + 0.001 * axis_pen
            if score < best_score:
                best_score = score
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]