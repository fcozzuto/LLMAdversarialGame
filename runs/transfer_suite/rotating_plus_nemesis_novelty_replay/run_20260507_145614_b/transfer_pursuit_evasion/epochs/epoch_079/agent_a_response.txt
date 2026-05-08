def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    self_role = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("purs" in self_role) or ("chaser" in self_role) or ("tag" in self_role)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def min_obst_d2(x, y):
        md = 10**9
        for bx, by in obst:
            d = dist2(x, y, bx, by)
            if d < md:
                md = d
                if md == 0:
                    return 0
        return md if md != 10**9 else 10**9

    # Predict a plausible opponent direction without history: assume opponent moves to improve its objective.
    # If we are pursuer, opponent likely evades; if we are evader, opponent likely pursues.
    target_moves = []
    for odx, ody, nx, ny in candidates:
        # Not used; just keeps deterministic ordering.
        pass

    # Objective score:
    #   pursuer: minimize distance and keep away from obstacles
    #   evader: maximize distance and keep away from obstacles
    best = None
    for dx, dy, nx, ny in candidates:
        d = dist2(nx, ny, ox, oy)

        # Obstacle "risk": closer obstacles are worse.
        md = min_obst_d2(nx, ny)
        risk = md if md < 10**9 else 64*64

        # Small "keep inside" bias to avoid drifting into corners too early as pursuer; opposite for evader.
        edge = min(nx, ny, (w - 1) - nx, (h - 1) - ny)
        edge_bias = edge

        if is_pursuer:
            score = (d * 10.0) + (64.0 - (risk**0.5)) - (edge_bias * 0.02)
        else:
            score = (-d * 10.0) + (64.0 - (risk**0.5)) + (edge_bias * 0.02)

        # Deterministic tie-break: lexicographic on (score, dx, dy)
        key = (score, dx, dy) if best is None else (score, dx, dy)
        if best is None or key < best[0]:
            best = (key, [dx, dy])

    return best[1]