def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources or w <= 0 or h <= 0:
        # fallback: move toward center
        cx, cy = w // 2, h // 2
        dx = 0 if sx == cx else (1 if sx < cx else -1)
        dy = 0 if sy == cy else (1 if sy < cy else -1)
        return [dx, dy]

    self_best = min(resources, key=lambda t: man(sx, sy, t[0], t[1]))
    opp_best = min(resources, key=lambda t: man(ox, oy, t[0], t[1]))

    rem = observation.get("remaining_resource_count", None)
    try:
        rem = int(rem)
    except Exception:
        rem = 999

    d_self = man(sx, sy, self_best[0], self_best[1])
    d_opp_self = man(ox, oy, self_best[0], self_best[1])
    d_opp_t1 = man(ox, oy, opp_best[0], opp_best[1])
    d_self_t1 = man(sx, sy, opp_best[0], opp_best[1])

    # Intercept if opponent is strictly closer to the same key resource and resources are plentiful
    if rem > 6 and d_self_t1 > 0 and (d_opp_t1 + 1) <= d_self_t1:
        target = opp_best
    else:
        target = self_best

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obst:
            continue
        dt = man(nx, ny, target[0], target[1])
        dn = man(nx, ny, self_best[0], self_best[1])
        dp = man(nx, ny, opp_best[0], opp_best[1])
        # Prefer decreasing distance to target; slight bias to not let opponent get too close to their best.
        val = (-dt * 10) + (-dn) + (-dp if target == opp_best else 0)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]