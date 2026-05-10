def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if not resources:
        # Default: drift toward center to reduce worst-case
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    deltas = [(0, 0), (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def nearest_obstacle_dist(x, y):
        # cheap local distance: check neighbors within 2 steps to stay fast/deterministic
        best = 10**9
        for dx in (-2, -1, 0, 1, 2):
            for dy in (-2, -1, 0, 1, 2):
                nx, ny = x + dx, y + dy
                if (nx, ny) in obstacles:
                    d = abs(dx) + abs(dy)
                    if d < best:
                        best = d
        return best if best != 10**9 else 99

    # Choose resource target for strategic pressure
    best_target = None
    best_val = 10**18
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Prefer resources we can likely reach first (smaller sd-od), break ties toward closer to us and center.
        val = (sd - od) * 10 + sd + 0.2 * (man(rx, ry, cx, cy))
        if val < best_val:
            best_val = val
            best_target = (rx, ry)

    # Move by evaluating immediate deltas, aiming to improve relative reach and avoid obstacles
    rx, ry = best_target
    best_move = (0, 0)
    best_move_val = 10**18
    for dx, dy in deltas:
        nx, ny = clamp(sx + dx, 0, w - 1), clamp(sy + dy, 0, h - 1)
        if (nx, ny) in obstacles:
            continue
        sd = man(nx, ny, rx, ry)
        od = man(ox, oy, rx, ry)
        # Avoid getting stuck near obstacles; also nudge toward target even if sd tie.
        obst_pen = max(0, 3 - nearest_obstacle_dist(nx, ny))
        # Secondary: slightly prefer moves that increase distance from opponent (denies sweep patterns)
        opp_dn = man(nx, ny, ox, oy)
        val = (sd - od) * 10 + sd + obst_pen * 2 - 0.05 * opp_dn
        if val < best_move_val:
            best_move_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]