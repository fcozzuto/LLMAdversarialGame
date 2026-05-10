def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation["self_position"])
    ox, oy = map(int, observation["opponent_position"])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    role = (str(observation.get("self_role", "")) + " " + str(observation.get("opponent_role", ""))).lower()
    pursuer = ("pursuer" in role) and ("evader" not in role)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs
    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy
    def mobility(x, y):
        c = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                c += 1
        return c

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if pursuer:
        best = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = dist2(nx, ny, ox, oy)
            m = mobility(nx, ny)
            # Break ties by favoring larger mobility, then move that reduces manhattan slightly
            md = abs(nx - ox) + abs(ny - oy)
            score = (d, -m, md)
            if best is None or score < best[0]:
                best = (score, (dx, dy))
        if best is None:
            return [0, 0]
        return [best[1][0], best[1][1]]

    # Evader: prioritize increasing distance, keep options open, and bias toward far corner
    target_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    cx, cy = target_corner
    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        m = mobility(nx, ny)
        # Prefer corner alignment: larger distance to pursuer and farther from corner in case corner is blocked is not needed
        corner_bias = dist2(nx, ny, cx, cy)
        md = abs(nx - ox) + abs(ny - oy)
        score = (-d, -m, -corner_bias, -md)  # minimize negative => maximize these
        if best is None or score < best[0]:
            best = (score, (dx, dy))
    if best is None:
        return [0, 0]
    return [best[1][0], best[1][1]]