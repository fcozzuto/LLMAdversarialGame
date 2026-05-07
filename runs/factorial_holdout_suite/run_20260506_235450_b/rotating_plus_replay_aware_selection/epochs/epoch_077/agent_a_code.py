def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    legal = []
    for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal or not resources:
        return [0, 0]

    prefer_timing = int(observation.get("turn_index", 0)) % 2

    best_move = None
    best_key = None
    for dx, dy, nx, ny in legal:
        # Evaluate by racing: maximize (opponent_arrival - self_arrival),
        # with a bias to pick a target we can win (self arrives first).
        local_best = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            win_flag = 1 if sd <= od else 0
            # If we can't win, still try to deny by choosing larger od-sd.
            gap = od - sd
            # Small deterministic bias to avoid oscillation
            bias = 0
            if (rx + ry + prefer_timing) % 3 == 0:
                bias = 0.001
            key = (win_flag, gap, -sd, -(rx + ry), bias)
            if local_best is None or key > local_best:
                local_best = key
        if best_key is None or local_best > best_key:
            best_key = local_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]