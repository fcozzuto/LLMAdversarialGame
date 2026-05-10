def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    self_is_pursuer = ("purs" in self_role) or (("evad" not in self_role) and ("purs" in opp_role) and ("evad" not in opp_role))

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def mob(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                c += 1
        return c

    def dist(x, y, u, v):
        return abs(x - u) + abs(y - v)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if self_is_pursuer:
        target = (ox, oy)
        # keep bias slightly toward central crossing to reduce evasion paths
        center_bias = -1.0
    else:
        # bias toward corner farthest from pursuer
        target = max(corners, key=lambda t: dist(t[0], t[1], ox, oy))
        center_bias = 0.6

    best = None
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = dist(nx, ny, ox, oy)
        if (nx, ny) == (ox, oy) and not self_is_pursuer:
            continue  # suicide if evader
        # primary: chase or evade
        if self_is_pursuer:
            primary = -d
        else:
            primary = d
        # secondary: avoid being boxed in (for both roles)
        m = mob(nx, ny)
        # tertiary: directional bias to target (pursuer intercept, evader escape)
        td = dist(nx, ny, target[0], target[1])
        target_term = -td if self_is_pursuer else td
        # quaternary: slight center preference for pursuer, slight center avoidance for evader
        cb = (abs(nx - cx) + abs(ny - cy))
        center_term = (center_bias * (-cb if self_is_pursuer else cb))  # deterministic sign handling
        # final score with small deterministic tie-breaker
        v = primary * 10.0 + m * 1.7 + target_term * 0.9 + center_term * 0.2 + (dx * 0.01 - dy * 0.005)
        if v > bestv:
            bestv = v
            best = [dx, dy]

    return best if best is not None else [0, 0]