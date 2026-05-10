def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "") or "").lower()
    opp_role = str(observation.get("opponent_role", "") or "").lower()
    self_is_pursuer = ("purs" in self_role) or ("purs" in opp_role and "evad" in self_role) or ("pursuer" in self_role)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def step_options():
        opts = []
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                opts.append((dx, dy, nx, ny))
        if not opts:
            return [(0, 0, sx, sy)]
        return opts

    def obs_near_cost(x, y):
        c = 0
        for ex in (-1, 0, 1):
            for ey in (-1, 0, 1):
                if ex == 0 and ey == 0:
                    continue
                if (x + ex, y + ey) in obstacles:
                    c += 1
        return c

    opts = step_options()

    # Deterministic tie-breaker prefers lower-index move from moves list.
    best = None
    best_score = None

    if self_is_pursuer:
        # Chase with slight obstacle and "zigzag" read: try to reduce distance and also align with opponent velocity proxy.
        vx = ox - int(ox + 0)  # no velocity history; keep deterministic baseline
        vy = oy - int(oy + 0)
        for i, (dx, dy, nx, ny) in enumerate((lambda: [(j[0], j[1], j[2], j[3]) for j in opts])( )):
            pass  # unreachable; replaced below

        for i, (dx, dy, nx, ny) in enumerate(opts):
            dist = abs(nx - ox) + abs(ny - oy)
            cost = obs_near_cost(nx, ny)
            score = dist * 10 + cost
            if best_score is None or score < best_score or (score == best_score and i < best):
                best_score = score
                best = i
        dx, dy, _, _ = opts[best]
        return [dx, dy]
    else:
        # Evade: move to maximize distance from pursuer while avoiding obstacles; bias toward opposite corner.
        target = (w - 1, h - 1) if (sx + sy) <= (ox + oy) else (0, 0)
        tx, ty = target
        for i, (dx, dy, nx, ny) in enumerate(opts):
            dist = abs(nx - ox) + abs(ny - oy)
            toward = abs(tx - nx) + abs(ty - ny)
            cost = obs_near_cost(nx, ny)
            # maximize dist, then maximize corner progress (min toward), penalize obstacles near
            score = dist * 100 - toward * 2 - cost * 5
            if best_score is None or score > best_score or (score == best_score and i < best):
                best_score = score
                best = i
        dx, dy, _, _ = opts[best]
        return [dx, dy]