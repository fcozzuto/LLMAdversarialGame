def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    role_self = str(observation.get("self_role", "") or "").lower()
    self_is_evader = ("evader" in role_self) or ("runner" in role_self)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def obs_pen(x, y):
        p = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    p += 1
        return p

    # If on obstacle (shouldn't happen), stay safe.
    if (sx, sy) in obstacles:
        return [0, 0]

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = dist2(nx, ny, ox, oy)
        p = obs_pen(nx, ny)

        # Corner pressure: evader prefers central escape; pursuer avoids giving free corners to evader.
        corner_dist2 = (nx - 3.5) * (nx - 3.5) + (ny - 3.5) * (ny - 3.5)
        if self_is_evader:
            score = d - 0.25 * p + 0.08 * corner_dist2
        else:
            score = -d - 0.25 * p + 0.02 * corner_dist2

        if best_score is None or (score > best_score):
            best_score = score
            best = (dx, dy)

    # Deterministic fallback (should rarely trigger)
    if best is None:
        # Prefer staying in-bounds and not on obstacle by simple direction away/toward opponent
        if self_is_evader:
            return [0 if ox == sx else (1 if ox < sx else -1), 0 if oy == sy else (1 if oy < sy else -1)]
        else:
            return [0 if ox == sx else (-1 if ox > sx else 1), 0 if oy == sy else (-1 if oy > sy else 1)]

    return [int(best[0]), int(best[1])]