def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role_s = str(observation.get("self_role", "")).lower()
    i_am_evader = not any(k in role_s for k in ("pursuer", "chaser", "catch", "pursuit"))

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x, y):
        dx = abs(x - ox)
        dy = abs(y - oy)
        return dx if dx >= dy else dy

    def manh(x, y):
        return abs(x - ox) + abs(y - oy)

    # Prefer edges/corners opposite to opponent when evading to disrupt zigzags.
    edge_bias = 0
    if i_am_evader:
        edge_bias = 1
        tx = 0 if ox > (w - 1) / 2 else (w - 1)
        ty = 0 if oy > (h - 1) / 2 else (h - 1)
    else:
        edge_bias = 0
        tx = ox
        ty = oy

    best = None
    best_move = [0, 0]
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            moves.append((dx, dy))
    # Deterministic tie-break: fixed ordering around "stay then clockwise".
    order = [(0, 0), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
    for dx, dy in order:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = cheb(nx, ny)
        m = manh(nx, ny)

        # Obstacle wedge/nearby penalty
        near_pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx2, ty2 = nx + ax, ny + ay
                if (tx2, ty2) in blocked:
                    near_pen += 2 - (abs(ax) + abs(ay) == 2)  # higher for orthogonal adjacency

        # Edge/corner bias for evader; for pursuer head toward opponent.
        edge_score = 0
        if edge_bias:
            edge_score = -(abs(nx - tx) + abs(ny - ty))
        else:
            edge_score = -m

        # Main objective: maximize distance if evader, minimize if pursuer.
        score = (d if i_am_evader else -d) + 0.35 * edge_score - 0.6 * near_pen
        # Small deterministic preference to avoid oscillation: prefer moves that change position toward objective.
        if dx == 0 and dy == 0:
            score -= 0.02 if i_am_evader else 0.01

        if best is None or score > best:
            best = score
            best_move = [dx, dy]

    return best_move