def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    if w < 1 or h < 1 or len(sp) < 2 or len(op) < 2:
        return [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in observation.get("obstacles") or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    evader = ("evader" in role) or ("runner" in role)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    nearest_corner_to_op = min(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    farthest_corner_from_op = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def clearance(x, y):
        if not obstacles:
            return 99
        md = 10**9
        for ax, ay in obstacles:
            d = abs(x - ax) + abs(y - ay)
            if d < md:
                md = d
        return md if md != 10**9 else 99

    def score_move(nx, ny):
        d_op = abs(nx - ox) + abs(ny - oy)
        clr = clearance(nx, ny)
        # slight bias to avoid obstacles hard, but still deterministic
        if (nx, ny) in obstacles:
            return -10**9 if not evader else -10**9
        if evader:
            # stay away from pursuer and trend toward far corner when it doesn't increase risk too much
            tx, ty = farthest_corner_from_op
            d_corner = abs(nx - tx) + abs(ny - ty)
            return (d_op * 10) + (d_corner * 0.6) + (clr * 0.7)
        else:
            # pursuer: chase opponent; if opponent is corner-evading, head toward their nearest corner to intercept
            tx, ty = nearest_corner_to_op
            d_corner = abs(nx - tx) + abs(ny - ty)
            return (-d_op * 10) + (-d_corner * 0.8) + (clr * 0.2)

    best = None
    best_mv = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        sc = score_move(nx, ny)
        if best is None or sc > best:
            best = sc
            best_mv = [dx, dy]

    return [int(best_mv[0]), int(best_mv[1])]