def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Pick a target resource we can "deny": prefer large (opp_dist - self_dist), then closeness.
    best_t = None
    cx0, cy0 = (w - 1) / 2.0, (h - 1) / 2.0
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        score = (od - sd) * 8 - sd
        center_bias = -(((rx - cx0) ** 2 + (ry - cy0) ** 2) * 1e-4)
        t = (score + center_bias, -od, sd, rx, ry)
        if best_t is None or t > best_t:
            best_t = t
    tx, ty = best_t[3], best_t[4]

    # Greedy step selection with obstacle/out-of-bounds avoidance.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))

    if not moves:
        return [0, 0]

    best_m = None
    for dx, dy, nx, ny in moves:
        sd1 = man(nx, ny, tx, ty)
        sd0 = man(sx, sy, tx, ty)
        od1 = man(ox, oy, tx, ty)
        # Encourage getting closer to target and improving our deny margin vs opponent's reach.
        deny_now = (od1 - sd1)
        progress = sd0 - sd1
        # Slight tie-break to reduce oscillation: prefer moving toward decreasing manhattan to target.
        t = (deny_now * 10 + progress * 2 - sd1, -abs((tx - nx)) - abs((ty - ny)), dx, dy)
        if best_m is None or t > best_m:
            best_m = t
    return [int(best_m[2]), int(best_m[3])]