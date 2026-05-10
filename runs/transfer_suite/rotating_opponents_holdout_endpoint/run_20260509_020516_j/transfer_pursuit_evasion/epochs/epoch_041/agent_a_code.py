def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for it in observation.get("obstacles") or []:
        if isinstance(it, dict):
            x, y = it.get("x"), it.get("y")
        else:
            x, y = it[0], it[1]
        if x is None or y is None:
            continue
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role)
    is_pursuer = ("pursuer" in role) or ("chaser" in role) or ("catcher" in role)
    if not (is_evader or is_pursuer):
        is_pursuer = True

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def dist(nx, ny):
        return abs(nx - ox) + abs(ny - oy)

    def score_evader(nx, ny):
        # maximize distance; also prefer cornering without being trapped by obstacles
        d = dist(nx, ny)
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        cx, cy = max(corners, key=lambda c: (-(abs(nx - c[0]) + abs(ny - c[1]))))
        corner_bias = -(abs(nx - cx) + abs(ny - cy))
        # "mobility" = number of legal neighboring cells (avoid corners too tight if tie)
        mob = 0
        for dx, dy in moves:
            ax, ay = nx + dx, ny + dy
            if legal(ax, ay):
                mob += 1
        return d * 10 + mob + corner_bias * 0.01

    def score_pursuer(nx, ny):
        # minimize distance; keep diagonal alignment and avoid reducing mobility
        d = dist(nx, ny)
        align = -(abs((nx - sx) - (ny - sy)))  # prefer balanced x/y movement (encourages diagonals)
        mob = 0
        for dx, dy in moves:
            ax, ay = nx + dx, ny + dy
            if legal(ax, ay):
                mob += 1
        return -d * 10 + align * 0.1 + mob * 0.01

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        val = score_evader(nx, ny) if is_evader else score_pursuer(nx, ny)
        if best is None or (val > best_val if is_evader else val > best_val):
            best = (dx, dy)
            best_val = val

    if best is None:
        return [0, 0]
    return [best[0], best[1]]