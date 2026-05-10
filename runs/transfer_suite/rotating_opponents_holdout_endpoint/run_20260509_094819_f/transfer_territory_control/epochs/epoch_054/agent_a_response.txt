def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_set = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_set = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = [tuple(p) for p in (observation.get("unclaimed_cells") or [])]
    resources = [tuple(p) for p in (observation.get("resources") or [])]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        return (dx * dx + dy * dy)

    targets = resources if resources else unclaimed
    if not targets:
        return [0, 0]

    best_t = None
    best_tv = None
    for tx, ty in targets:
        if (tx, ty) in obstacles:
            continue
        tb = dist(sx, sy, tx, ty)
        # Prefer center-ish and far from opponent (to avoid easy flips back)
        cb = (tx - cx) * (tx - cx) + (ty - cy) * (ty - cy)
        ob = dist(ox, oy, tx, ty)
        v = tb * 2.0 + cb * 0.35 + (8.0 / (1.0 + ob)) * 2000.0
        if best_tv is None or v < best_tv:
            best_tv = v
            best_t = (tx, ty)

    tx, ty = best_t
    best_m = (0, 0)
    best_mv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # Score: move closer to target; reward stealing opponent territory; avoid stepping into opponent if we can't steal well
        md = dist(nx, ny, tx, ty)
        steal = 0
        if (nx, ny) in opp_set:
            steal = 1
        stay_cost = 0
        if (nx, ny) in self_set:
            stay_cost = -0.05  # small preference to keep stable control
        steal_bonus = -1200.0 if steal else 0.0
        v = md + steal_bonus + stay_cost
        # Prefer non-stay slightly when tied
        if (best_mv is None) or (v < best_mv - 1e-9) or (abs(v - best_mv) <= 1e-9 and (dx != 0 or dy != 0) and (best_m == (0, 0))):
            best_mv = v
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]