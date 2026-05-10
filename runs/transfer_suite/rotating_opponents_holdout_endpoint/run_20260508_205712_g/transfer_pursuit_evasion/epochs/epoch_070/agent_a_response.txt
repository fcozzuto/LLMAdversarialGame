def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles") or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    sr = str(observation.get("self_role", "")).lower()
    orr = str(observation.get("opponent_role", "")).lower()
    env = str(observation.get("environment_name", "")).lower()
    self_is_pursuer = ("pursuer" in sr) or ("catch" in sr) or ("pred" in sr) or (env == "pursuit_evasion" and "evader" not in sr and "pursuer" in (orr or ""))
    if env == "pursuit_evasion" and ("evader" in sr):
        self_is_pursuer = False
    if env == "pursuit_evasion" and ("pursuer" in orr):
        self_is_pursuer = True

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def clamp(x, y):
        if x < 0: x = 0
        elif x >= w: x = w - 1
        if y < 0: y = 0
        elif y >= h: y = h - 1
        return x, y

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def min_obst_dist(x, y):
        if not obstacles:
            return 999
        md = 999
        for bx, by in obstacles:
            d = abs(x - bx) + abs(y - by)
            if d < md:
                md = d
        return md

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obstacles:
            continue
        d_opp = man(nx, ny, ox, oy)
        d_obs = min_obst_dist(nx, ny)

        # Deterministic tie-breaker favors diagonal when equal.
        diag = 1 if (dx != 0 and dy != 0) else 0
        # For pursuer: minimize distance to opponent, maximize obstacle clearance.
        # For evader: maximize distance to opponent, maximize obstacle clearance.
        if self_is_pursuer:
            key = (d_opp, -d_obs, -diag, nx, ny)
        else:
            key = (-d_opp, -d_obs, -diag, nx, ny)

        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        # If trapped by obstacles, stay.
        return [0, 0]
    return best