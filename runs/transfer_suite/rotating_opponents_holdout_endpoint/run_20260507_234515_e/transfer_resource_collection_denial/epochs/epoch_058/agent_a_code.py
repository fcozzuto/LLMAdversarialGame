def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    rem = observation.get("remaining_resource_count", 0)

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y):
                res.append((x, y))
    res_set = set(res)

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    # Deterministic preference ordering for ties
    dir_order = {(0, 0): 0, (1, 0): 1, (-1, 0): 2, (0, 1): 3, (0, -1): 4, (1, 1): 5, (-1, 1): 6, (1, -1): 7, (-1, -1): 8}
    # Score move by greedy collection potential and race vs opponent
    best = None
    for dx, dy, nx, ny in cand:
        if (nx, ny) in obs:
            continue
        if (nx, ny) in res_set:
            # Immediate collection: very strong
            score = 10_000 + (rem * 3)
        else:
            # Find best target resource for us from this next position
            best_local = None
            for rx, ry in res:
                d_us = man(nx, ny, rx, ry)
                d_op = man(ox, oy, rx, ry)
                # If opponent is closer, reduce attractiveness
                race_pen = 500 if d_op < d_us else (0 if d_op == d_us else -100)
                # Prefer nearer resources; slightly prefer those with lower opponent distance
                val = (-(d_us * 40) + (d_op * -5) + race_pen)
                if best_local is None or val > best_local:
                    best_local = val
            if best_local is None:
                # No resources visible: drift toward center while avoiding opponent pressure
                cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
                dc = abs(nx - cx) + abs(ny - cy)
                dop = man(nx, ny, ox, oy)
                score = -(dc * 10) - (dop * 2)
            else:
                score = best_local

            # Mildly avoid getting adjacent to opponent unless collecting
            dop_now = man(nx, ny, ox, oy)
            score -= 30 if dop_now <= 1 else 0

        key = (score, -dir_order[(dx, dy)])
        if best is None or key > best[0]:
            best = (key, dx, dy)

    return [best[1], best[2]]