def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role", "") or "").lower()
    pursuer = any(k in role for k in ("pursuer", "hunter", "chaser", "pursuit"))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def clamp(nx, ny):
        if nx < 0: nx = 0
        elif nx >= w: nx = w - 1
        if ny < 0: ny = 0
        elif ny >= h: ny = h - 1
        return nx, ny

    def obs_pen(nx, ny):
        if not obstacles:
            return 0.0
        best = 10**9
        for (x, y) in obstacles:
            d = abs(nx - x) + abs(ny - y)
            if d < best:
                best = d
                if best == 0:
                    break
        if best == 0:
            return 1e6
        if best == 1:
            return 30.0
        if best == 2:
            return 10.0
        return best * 0.15

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)

        # Avoid stepping onto obstacle (in case engine doesn't enforce)
        if (nx, ny) in obstacles:
            continue

        d = abs(nx - ox) + abs(ny - oy)
        # pursuer wants smaller distance; evader wants larger distance
        dist_score = (-d if pursuer else d)

        # Encourage moving away/toward while reducing obstacle proximity risk
        val = dist_score - obs_pen(nx, ny) if pursuer else dist_score - obs_pen(nx, ny)

        # Deterministic tie-break: prefer lexicographically smallest (dx,dy) among equals
        if best is None or (val > best_val if not pursuer else val > best_val):
            best = (dx, dy)
            best_val = val
        elif best is not None and val == best_val:
            if (dx, dy) < best:
                best = (dx, dy)

    if best is None:
        best = (0, 0)
    return [int(best[0]), int(best[1])]